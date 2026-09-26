import time
import uuid

import httpx
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keys.authentication import ApiKeyAuthentication
from apps.providers.groq import GroqAdapter


class ChatCompletionsView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def post(self, request: Request) -> Response:
        model = request.data["model"]
        messages = request.data["messages"]

        adapter = GroqAdapter(client=httpx.Client(), api_key=settings.GROQ_API_KEY)

        provider_response = adapter.complete(model=model, messages=messages)

        prompt_tokens = provider_response.prompt_tokens
        completion_tokens = provider_response.completion_tokens

        usage = {
            "prompt_tokens": provider_response.prompt_tokens,
            "completion_tokens": provider_response.completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

        message = {"role": "assistant", "content": provider_response.content}

        choice = {
            "index": 0,
            "message": message,
            "finish_reason": provider_response.finish_reason,
        }

        body = {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [choice],
            "usage": usage,
        }

        return Response(body)
