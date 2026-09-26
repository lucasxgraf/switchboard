from unittest.mock import patch

import httpx
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.keys.models import ApiKey


class ChatCompletionsTest(TestCase):
    def setUp(self) -> None:
        self.url = "/v1/chat/completions"

        self.client = APIClient()
        self.model = "llama-3.1-8b-instant"
        self.messages = [{"role": "user", "content": "Hi"}]

    def test_missing_api_key_returns_401(self) -> None:
        response = self.client.post(
            self.url, {"model": self.model, "messages": self.messages}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correct_api_key(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")
        groq_body = {
            "choices": [{"message": {"content": "Hi there"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        }

        with patch.object(
            httpx.Client, "post", return_value=httpx.Response(200, json=groq_body)
        ):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["object"], "chat.completion")
        self.assertEqual(data["model"], "llama-3.1-8b-instant")
        self.assertEqual(data["choices"][0]["message"]["role"], "assistant")
        self.assertEqual(data["choices"][0]["message"]["content"], "Hi there")
        self.assertEqual(data["choices"][0]["finish_reason"], "stop")
        self.assertEqual(data["usage"]["prompt_tokens"], 5)
        self.assertEqual(data["usage"]["completion_tokens"], 3)
        self.assertEqual(data["usage"]["total_tokens"], 8)
        self.assertTrue(data["id"].startswith("chatcmpl-"))
        self.assertIsInstance(data["created"], int)
