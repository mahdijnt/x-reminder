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
    api_timeout_seconds: float = 10.0
    api_retry_attempts: int = 3
    api_retry_base_delay_seconds: float = 0.5
    api_retry_max_delay_seconds: float = 3.0
    bot_mode: str = "polling"
    webhook_url: str = ""
    webhook_secret_token: str = ""
    webhook_listen_host: str = "0.0.0.0"
    webhook_listen_port: int = 8080
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


def _as_bool(value: str, default: bool) -> bool:
    text = value.strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


@lru_cache
def get_settings() -> Settings:
    _load_env_files()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    log_level = os.environ.get("BOT_LOG_LEVEL", os.environ.get("LOG_LEVEL", "INFO")).strip()
    default_locale = os.environ.get("DEFAULT_LOCALE", "en").strip().lower()
    backend_base_url = os.environ.get(
        "BACKEND_BASE_URL",
        os.environ.get("BOT_BACKEND_BASE_URL", "http://localhost:8000/api/v1"),
    ).strip()

    return Settings(
        telegram_bot_token=token,
        log_level=log_level,
        default_locale=default_locale,
        backend_base_url=backend_base_url,
        api_timeout_seconds=float(os.environ.get("BOT_API_TIMEOUT_SECONDS", "10").strip()),
        api_retry_attempts=int(os.environ.get("BOT_API_RETRY_ATTEMPTS", "3").strip()),
        api_retry_base_delay_seconds=float(os.environ.get("BOT_API_RETRY_BASE_DELAY_SECONDS", "0.5").strip()),
        api_retry_max_delay_seconds=float(os.environ.get("BOT_API_RETRY_MAX_DELAY_SECONDS", "3").strip()),
        bot_mode=os.environ.get("BOT_MODE", "polling").strip().lower(),
        webhook_url=os.environ.get("WEBHOOK_URL", "").strip(),
        webhook_secret_token=os.environ.get("WEBHOOK_SECRET_TOKEN", "").strip(),
        webhook_listen_host=os.environ.get("WEBHOOK_LISTEN_HOST", "0.0.0.0").strip(),
        webhook_listen_port=int(os.environ.get("WEBHOOK_LISTEN_PORT", "8080").strip()),
        error_monitoring_provider=os.environ.get("BOT_ERROR_MONITORING_PROVIDER", "none").strip().lower(),
        error_monitoring_dsn=os.environ.get("BOT_ERROR_MONITORING_DSN", "").strip(),
    )

