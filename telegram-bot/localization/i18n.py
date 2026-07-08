from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from bot.config import get_settings

_LOCALE_DIR = Path(__file__).resolve().parent


@lru_cache
def _load_locale(locale: str) -> dict[str, Any]:
    path = _LOCALE_DIR / f"{locale}.json"
    if not path.is_file():
        path = _LOCALE_DIR / "en.json"
    with path.open(encoding="utf-8-sig") as f:
        return json.load(f)


def _get_nested(data: dict[str, Any], key: str) -> str | None:
    parts = key.split(".")
    node: Any = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def t(key: str, locale: str | None = None, **kwargs: Any) -> str:
    loc = (locale or get_settings().default_locale).lower()
    data = _load_locale(loc)
    template = _get_nested(data, key)
    if template is None:
        template = _get_nested(_load_locale("en"), key) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def reply_label_to_key(label: str) -> str | None:
    for loc in ("en",):
        data = _load_locale(loc)
        replies = data.get("reply", {})
        for k, v in replies.items():
            if v == label:
                return f"reply.{k}"
    return None
