from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    log_level: str = "INFO"
    default_locale: str = "en"
    use_mock_backend: bool = True


@lru_cache
def get_settings() -> Settings:
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
        use_mock_backend=use_mock,
    )
