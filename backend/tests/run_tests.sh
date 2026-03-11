#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "Running test suite..."

uv run pytest tests/ -v "$@"
