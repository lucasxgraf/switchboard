# ADR-0005: Cost and latency representation

**Date:** 2026-09-14
**Status:** Accepted

## Decision
- Costs stored as integers in micro-cents; unit is part of the field name (cost_micro_cents on RequestLog, monthly_budget_micro_cents on ApiKey), so a scale mismatch is visible at read time, not just in a comment
- rate_limit_per_minute on ApiKey, unit named explicitly; the enforcement algorithm (fixed vs. sliding window) is a separate, later decision (ADR-0012)
- Latency measured twice: total gateway duration and provider-only duration, stored separately — their difference is the gateway's own overhead
- RequestLog.key (FK to ApiKey) is required, not nullable — a request with no valid key never gets a row, since there's nothing valid to attach it to
- Provider-outcome fields on RequestLog (Provider, Prompt-/Completion-Tokens, cost_micro_cents, provider latency, cache hit, fallback depth) are nullable — a request rejected before reaching a provider (deactivated key, rate-limited) still gets a row, but these fields stay empty

## Context
Migrations shouldn't change after the schema has run on the VPS, so the cost/latency representation and the logging scope need to be decided before the first migration, not discovered afterward. 
Zone-B auth tests (M1-03) cover four cases — missing header, invalid key, deactivated key, valid key — and the first two never reach a valid ApiKey, which forces the nullability question now.

## Alternatives considered
- DecimalField for cost — rejected in favor of integer micro-cents. Idiomatic and avoids float drift too, but doesn't remove the need to pick a precision, and doesn't get the "unit in the name" self-documentation for free. Integer-smallest-unit is also the common practice for representing money (e.g. Stripe stores amounts as integer cents).
- Logging every request regardless of auth outcome — rejected. A RequestLog row needs a subject (the key); an invalid/missing key has none, so there's nothing meaningful to attach a row to.

## Consequences
- Every future write to cost_micro_cents or monthly_budget_micro_cents must stay in the same unit — a helper function for the conversion (micro-cents ↔ display currency) is worth writing once RequestLog exists, rather than converting inline wherever it's needed.
