from __future__ import annotations

from typing import Any

from localization.i18n import t


def format_stat_card(title: str, lines: list[str]) -> str:
    body = "\n".join(f"  {line}" for line in lines)
    return f"*{title}*\n{body}"


def format_dashboard_message(stats: dict[str, Any], locale: str | None = None) -> str:
    x_line = (
        t("dashboard.x_connected", locale=locale)
        if stats.get("x_connected")
        else t("dashboard.x_not_connected", locale=locale)
    )
    lines = [
        f"Targets: {stats.get('follow_targets_count', 0)}",
        f"Following: {stats.get('following_count', 0)}",
        f"Mutual: {stats.get('mutual_count', 0)}",
        f"Unread notifications: {stats.get('notifications_unread', 0)}",
        f"Targets achieved: {stats.get('targets_achieved_count', 0)}",
        x_line,
    ]
    return format_stat_card(t("dashboard.card_title", locale=locale), lines)


def format_account_list(accounts: list[dict[str, Any]], empty_msg: str) -> str:
    if not accounts:
        return empty_msg
    rows = []
    for a in accounts:
        uname = a.get("username", "?")
        name = a.get("display_name", uname)
        followers = a.get("followers")
        extra = f" ({followers:,} followers)" if isinstance(followers, int) else ""
        rows.append(f"@{uname} — {name}{extra}")
    return "\n".join(rows)


def format_profile(profile: dict[str, Any], locale: str | None = None) -> str:
    title = t("profile.title", locale=locale)
    lines = [
        f"Telegram ID: {profile.get('telegram_id')}",
        f"Display: {profile.get('display_name')}",
        f"X: @{profile.get('x_username')}" if profile.get("x_username") else "X: not linked",
        f"Locale: {profile.get('locale', 'en')}",
    ]
    return format_stat_card(title, lines)
