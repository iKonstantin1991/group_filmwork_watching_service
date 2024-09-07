#!/bin/sh

uv run alembic upgrade head
uv run gunicorn src.main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

exec "$@"
