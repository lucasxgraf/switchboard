# ADR-0002: Python and packaging

**Date:** 2026-09-09
**Status:** Accepted

## Decision
Python 3.14.3, pip/venv.

## Context
Python 3.14.3 was already installed locally. uv/poetry were not
available. The risk was whether psycopg[binary] and uvicorn[standard]
(both with C extensions) have pre-built wheels for 3.14.

## Test
Ran the following in a fresh .venv:
python3 -m venv .venv && source .venv/bin/activate
pip install "psycopg[binary]" "uvicorn[standard]"

The install succeeded with no compiler errors.

## Alternatives considered
- uv/poetry — rejected, not installed, no added benefit for a project this size; CLAUDE.md requires a justification for every new dependency
- Install Python 3.13 as fallback — rejected, the test above didn't fail, so no need

## Consequences
.python-version pins 3.14.3, the Docker image later uses python:3.14-slim.
