# ADR-0009: Provider error handling

**Date:** 2026-09-23
**Status:** Accepted

## Decision
- Provider errors are modeled as their own exception types (ProviderError as the base, RateLimitError, ProviderServerError, ProviderAuthenticationError, ProviderTimeoutError, InvalidProviderResponseError as subclasses) instead of a generic exception with a status_code attribute.
- HTTP status codes (401/429/500) are checked right after the request and translated into the matching exception before the response body is touched at all.
- Network timeouts (httpx.TimeoutException) and response shape errors (json.JSONDecodeError, KeyError, IndexError) are each caught in their own, narrowly scoped try/except and chained into the matching exception via raise ... from e, so the original error stays visible in the traceback.

## Context
- M1-05 requires five defined error outcomes (timeout, 429, 500, invalid key, malformed JSON), test-first against httpx.MockTransport.
- M2-08 will later need to decide which errors are retryable (429/500/timeout yes, 401 no). That decision should live with the caller, not inside the adapter.

## Alternatives considered
- A generic ProviderError(status_code: int) — rejected: pushes the meaning of error codes onto every caller, which would then have to check if err.status_code in (429, 500) instead of relying on the type.
- Returning None/an error flag instead of raising — rejected: obscures failures; a Groq response must resolve to either a valid ProviderResponse or a clearly named error.

## Consequences
- M2-08 can write the retry decision as a plain except (RateLimitError, ProviderServerError, ProviderTimeoutError): retry(), without knowing about status codes.
- Every further provider (Gemini, Anthropic, Ollama in M2) must raise these same six exception types — this is the implicit interface that M2-01 will make explicit.
