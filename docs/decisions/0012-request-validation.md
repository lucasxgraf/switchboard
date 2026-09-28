# ADR-0012: Request validation

**Date:** 2026-09-28
**Status:** Accepted

## Decision
- `model`/`messages` validation runs through a DRF `Serializer` (`ChatCompletionRequestSerializer`), not manual checks or `try/except KeyError`.
- A validation failure is handled locally in the view (`serializer.is_valid()` without `raise_exception`) and translated by hand into the existing OpenAI envelope (`type`/`code` = `"invalid_request_error"`), so the format stays consistent with the four provider error paths — no global `exception_handler`.
- On a 400, no `RequestLog` entry is deliberately created.

## Context
- M1-06 Test 5 requires: an invalid body (`model`/`messages` missing) → 400.
- The view previously accessed `request.data["model"]`/`["messages"]` directly — a missing key produced an unhandled `KeyError` instead of a defined 400.

## Alternatives considered
- Manual `if`/`not in` checks or `try/except KeyError` — rejected. DRF already provides the serializer as the idiomatic tool for request validation; this is not premature abstraction, it's using the already-adopted framework for its intended purpose.
- `serializer.is_valid(raise_exception=True)` plus a global DRF `exception_handler` translating every error (including built-in ones like 404) into the OpenAI envelope — rejected for now. There is currently only one endpoint with this contract; a global handler would be broader than the current need. Deferred until a second OpenAI-compatible endpoint provides the second use case that justifies the abstraction.
- Writing a `RequestLog` for 400s too — rejected. The request was never forwarded to a provider; most log fields (`provider`, `used_model`, `provider_latency_ms`) would be meaningless or would need to be filled artificially. Unlike the four provider error paths (ADR-0011), this is clearly the client's own fault, not an operational event that needs the same tracking.

## Consequences
- Groq is never contacted on an invalid body — no unnecessary network call for broken requests.
- Once a second OpenAI-compatible endpoint exists, the global-handler approach should be reconsidered, to avoid duplicating the envelope-building code.
- M1-06's test list is now complete (401, 200, RequestLog, four provider error paths, 400).
