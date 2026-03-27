from __future__ import annotations

import os
from pathlib import Path


def _candidate_env_files() -> list[Path]:
    module_path = Path(__file__).resolve()
    root = module_path.parents[2]
    return [root / ".env", root / ".env.production"]


def _parse_env_line(raw_line: str) -> tuple[str, str] | None:
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip().strip("'").strip('"')
    if not key:
        return None
    return key, value


def _apply_env_aliases(override: bool = False) -> None:
    aliases = {
        "ASK_URL": "UNIGURU_ASK_URL",
        "AUTH_ENABLED": "UNIGURU_API_AUTH_REQUIRED",
        "PORT": "NODE_BACKEND_PORT",
    }
    for source_key, target_key in aliases.items():
        source_value = os.getenv(source_key)
        if source_value is None:
            continue
        if override or target_key not in os.environ:
            os.environ[target_key] = source_value


def load_project_env(override: bool = False) -> None:
    for env_path in _candidate_env_files():
        if not env_path.exists():
            continue
        try:
            lines = env_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            parsed = _parse_env_line(line)
            if parsed is None:
                continue
            key, value = parsed
            if override or key not in os.environ:
                os.environ[key] = value
    _apply_env_aliases(override=override)
