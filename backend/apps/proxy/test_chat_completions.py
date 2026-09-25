from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


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
