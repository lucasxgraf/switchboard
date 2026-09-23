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

    def complete(self, model: str, messages: list[dict[str, str]]) -> ProviderResponse:
        url = "https://api.groq.com/openai/v1/chat/completions"
        authorization = f"Bearer {self.api_key}"
        body = {"model": model, "messages": messages}

        response = self.client.post(
            url, headers={"Authorization": authorization}, json=body
        )

        if response.status_code == 429:
            raise RateLimitError

        if response.status_code == 500:
            raise ProviderServerError

        data = response.json()

        return ProviderResponse(
            data["choices"][0]["message"]["content"],
            data["usage"]["prompt_tokens"],
            data["usage"]["completion_tokens"],
        )
