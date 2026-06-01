#!/bin/sh
set -e

export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-/tmp/stei-backend-venv}"

echo "Running database migrations..."
if ! uv run alembic upgrade heads; then
	echo "Migration upgrade failed; attempting recovery with alembic stamp heads..."
	uv run alembic stamp heads
	uv run alembic upgrade heads
fi

echo "Running seeder..."
uv run python scripts/seed.py

echo "Starting server..."
if [ "$APP_ENV" = "production" ]; then
	exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
fi

exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
