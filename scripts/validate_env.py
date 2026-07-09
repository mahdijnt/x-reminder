from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "backend": ["SECRET_KEY", "REDIS_URL"],
    "dashboard": ["NEXT_PUBLIC_API_BASE_URL", "NEXT_PUBLIC_APP_URL"],
    "telegram-bot": ["TELEGRAM_BOT_TOKEN"],
}

PLACEHOLDER_VALUES = {
    "",
    "replace-with-strong-secret",
    "change-me-in-production",
}


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _keys_in_example(path: Path) -> set[str]:
    keys: set[str] = set()
    if not path.is_file():
        return keys
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        keys.add(line.split("=", 1)[0].strip())
    return keys


def _check_example_keys() -> int:
    example_keys = _keys_in_example(REPO_ROOT / ".env.example")
    undocumented: list[tuple[str, str]] = []
    for service, keys in REQUIRED.items():
        for key in keys:
            if key not in example_keys:
                undocumented.append((service, key))
    if undocumented:
        print(".env.example is missing required keys:")
        for service, key in undocumented:
            print(f"- [{service}] {key}")
        return 1
    print(".env.example documents all required keys.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required deployment environment variables.")
    parser.add_argument(
        "--check-example",
        action="store_true",
        help="Verify .env.example documents all required keys (no live secrets required).",
    )
    args = parser.parse_args()

    if args.check_example:
        return _check_example_keys()

    _load_env_file(REPO_ROOT / ".env")
    _load_env_file(REPO_ROOT / ".env.local")

    missing: list[tuple[str, str]] = []
    weak: list[tuple[str, str]] = []
    for service, keys in REQUIRED.items():
        for key in keys:
            value = os.getenv(key)
            if not value or value in PLACEHOLDER_VALUES:
                missing.append((service, key))
            elif key == "SECRET_KEY" and os.getenv("ENVIRONMENT", "development") == "production":
                if value in PLACEHOLDER_VALUES:
                    weak.append((service, key))

    if missing:
        print("Missing required environment variables:")
        for service, key in missing:
            print(f"- [{service}] {key}")
        print("Tip: copy .env.example to .env and set real values.")
        return 1

    if weak:
        print("Weak values detected for production:")
        for service, key in weak:
            print(f"- [{service}] {key}")
        return 1

    print("Environment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
