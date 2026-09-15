#!/usr/bin/env bash
set -e # exit on error

ruff check .
ruff format --check .
mypy .
python manage.py makemigrations --check --dry-run
pytest