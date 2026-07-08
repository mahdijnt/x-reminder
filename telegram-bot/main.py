import os

from telegram.ext import Application


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    # Skeleton application setup only.
    application = Application.builder().token(token).build()

    # No handlers/menu implemented yet.
    application.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()
