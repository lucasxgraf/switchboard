import httpx
from django.test import TestCase

from .groq import GroqAdapter


class GroqAdapterTest(TestCase):
    def test_complete(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "Hi there"}}],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 3},
                },
            )

        client = httpx.Client(transport=httpx.MockTransport(handler))

        adapter = GroqAdapter(client=client, api_key="test-key")

        response = adapter.complete(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hi"}],
        )

        self.assertEqual(response.content, "Hi there")
        self.assertEqual(response.prompt_tokens, 5)
        self.assertEqual(response.completion_tokens, 3)
