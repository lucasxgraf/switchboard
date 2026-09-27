import time

import httpx
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keys.authentication import ApiKeyAuthentication
from apps.keys.models import RequestLog
from apps.providers.groq import GroqAdapter


class ChatCompletionsView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def post(self, request: Request) -> Response:
        gateway_start = time.perf_counter()

        model = request.data["model"]
        messages = request.data["messages"]

        adapter = GroqAdapter(client=httpx.Client(), api_key=settings.GROQ_API_KEY)

        provider_start = time.perf_counter()
        provider_response = adapter.complete(model=model, messages=messages)
        provider_latency_ms = int((time.perf_counter() - provider_start) * 1000)

        prompt_tokens = provider_response.prompt_tokens
        completion_tokens = provider_response.completion_tokens

        usage = {
            "prompt_tokens": provider_response.prompt_tokens,
            "completion_tokens": provider_response.completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

        gateway_latency_ms = int((time.perf_counter() - gateway_start) * 1000)

        request_log = RequestLog.objects.create(
            api_key=request.api_key,
            requested_model=model,
            used_model=model,
            provider="groq",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            gateway_latency_ms=gateway_latency_ms,
            provider_latency_ms=provider_latency_ms,
            status_code=200,
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
