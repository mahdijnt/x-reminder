from __future__ import annotations

import sys

from bot.app import build_application
from bot.config import get_settings
from bot.logging import setup_logging


def main() -> None:
    setup_logging()
    settings = get_settings()
    if not settings.telegram_bot_token:
        print("TELEGRAM_BOT_TOKEN is not set. Export it in your environment or .env file.", file=sys.stderr)
        sys.exit(1)

    application = build_application(settings)
    if settings.bot_mode == "webhook":
        if not settings.webhook_url:
            print("WEBHOOK_URL is required when BOT_MODE=webhook.", file=sys.stderr)
            sys.exit(1)
        application.run_webhook(
            listen=settings.webhook_listen_host,
            port=settings.webhook_listen_port,
            webhook_url=settings.webhook_url,
            secret_token=settings.webhook_secret_token or None,
            allowed_updates=["message", "callback_query"],
        )
        return

    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
