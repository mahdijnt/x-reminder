from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.constants import STATE_REMOVE_USERNAME
from localization.i18n import t


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text(t("flows.remove_prompt"))
    return STATE_REMOVE_USERNAME
