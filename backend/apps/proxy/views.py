import time

import httpx
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keys.authentication import ApiKeyAuthentication
from apps.keys.models import RequestLog
from apps.providers.groq import (
    GroqAdapter,
    ProviderAuthenticationError,
    ProviderServerError,
    RateLimitError,
)


class ChatCompletionsView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def post(self, request: Request) -> Response:
        gateway_start = time.perf_counter()

        model = request.data["model"]
        messages = request.data["messages"]

        rate_limit_error_code = "rate_limit_exceeded"

        adapter = GroqAdapter(client=httpx.Client(), api_key=settings.GROQ_API_KEY)

        try:
            provider_start = time.perf_counter()
            provider_response = adapter.complete(model=model, messages=messages)
        except RateLimitError:
            error_body = {
                "error": {
                    "message": "The upstream provider is rate-limiting requests.",
                    "type": "rate_limit_error",
                    "code": rate_limit_error_code,
                }
            }
            gateway_latency_ms = int((time.perf_counter() - gateway_start) * 1000)
            provider_latency_ms = int((time.perf_counter() - provider_start) * 1000)

            request_log = RequestLog.objects.create(
                api_key=request.api_key,
                requested_model=model,
                used_model=model,
                provider="groq",
                prompt_tokens=None,
                completion_tokens=None,
                gateway_latency_ms=gateway_latency_ms,
                provider_latency_ms=provider_latency_ms,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                error_code=rate_limit_error_code,
            )

            return Response(error_body, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except (ProviderServerError, ProviderAuthenticationError) as e:
            error_body = {
                "error": {
                    "message": "The upstream provider returned an error.",
                    "type": "server_error",
                    "code": "server_error",
                }
            }
            gateway_latency_ms = int((time.perf_counter() - gateway_start) * 1000)
            provider_latency_ms = int((time.perf_counter() - provider_start) * 1000)

            request_log = RequestLog.objects.create(
                api_key=request.api_key,
                requested_model=model,
                used_model=model,
                provider="groq",
                prompt_tokens=None,
                completion_tokens=None,
                gateway_latency_ms=gateway_latency_ms,
                provider_latency_ms=provider_latency_ms,
                status_code=status.HTTP_502_BAD_GATEWAY,
                error_code=type(e).__name__,
            )

            return Response(error_body, status=status.HTTP_502_BAD_GATEWAY)

        provider_latency_ms = int((time.perf_counter() - provider_start) * 1000)
        gateway_latency_ms = int((time.perf_counter() - gateway_start) * 1000)

        prompt_tokens = provider_response.prompt_tokens
        completion_tokens = provider_response.completion_tokens

        usage = {
            "prompt_tokens": provider_response.prompt_tokens,
            "completion_tokens": provider_response.completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

        request_log = RequestLog.objects.create(
            api_key=request.api_key,
            requested_model=model,
            used_model=model,
            provider="groq",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            gateway_latency_ms=gateway_latency_ms,
            provider_latency_ms=provider_latency_ms,
            status_code=status.HTTP_200_OK,
        )

        message = {"role": "assistant", "content": provider_response.content}

        choice = {
            "index": 0,
            "message": message,
            "finish_reason": provider_response.finish_reason,
        }

        body = {
            "id": f"chatcmpl-{request_log.request_id.hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [choice],
            "usage": usage,
        }

        return Response(body)
