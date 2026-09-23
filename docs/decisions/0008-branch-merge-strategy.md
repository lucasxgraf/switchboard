# ADR-0008: Branch granularity and merge strategy

**Date:** 2026-09-23
**Status:** Accepted

## Decision
- One branch per *bundle* of related tasks, not one branch per plan task.
  Example: M1-01 through M1-04 (data model, key model, authentication, admin)
  share the branch `feat/m1-api-key-model`.
- Commit granularity is unchanged: still one commit per completed task, with a
  meaningful message. This ADR changes branch and PR size, not commit size.
- **Rebase merge**, not squash merge.
- A bundle is merged by the end of its milestone week at the latest. A bundle
  that outgrows that window is a signal to split it, not to keep adding.

## Context
`docs/plan.md` section 2 specifies one branch per task plus squash merge. In
practice a plan task is too small to carry its own branch and PR — several are
sized at one session, and M1-01 produces no code at all (design only). The
per-PR overhead exceeded the benefit.

The cost of the opposite extreme became visible in M1: 14 commits covering
M1-01 through M1-05 accumulated on a single branch, `main` was still at the end
of M0, and no PR existed. CI had therefore verified nothing against `main` for
the entire milestone, and the required status check from M0-03 had not been
exercised since the proof PR.

The plan's stated reason for the branch workflow was a readable history for the
portfolio view. Broad branches combined with squash merging destroys exactly
that, which is what forced the merge-strategy half of this decision.

## Alternatives considered
- One branch per plan task (the plan's original) — rejected. PR overhead per
  one-session task is disproportionate, and design-only tasks have nothing to
  put in a PR.
- Broad branch + squash merge — rejected. Collapses N task commits into a
  single commit on `main`. The granular history then survives only inside the
  branch and on the PR page, and disappears once the branch is deleted. That
  removes the reason the workflow existed in the first place.
- Merge commit — rejected. Preserves the commits but makes `main` non-linear.
  No upside for a solo project with no parallel long-lived branches.

## Verification
- "Allow rebase merging" is enabled in Settings → General → Pull Requests.

## Consequences
- ADR-0004 records a squash merge in its verification section. That was correct
  at the time; for future merges this ADR supersedes it.
- Rebase merging rewrites commit SHAs. After a merge the local feature branch is
  stale: delete it and branch fresh off `main` instead of continuing on it.
- Work in progress stays on the feature branch as WIP commits. The branch may be
  ugly, `main` may not.
- In Linear, all issues belonging to one bundle move to Done together when the
  PR merges — Definition of Done item 6 requires the merged PR.
- A new required status check must run at least once before it can be selected
  in the branch protection rule (unchanged from ADR-0004).
