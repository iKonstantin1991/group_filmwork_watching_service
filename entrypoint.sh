#!/bin/sh

uv run alembic upgrade head
uv run gunicorn src.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

exec "$@"
