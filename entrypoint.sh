#!/bin/sh

uv run alembic upgrade head
uv run fastapi run --workers 2 src/main.py

exec "$@"
