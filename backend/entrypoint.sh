#!/bin/sh
set -e

echo "Running database migrations..."
if ! uv run alembic upgrade heads; then
	echo "Migration upgrade failed; attempting recovery with alembic stamp heads..."
	uv run alembic stamp heads
	uv run alembic upgrade heads
fi

echo "Starting server..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
