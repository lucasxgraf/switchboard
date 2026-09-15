# ADR-0007: API key authentication

**Date:** 2026-09-15
**Status:** Accepted

## Decision
- DRF authentication class (ApiKeyAuthentication) instead of ASGI middleware for API key verification.
- Since there's only one auth scheme (no session login, no second token type), authenticate() raises AuthenticationFailed on every failure case — instead of the usual DRF convention of returning None so the next authenticator can try, which has no one left to try here.
- authenticate_header() is implemented (returns "Bearer"), because DRF otherwise silently downgrades AuthenticationFailed/NotAuthenticated from 401 to 403 whenever no WWW-Authenticate scheme is offered (source: rest_framework/views.py::handle_exception).
- On success: the verified ApiKey is exposed both as its own attribute request.api_key (set directly on the DRF request object) and as the second element of the (user, auth) tuple ((None, api_key)). user stays None — there's no Django User model for gateway keys, and no IsAuthenticated permission is needed: enforcement happens entirely inside the authentication class.
- Tested against the full HTTP cycle, not in isolation against authenticate(): a test-local ProbeView + urlpatterns, activated only for the test class via @override_settings(ROOT_URLCONF=__name__) — the same pattern DRF's own test suite uses for its bundled authentication classes.

## Context
- M1-03 requires four test cases with four defined outcomes (no header, malformed header, unknown key, valid key) — the first three as 401.
- At decision time, no protected business endpoint exists yet (that comes in M1-06). The tests still needed to go through a real request/response cycle, not just call authenticate() in isolation — otherwise two things stay unproven: that DRF actually translates a raised exception into the right status code, and that request.api_key really reaches view code.
- Django runs under ASGI (M0 decision), but DRF authentication classes are synchronous — a known, accepted trade-off (see Consequences).

## Alternatives considered
- ASGI middleware — rejected. Would have run ahead of the whole stack, natively async. Downside: no access to view metadata (exceptions like /healthz only via path matching, not declaratively), no DRF request.auth/permission mechanism, would need its own 401 error formatting instead of DRF's built-in consistency.
- Returning None instead of raising on a missing header (the "normal" DRF convention for chained auth schemes) — rejected: walks straight into the 401/403 trap (DRF downgrades to 403 without authenticate_header()), and there's no second scheme here that would ever deserve a chance to try.
- response.data instead of response.json() in the tests — rejected: django-stubs doesn't know DRF's Response class, so mypy flags it as a type error. djangorestframework-stubs wasn't added as an extra dependency for this; .json() is closer to the actual HTTP contract anyway (parses the real response bytes instead of DRF's internal pre-render representation).

## Consequences
- Any future endpoint just sets authentication_classes = [ApiKeyAuthentication] and can rely on request.api_key once the view is reached.
- If a second auth scheme is ever added (not currently planned), authenticate() would need rework — it's currently built for exactly one scheme, not several chained ones.
- The async/sync coupling (ApiKey.verify_key is a synchronous ORM call, authenticate() is not an async def method) hasn't been checked yet for M1-06 (the first async def view) — it'll become relevant under load once the first real streaming endpoint exists.
