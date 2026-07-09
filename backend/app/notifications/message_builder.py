from __future__ import annotations

from collections import defaultdict
from html import escape

from app.notifications.models import TweetNotificationData


def _format_timestamp(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def build_single_tweet_message(tweet: TweetNotificationData) -> str:
    username = escape(tweet.username or tweet.author_id)
    link = escape(tweet.url)
    ts = escape(_format_timestamp(tweet.created_at))
    return (
        "<b>New activity detected</b>\n"
        f"@{username}\n"
        f'<a href="{link}">{link}</a>\n'
        f"<i>{ts}</i>"
    )


def build_batch_message(tweets: list[TweetNotificationData]) -> str:
    if len(tweets) == 1:
        return build_single_tweet_message(tweets[0])
    by_list: dict[str, list[TweetNotificationData]] = defaultdict(list)
    for t in tweets:
        by_list[t.list_type].append(t)
    lines = ["<b>New activity detected</b>"]
    for list_type, items in sorted(by_list.items()):
        label = escape(list_type.replace("-", " ").title())
        lines.append(f"\n<b>{label}</b>")
        for tweet in items:
            username = escape(tweet.username or tweet.author_id)
            link = escape(tweet.url)
            ts = escape(_format_timestamp(tweet.created_at))
            lines.append(f"@{username} — <a href=\"{link}\">tweet</a> ({ts})")
    return "\n".join(lines)
