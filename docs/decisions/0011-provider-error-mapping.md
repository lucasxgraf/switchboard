# ADR-0011: Provider error mapping

**Date:** 2026-09-27
**Status:** Accepted

## Decision
- Provider exceptions (`apps.providers.groq`, see ADR-0009) are mapped in the view, via an `except` chain, to fixed HTTP status codes for the client: `RateLimitError` → 429, `ProviderServerError` → 502, `ProviderAuthenticationError` → 502, `ProviderTimeoutError` → 504, `InvalidProviderResponseError` → 502.
- The error body follows OpenAI's envelope format (`{"error": {"message", "type", "code"}}`), using OpenAI's own `type`/`code` vocabulary, but with generic messages authored by Switchboard itself — Groq's raw error text is never passed through.
- `RequestLog.error_code` mirrors the same value as `error.code` in the body (one source of truth, one literal, no duplication).

## Addition to decision — 2026-09-27
- `ProviderServerError` and `ProviderAuthenticationError` are handled in one shared `except` branch and get an identical status code (502) and identical error envelope (`type`/`code` = `"server_error"`) for the client — the client should not be able to tell whether Groq itself is down or Switchboard's own Groq key is broken, to avoid leaking internal details.
- Internally (`RequestLog.error_code`), the two cases are deliberately distinguished, via `type(e).__name__` (`"ProviderServerError"` or `"ProviderAuthenticationError"`).

## Addition to decision — 2026-09-28
- `InvalidProviderResponseError` joins the same shared `except` branch as `ProviderServerError`/`ProviderAuthenticationError` (identical 502 envelope, `error_code` distinguished internally via `type(e).__name__`). It fits particularly well: 502's actual definition is "gateway received an invalid response from the upstream," which is exactly this case (Groq returns 200 but the body is malformed or missing expected fields).

## Context
- M1-06 Test 4 requires a defined status code on a provider error, plus a log entry.
- The client authenticates against Switchboard, not against Groq — passing Groq's own status codes through 1:1 (especially 401) would falsely signal to the client that its own Switchboard key is invalid, when the actual problem is Switchboard's Groq key.

## Alternatives considered
- Passing provider status codes through 1:1 — rejected, see above (auth misinterpretation).
- A dict lookup (`{ExceptionType: status_code}`) instead of an `except` chain — rejected because at least one branch (`RateLimitError`) will foreseeably need more than just a status code (e.g. a `Retry-After` header, once M2's own rate limiting arrives, see `docs/plan.md` line 207/588). A chain scales naturally for that; a dict would need special-casing anyway.
- Passing through Groq's raw error text — rejected. The adapter exists precisely to hide provider specifics; every further provider (M2: Gemini, Anthropic/OpenAI, Ollama) would have its own error schema, requiring a parser per provider just to fill one text field, without the client needing that value (`error.type`/`error.code` already suffice for distinguishing cases).
- A custom error vocabulary instead of OpenAI's — rejected, because compatibility with real OpenAI client libraries (which evaluate `error.type`/`error.message` to construct exceptions) is the actual purpose of the gateway.

## Addition to alternatives considered — 2026-09-27
- Unifying `RequestLog.error_code` too (identical to `error.code` in the body, as with `RateLimitError`) — rejected. Unlike the rate-limit case, there's a real reason for different values here: the operational response differs (wait out Groq vs. rotate Switchboard's own key immediately), and Sentry isn't wired up yet (not until M1-09) — `RequestLog` is currently the only durable place that captures this distinction.

## Consequences
- All five error paths are implemented (2026-09-28) and follow this pattern; no further ADR needed unless a genuinely new trade-off comes up.
- Currently duplicated code (latency measurement + `RequestLog.create`, once per `except` branch) is now due for the refactor already flagged when this ADR was written — all five paths exist.
- Once M2's own rate limiting arrives, there will be two distinct sources of a 429 (Groq's limit vs. Switchboard's own) — these must be kept clearly apart, among other things around the `Retry-After` header, which only makes sense for Switchboard's own limit.

## Addition to consequences — 2026-09-27
- Since `RequestLog.error_code` and the body's `error.code` deliberately diverge for `ProviderServerError`/`ProviderAuthenticationError`, this must be accounted for in future evaluations (dashboards, alerts) — a simple comparison of the two fields no longer works here.
