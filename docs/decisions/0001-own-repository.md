# ADR-0001: Own repo

**Date:** 2026-09-09
**Status:** Accepted

## Decision
The project is a standalone GitHub repo, public from day 1.
It was excluded from the workspace repo.

## Context
The project lived under ~/Claude, a private multi-project workspace.
It also holds sensitive content. Build-in-public, its own CI, and a
shareable link required a separate, public repo.

## Alternatives considered
- Stay in the workspace repo — rejected, the workspace repo is private and has no CI run of its own
- Private until M1 is done — rejected, the repo is meant to be public from day 1

## Consequences
From now on: nothing gets committed that can't stand being public.
