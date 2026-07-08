from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from components.formatters import format_dashboard_message, format_profile
from handlers import get_api_client, telegram_id
from localization.i18n import t


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api = get_api_client(context)
    tid = telegram_id(update)
    stats = await api.get_dashboard_stats(tid)
    profile = await api.get_user_profile(tid)
    text = (
        f"*{t('commands.status_title')}*\n\n"
        f"{format_dashboard_message(stats)}\n\n"
        f"{format_profile(profile)}"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")
