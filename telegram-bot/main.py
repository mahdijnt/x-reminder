from __future__ import annotations

import sys

from bot.app import build_application
from bot.config import get_settings
from bot.logging import setup_logging


def main() -> None:
    setup_logging()
    settings = get_settings()
    if not settings.telegram_bot_token:
        print(
            "TELEGRAM_BOT_TOKEN is not set. Export it in your environment or .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    application = build_application(settings)
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
