from __future__ import annotations

from typing import Any

from localization.i18n import t


def tweet_notification(
    username: str,
    tweet_url: str,
    text: str,
    posted_at: str,
    locale: str | None = None,
) -> str:
    header = f"New post from @{username}"
    return (
        f"{header}\n"
        f"{text}\n\n"
        f"Link: {tweet_url}\n"
        f"Posted: {posted_at}"
    )


def notifications_digest(items: list[dict[str, Any]], locale: str | None = None) -> str:
    title = t("notifications.title", locale=locale)
    if not items:
        return f"*{title}*\n{t('notifications.empty', locale=locale)}"
    parts = [f"*{title}*"]
    for item in items[:10]:
        parts.append(
            tweet_notification(
                item.get("username", "?"),
                item.get("tweet_url", ""),
                item.get("text", ""),
                item.get("posted_at", ""),
                locale=locale,
            )
        )
        parts.append("---")
    if parts[-1] == "---":
        parts.pop()
    return "\n\n".join(parts)


def targets_achieved_message(items: list[dict[str, Any]], locale: str | None = None) -> str:
    title = t("target.title", locale=locale)
    if not items:
        return f"*{title}*\n{t('target.empty', locale=locale)}"
    lines = [f"*{title}*"]
    for item in items:
        lines.append(
            f"@{item.get('username')} — {item.get('target_type')} at {item.get('achieved_at')}"
        )
    return "\n".join(lines)


def paginate_lines(lines: list[str], page: int, page_size: int = 5) -> tuple[list[str], int, int]:
    total_pages = max(1, (len(lines) + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))
    start = page * page_size
    return lines[start : start + page_size], page, total_pages
