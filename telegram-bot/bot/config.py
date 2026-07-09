from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    log_level: str = "INFO"
    default_locale: str = "en"
    backend_base_url: str = "http://localhost:8000/api/v1"
    use_mock_backend: bool = True
    api_timeout_seconds: float = 10.0
    error_monitoring_provider: str = "none"
    error_monitoring_dsn: str = ""


def _load_env_files() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    for env_path in (repo_root / ".env", repo_root / ".env.local"):
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@lru_cache
def get_settings() -> Settings:
    _load_env_files()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    log_level = os.environ.get("BOT_LOG_LEVEL", os.environ.get("LOG_LEVEL", "INFO")).strip()
    default_locale = os.environ.get("DEFAULT_LOCALE", "en").strip().lower()
    use_mock = os.environ.get("USE_MOCK_BACKEND", "true").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    return Settings(
        telegram_bot_token=token,
        log_level=log_level,
        default_locale=default_locale,
        backend_base_url=os.environ.get("BOT_BACKEND_BASE_URL", "http://localhost:8000/api/v1").strip(),
        use_mock_backend=use_mock,
        api_timeout_seconds=float(os.environ.get("BOT_API_TIMEOUT_SECONDS", "10").strip()),
        error_monitoring_provider=os.environ.get("BOT_ERROR_MONITORING_PROVIDER", "none").strip().lower(),
        error_monitoring_dsn=os.environ.get("BOT_ERROR_MONITORING_DSN", "").strip(),
    )
