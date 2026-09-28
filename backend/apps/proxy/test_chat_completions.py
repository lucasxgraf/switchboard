from unittest.mock import patch

import httpx
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.keys.models import ApiKey, RequestLog


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
        prompt_tokens = 5
        completion_tokens = 3
        groq_body = {
            "choices": [{"message": {"content": "Hi there"}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
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
        self.assertEqual(data["usage"]["prompt_tokens"], prompt_tokens)
        self.assertEqual(data["usage"]["completion_tokens"], completion_tokens)
        self.assertEqual(data["usage"]["total_tokens"], 8)
        self.assertTrue(data["id"].startswith("chatcmpl-"))
        self.assertIsInstance(data["created"], int)

    def test_correct_request_log(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")
        prompt_tokens = 5
        completion_tokens = 3
        groq_body = {
            "choices": [{"message": {"content": "Hi there"}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
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

        request_log = RequestLog.objects.get()

        self.assertEqual(request_log.api_key, apikey)
        self.assertEqual(data["id"], f"chatcmpl-{request_log.request_id.hex}")
        self.assertEqual(request_log.requested_model, self.model)
        self.assertEqual(request_log.used_model, self.model)
        self.assertEqual(request_log.status_code, status.HTTP_200_OK)
        self.assertEqual(request_log.provider, "groq")
        self.assertEqual(request_log.prompt_tokens, prompt_tokens)
        self.assertEqual(request_log.completion_tokens, completion_tokens)
        self.assertIsNotNone(request_log.gateway_latency_ms)
        assert request_log.gateway_latency_ms is not None
        self.assertGreaterEqual(request_log.gateway_latency_ms, 0)
        self.assertIsNotNone(request_log.provider_latency_ms)
        assert request_log.provider_latency_ms is not None
        self.assertGreaterEqual(request_log.provider_latency_ms, 0)
        self.assertLessEqual(
            request_log.provider_latency_ms, request_log.gateway_latency_ms
        )
        self.assertIsNone(request_log.cost_micro_cents)
        assert request_log.cost_micro_cents is None
        self.assertEqual(request_log.error_code, "")

    def test_rate_limit_error_returns_429(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(429)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(
            data["error"]["message"], "The upstream provider is rate-limiting requests."
        )
        self.assertEqual(data["error"]["type"], "rate_limit_error")
        self.assertEqual(data["error"]["code"], "rate_limit_exceeded")

    def test_rate_limit_error_request_log(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(429)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        request_log = RequestLog.objects.get()

        self.assertEqual(request_log.api_key, apikey)
        self.assertEqual(request_log.requested_model, self.model)
        self.assertEqual(request_log.used_model, self.model)
        self.assertEqual(request_log.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(request_log.provider, "groq")
        self.assertEqual(request_log.prompt_tokens, None)
        self.assertEqual(request_log.completion_tokens, None)
        self.assertIsNotNone(request_log.gateway_latency_ms)
        assert request_log.gateway_latency_ms is not None
        self.assertGreaterEqual(request_log.gateway_latency_ms, 0)
        self.assertIsNotNone(request_log.provider_latency_ms)
        assert request_log.provider_latency_ms is not None
        self.assertGreaterEqual(request_log.provider_latency_ms, 0)
        self.assertLessEqual(
            request_log.provider_latency_ms, request_log.gateway_latency_ms
        )
        self.assertIsNone(request_log.cost_micro_cents)
        assert request_log.cost_micro_cents is None
        self.assertEqual(request_log.error_code, "rate_limit_exceeded")

    def test_provider_server_error_returns_502(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(500)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            data["error"]["message"],
            "The upstream provider returned an error.",
        )
        self.assertEqual(data["error"]["type"], "server_error")
        self.assertEqual(data["error"]["code"], "server_error")

    def test_provider_server_error_request_log(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(500)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)

        request_log = RequestLog.objects.get()

        self.assertEqual(request_log.api_key, apikey)
        self.assertEqual(request_log.requested_model, self.model)
        self.assertEqual(request_log.used_model, self.model)
        self.assertEqual(request_log.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(request_log.provider, "groq")
        self.assertEqual(request_log.prompt_tokens, None)
        self.assertEqual(request_log.completion_tokens, None)
        self.assertIsNotNone(request_log.gateway_latency_ms)
        assert request_log.gateway_latency_ms is not None
        self.assertGreaterEqual(request_log.gateway_latency_ms, 0)
        self.assertIsNotNone(request_log.provider_latency_ms)
        assert request_log.provider_latency_ms is not None
        self.assertGreaterEqual(request_log.provider_latency_ms, 0)
        self.assertLessEqual(
            request_log.provider_latency_ms, request_log.gateway_latency_ms
        )
        self.assertIsNone(request_log.cost_micro_cents)
        assert request_log.cost_micro_cents is None
        self.assertEqual(request_log.error_code, "ProviderServerError")

    def test_provider_authentication_error_returns_502(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(401)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            data["error"]["message"],
            "The upstream provider returned an error.",
        )
        self.assertEqual(data["error"]["type"], "server_error")
        self.assertEqual(data["error"]["code"], "server_error")

    def test_provider_authentication_error_request_log(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(401)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)

        request_log = RequestLog.objects.get()

        self.assertEqual(request_log.api_key, apikey)
        self.assertEqual(request_log.requested_model, self.model)
        self.assertEqual(request_log.used_model, self.model)
        self.assertEqual(request_log.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(request_log.provider, "groq")
        self.assertEqual(request_log.prompt_tokens, None)
        self.assertEqual(request_log.completion_tokens, None)
        self.assertIsNotNone(request_log.gateway_latency_ms)
        assert request_log.gateway_latency_ms is not None
        self.assertGreaterEqual(request_log.gateway_latency_ms, 0)
        self.assertIsNotNone(request_log.provider_latency_ms)
        assert request_log.provider_latency_ms is not None
        self.assertGreaterEqual(request_log.provider_latency_ms, 0)
        self.assertLessEqual(
            request_log.provider_latency_ms, request_log.gateway_latency_ms
        )
        self.assertIsNone(request_log.cost_micro_cents)
        assert request_log.cost_micro_cents is None
        self.assertEqual(request_log.error_code, "ProviderAuthenticationError")

    def test_provider_timeout_error_returns_504(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(
            httpx.Client, "post", side_effect=httpx.TimeoutException("timed out")
        ):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(
            data["error"]["message"],
            "The upstream provider took too long to respond.",
        )
        self.assertEqual(data["error"]["type"], "timeout_error")
        self.assertEqual(data["error"]["code"], "timeout_error")

    def test_provider_timeout_error_request_log(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(
            httpx.Client, "post", side_effect=httpx.TimeoutException("timed out")
        ):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)

        request_log = RequestLog.objects.get()

        self.assertEqual(request_log.api_key, apikey)
        self.assertEqual(request_log.requested_model, self.model)
        self.assertEqual(request_log.used_model, self.model)
        self.assertEqual(request_log.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(request_log.provider, "groq")
        self.assertEqual(request_log.prompt_tokens, None)
        self.assertEqual(request_log.completion_tokens, None)
        self.assertIsNotNone(request_log.gateway_latency_ms)
        assert request_log.gateway_latency_ms is not None
        self.assertGreaterEqual(request_log.gateway_latency_ms, 0)
        self.assertIsNotNone(request_log.provider_latency_ms)
        assert request_log.provider_latency_ms is not None
        self.assertGreaterEqual(request_log.provider_latency_ms, 0)
        self.assertLessEqual(
            request_log.provider_latency_ms, request_log.gateway_latency_ms
        )
        self.assertIsNone(request_log.cost_micro_cents)
        assert request_log.cost_micro_cents is None
        self.assertEqual(request_log.error_code, "timeout_error")

    def test_invalid_provider_response_error_returns_502(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(200)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            data["error"]["message"],
            "The upstream provider returned an error.",
        )
        self.assertEqual(data["error"]["type"], "server_error")
        self.assertEqual(data["error"]["code"], "server_error")

    def test_invalid_provider_response_error_request_log(self) -> None:
        apikey = ApiKey.generate_key(name="testapikey")

        with patch.object(httpx.Client, "post", return_value=httpx.Response(200)):
            response = self.client.post(
                self.url,
                {"model": self.model, "messages": self.messages},
                format="json",
                HTTP_AUTHORIZATION=f"Bearer {apikey.raw_key}",
            )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)

        request_log = RequestLog.objects.get()

        self.assertEqual(request_log.api_key, apikey)
        self.assertEqual(request_log.requested_model, self.model)
        self.assertEqual(request_log.used_model, self.model)
        self.assertEqual(request_log.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(request_log.provider, "groq")
        self.assertEqual(request_log.prompt_tokens, None)
        self.assertEqual(request_log.completion_tokens, None)
        self.assertIsNotNone(request_log.gateway_latency_ms)
        assert request_log.gateway_latency_ms is not None
        self.assertGreaterEqual(request_log.gateway_latency_ms, 0)
        self.assertIsNotNone(request_log.provider_latency_ms)
        assert request_log.provider_latency_ms is not None
        self.assertGreaterEqual(request_log.provider_latency_ms, 0)
        self.assertLessEqual(
            request_log.provider_latency_ms, request_log.gateway_latency_ms
        )
        self.assertIsNone(request_log.cost_micro_cents)
        assert request_log.cost_micro_cents is None
        self.assertEqual(request_log.error_code, "InvalidProviderResponseError")
