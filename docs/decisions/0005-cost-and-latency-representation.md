# ADR-0005: Cost and latency representation

**Date:** 2026-09-14
**Status:** Accepted

## Decision
- Costs stored as integers in micro-cents; unit is part of the field name (cost_micro_cents on RequestLog, monthly_budget_micro_cents on ApiKey), so a scale mismatch is visible at read time, not just in a comment
- rate_limit_per_minute on ApiKey, unit named explicitly; the enforcement algorithm (fixed vs. sliding window) is a separate, later decision (ADR-0012)
- Latency measured twice: total gateway duration and provider-only duration, stored separately — their difference is the gateway's own overhead
- RequestLog.api_key (FK to ApiKey) is required, not nullable — a request with no valid key never gets a row, since there's nothing valid to attach it to
- Provider-outcome fields on RequestLog handle "not reached" differently by type: prompt_tokens, completion_tokens, cost_micro_cents, and provider_latency_ms are null=True and stay NULL; provider (CharField) has no null=True and falls back to Django's implicit empty-string default instead, per Django's convention of avoiding null on string fields; cache_hit (default=False) and fallback_depth (default=0) already carry a meaningful default for "didn't happen" and were never a nullability question to begin with

## Context
Migrations shouldn't change after the schema has run on the VPS, so the cost/latency representation and the logging scope need to be decided before the first migration, not discovered afterward. 
Zone-B auth tests (M1-03) cover four cases — missing header, invalid key, deactivated key, valid key — and the first two never reach a valid ApiKey, which forces the nullability question now.

## Alternatives considered
- DecimalField for cost — rejected in favor of integer micro-cents. Idiomatic and avoids float drift too, but doesn't remove the need to pick a precision, and doesn't get the "unit in the name" self-documentation for free. Integer-smallest-unit is also the common practice for representing money (e.g. Stripe stores amounts as integer cents).
- Logging every request regardless of auth outcome — rejected. A RequestLog row needs a subject (the key); an invalid/missing key has none, so there's nothing meaningful to attach a row to.

## Consequences
- Every future write to cost_micro_cents or monthly_budget_micro_cents must stay in the same unit — a helper function for the conversion (micro-cents ↔ display currency) is worth writing once RequestLog exists, rather than converting inline wherever it's needed.
