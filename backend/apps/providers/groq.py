import json
from dataclasses import dataclass

import httpx


@dataclass
class ProviderResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int


class ProviderError(Exception):
    pass


class RateLimitError(ProviderError):
    pass


class ProviderServerError(ProviderError):
    pass


class ProviderAuthenticationError(ProviderError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class InvalidProviderResponseError(ProviderError):
    pass


class GroqAdapter:
    def __init__(self, client: httpx.Client, api_key: str) -> None:
        self.client = client
        self.api_key = api_key

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise ProviderAuthenticationError

        if response.status_code == 429:
            raise RateLimitError

        if response.status_code == 500:
            raise ProviderServerError

    def _parse_response(self, response: httpx.Response) -> ProviderResponse:
        try:
            data = response.json()

            return ProviderResponse(
                data["choices"][0]["message"]["content"],
                data["usage"]["prompt_tokens"],
                data["usage"]["completion_tokens"],
            )
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise InvalidProviderResponseError from e

    def complete(self, model: str, messages: list[dict[str, str]]) -> ProviderResponse:
        url = "https://api.groq.com/openai/v1/chat/completions"
        authorization = f"Bearer {self.api_key}"
        body = {"model": model, "messages": messages}

        try:
            response = self.client.post(
                url, headers={"Authorization": authorization}, json=body
            )
        except httpx.TimeoutException as e:
            raise ProviderTimeoutError from e

        self._raise_for_status(response)
        return self._parse_response(response)
