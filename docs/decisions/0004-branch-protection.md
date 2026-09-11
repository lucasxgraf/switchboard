# ADR-0004: Branch protection

**Date:** 2026-09-11
**Status:** Accepted

## Decision
Classic branch protection rule on `main`, not a ruleset. Required in the
repo: PR before merge (no approval requirement, solo project), required
status check `test`, "Do not allow bypassing the above settings" enabled —
even the repo owner cannot bypass the rule.

## Context
Since M0-03 there is a CI workflow (lint, type check, migration check, tests)
that runs on every PR. Without branch protection it's only a recommendation —
anyone, including myself as owner, could push or merge directly to `main`
despite a red run.

GitHub offers two systems for this: the older "classic branch protection
rule" and the newer "rulesets".

## Alternatives considered
- Ruleset — rejected. More powerful (multiple branch patterns/repos at once,
  an "Evaluate" mode that only logs instead of blocking), but more concepts
  (targets, bypass list, enforcement status) for a single branch with one
  rule. Worth it once there are multiple branch patterns or repos.
- Without "Do not allow bypassing" — rejected. GitHub exempts repo admins
  from branch protection rules by default. Without this option the whole
  safeguard would be pointless for me as owner.

## Verification
- Created branch `test/branch-protection`:
  - Intentionally asserted 500 in `apps/core/test_healthz.py`, opened PR #1.
    CI ran red, the merge button was locked ("Required status check has
    failed").
- Reverted the test, pushed, CI turned green, button unlocked.
- Merged via squash merge, branch deleted.

## Consequences
- From now on every change goes through a PR with green CI; no more direct
  pushes to `main`. A new required status check (e.g. once CI gains
  Postgres/Redis jobs) must run at least once before it can be selected in
  the branch protection rule.
