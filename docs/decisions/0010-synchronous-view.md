# ADR-0010: Synchronous view

**Date:** 2026-09-25
**Status:** Accepted

## Decision
- The /v1/chat/completions endpoint (non-streaming, M1-06) is a synchronous DRF APIView (def post, not async def) — no bridging needed for auth, ORM, or the Groq adapter.
- Real async view architecture is deferred to M1-07 (streaming), where it's actually needed.

## Context
- The plan assumed async def views would be needed starting with M1-06. An empirical test against the installed DRF version (3.18.1) shows: APIView.dispatch() does not await handler methods — an async def post() returns an un-awaited coroutine object and crashes with AssertionError.
- ApiKeyAuthentication (ADR-0007) is built as a synchronous DRF authentication class, tightly coupled to APIView's dispatch mechanism.

## Alternatives considered
- A plain Django View with a real async def instead of DRF's APIView — rejected for M1-06: would mean calling ApiKeyAuthentication manually and translating AuthenticationFailed into a 401 response by hand, for a benefit M1-06 doesn't need yet (no concurrent I/O to interleave; a synchronous view already runs non-blocking under ASGI via a thread pool).
- Upgrading DRF hoping for async dispatch support — not pursued, since new dependencies/version bumps require asking first per CLAUDE.md, and DRF has no established first-class async APIView support to date.

## Consequences
- M1-07 has to solve this problem for real (likely via one of the two paths rejected/deferred here) — its own ADR once that milestone starts.
- Every further Zone B endpoint until M1-07 stays synchronous by default, unless a concrete reason demands async sooner.
