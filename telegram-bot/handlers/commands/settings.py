from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers import get_api_client, telegram_id
from keyboards.inline import settings_menu
from localization.i18n import t


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api = get_api_client(context)
    settings = await api.get_settings(telegram_id(update))
    text = f"*{t('commands.settings_title')}*\nNotifications: {settings.get('notifications_enabled')}"
    if update.message:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=settings_menu(bool(settings.get("notifications_enabled"))),
        )
