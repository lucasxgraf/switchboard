# ADR-0011: Provider error mapping

**Date:** 2026-09-27
**Status:** Accepted

## Decision
- Provider exceptions (`apps.providers.groq`, see ADR-0009) are mapped in the view, via an `except` chain, to fixed HTTP status codes for the client: `RateLimitError` → 429, `ProviderServerError` → 502, `ProviderAuthenticationError` → 502, `ProviderTimeoutError` → 504, `InvalidProviderResponseError` → 502.
- The error body follows OpenAI's envelope format (`{"error": {"message", "type", "code"}}`), using OpenAI's own `type`/`code` vocabulary, but with generic messages authored by Switchboard itself — Groq's raw error text is never passed through.
- `RequestLog.error_code` mirrors the same value as `error.code` in the body (one source of truth, one literal, no duplication).

## Context
- M1-06 Test 4 requires a defined status code on a provider error, plus a log entry.
- The client authenticates against Switchboard, not against Groq — passing Groq's own status codes through 1:1 (especially 401) would falsely signal to the client that its own Switchboard key is invalid, when the actual problem is Switchboard's Groq key.

## Alternatives considered
- Passing provider status codes through 1:1 — rejected, see above (auth misinterpretation).
- A dict lookup (`{ExceptionType: status_code}`) instead of an `except` chain — rejected because at least one branch (`RateLimitError`) will foreseeably need more than just a status code (e.g. a `Retry-After` header, once M2's own rate limiting arrives, see `docs/plan.md` line 207/588). A chain scales naturally for that; a dict would need special-casing anyway.
- Passing through Groq's raw error text — rejected. The adapter exists precisely to hide provider specifics; every further provider (M2: Gemini, Anthropic/OpenAI, Ollama) would have its own error schema, requiring a parser per provider just to fill one text field, without the client needing that value (`error.type`/`error.code` already suffice for distinguishing cases).
- A custom error vocabulary instead of OpenAI's — rejected, because compatibility with real OpenAI client libraries (which evaluate `error.type`/`error.message` to construct exceptions) is the actual purpose of the gateway.

## Consequences
- The remaining four error paths follow the same pattern; no further ADR needed unless a genuinely new trade-off comes up.
- Currently duplicated code (latency measurement + `RequestLog.create`, once per `except` branch) will be refactored once all five paths exist.
- Once M2's own rate limiting arrives, there will be two distinct sources of a 429 (Groq's limit vs. Switchboard's own) — these must be kept clearly apart, among other things around the `Retry-After` header, which only makes sense for Switchboard's own limit.
