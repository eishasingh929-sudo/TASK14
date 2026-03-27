#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}/node-backend"

export PORT="${PORT:-3000}"
export NODE_BACKEND_PORT="${NODE_BACKEND_PORT:-$PORT}"
export ASK_URL="${ASK_URL:-http://localhost:8000/ask}"
export UNIGURU_ASK_URL="${UNIGURU_ASK_URL:-$ASK_URL}"

exec npm start
