# ADR-0006: API key hashing

**Date:** 2026-09-14
**Status:** Accepted

## Decision
API key hashing via HMAC-SHA256 with a dedicated secret (`API_KEY_HASH_SECRET`, from `.env`).

## Context
API keys are high-entropy, randomly generated tokens (`secrets.token_urlsafe`), not human-chosen passwords — and the gateway checks the key on every request, not just at login.

## Alternatives considered
- Salted SHA-256 — would have been sufficient on its own (the key's entropy makes brute force practically infeasible even if both hash and salt leak), but rejected in favor of HMAC: for nearly identical implementation effort, HMAC additionally protects against a database-only leak (the secret lives in the server environment, not the DB).
- bcrypt/argon2 — rejected. Deliberately slow hashing schemes are designed for low-entropy, human-chosen passwords (brute-force protection). For an already high-entropy key, the artificial slowdown would only add unnecessary latency to every single gateway request.

## Consequences
`API_KEY_HASH_SECRET` must be set in every environment (same pattern as `SECRET_KEY`). The later verification logic must use `hmac.compare_digest()` instead of `==` to avoid timing attacks.
