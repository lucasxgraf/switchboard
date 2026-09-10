# ADR-0003: Backend tooling and layout

**Date:** 2026-09-10
**Status:** Accepted

## Decision
The project is a monorepo: `backend/` (Django/Python) and, later, `frontend/`
(React) live in one repo but are separate projects with separate tooling.

`backend/` is its own project root, holding `manage.py`, `pyproject.toml`
(config for the packaging tools), and `requirements*.txt`. Backend tooling
(pytest, ruff, mypy) is run from `backend/`.

`settings.py` is split into four files: `base.py`, `dev.py`, `test.py`,
`production.py`. `base.py` holds everything environment-independent; the others
import `base.py` and override only their differences (e.g. `DEBUG` True/False).
Each entry point selects the module via `DJANGO_SETTINGS_MODULE`:
`manage.py` -> dev, `asgi.py`/`wsgi.py` -> production, pytest -> test (via
`pyproject.toml`).

`load_dotenv` runs only in `dev.py`. `test` and `production` never read a
`.env` file: tests stay hermetic, production takes its values from the
container environment.

ruff: `select = ["E", "F", "I", "UP", "B", "DJ"]`. `F403`/`F405`/`E501` are
ignored for `config/settings/*.py`.

mypy: django-stubs plugin, `disallow_untyped_defs = true`. `rest_framework.*`
-> `ignore_missing_imports`, `*.migrations.*` -> `ignore_errors`.

`requirements.txt` is a hand-maintained list of direct runtime dependencies,
pinned; `requirements-dev.txt` starts with `-r requirements.txt` and adds the
tooling. Transitive dependencies are left for pip to resolve.


## Context
The project targets three real environments (local, CI, VPS) with different
values for DB, DEBUG, SECRET_KEY, ALLOWED_HOSTS, and Sentry.

A single `settings.py` with many `if` branches gets hard to follow quickly.

Two test-runner setups were on the table (see below). The tooling rule set
should be small and individually justifiable, not 40 categories.

## Alternatives considered
- One `settings.py` driven entirely by `.env` variables — rejected. Works for
  a single target, but here there are three, differing in more than one flag.
  The split makes "DEBUG = True in production" structurally impossible.

- pytest config at the repo root with `pythonpath = ["backend"]` — rejected.
  `pythonpath` manipulates `sys.path`, is hard to explain, and root configs in
  monorepos accumulate frontend-unrelated settings. "Backend tooling runs from
  `backend/`" is a one-line rule.

- Enforcing ruff `E501` globally at 88 — rejected for `config/settings/*.py`,
  because Django framework path strings there can't be wrapped sensibly.
  `ruff format` governs line length in the actual code.

- mypy `strict = true` — deferred. It flips ~15 flags, some of which fight
  django-stubs. Start with `disallow_untyped_defs`, tighten later.

- A full `pip freeze` lockfile as `requirements.txt` — rejected for now. It is
  reproducible but mixes runtime and dev packages and carries ~30 transitive
  pins that can't be explained line by line. Readability wins for a project
  whose point is defending every line; Docker-level reproducibility is handled
  separately in M1.

## Consequences
- All backend commands run from `backend/`; CI jobs need
  `working-directory: backend`.

- SECRET_KEY must be set in every env file (removed from `base.py`): `test` a
  throwaway value, `dev` with a fallback, `production` required from the
  environment.

- New mypy exceptions go in `pyproject.toml` rather than scattered
  `# type: ignore` comments.

- Adding a dependency means editing `requirements.txt` (or `-dev.txt`) by hand,
  not re-running `pip freeze`.

- The frontend will get its own tooling in `frontend/`, mirroring this setup.
