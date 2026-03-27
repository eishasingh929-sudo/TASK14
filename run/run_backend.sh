#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${ROOT_DIR}/backend:${PYTHONPATH:-}"
export UNIGURU_HOST="${UNIGURU_HOST:-127.0.0.1}"
export UNIGURU_PORT="${UNIGURU_PORT:-8000}"
export UNIGURU_API_AUTH_REQUIRED="${UNIGURU_API_AUTH_REQUIRED:-false}"
export UNIGURU_LLM_URL="${UNIGURU_LLM_URL:-http://127.0.0.1:11434/api/generate}"
export UNIGURU_LLM_MODEL="${UNIGURU_LLM_MODEL:-gpt-oss:120b-cloud}"
export UNIGURU_LLM_TIMEOUT_SECONDS="${UNIGURU_LLM_TIMEOUT_SECONDS:-12}"

exec python "${ROOT_DIR}/backend/main.py"
