#!/usr/bin/env sh
set -eu

HOST="${UNIGURU_HOST:-0.0.0.0}"
PORT="${UNIGURU_PORT:-8000}"
WORKERS="${UNIGURU_WORKERS:-2}"
export PYTHONPATH="${PYTHONPATH:-}:backend"

exec uvicorn uniguru.service.api:app --host "${HOST}" --port "${PORT}" --workers "${WORKERS}"
