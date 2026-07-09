from __future__ import annotations

import os
import sys

REQUIRED = {
    "backend": ["SECRET_KEY", "REDIS_URL"],
    "dashboard": ["NEXT_PUBLIC_API_BASE_URL", "NEXT_PUBLIC_APP_URL"],
    "telegram-bot": ["TELEGRAM_BOT_TOKEN"],
}


def main() -> int:
    missing = []
    for service, keys in REQUIRED.items():
        for key in keys:
            if not os.getenv(key):
                missing.append((service, key))
    if missing:
        print("Missing required environment variables:")
        for service, key in missing:
            print(f"- [{service}] {key}")
        return 1
    print("Environment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
