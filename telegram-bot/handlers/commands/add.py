from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.constants import STATE_ADD_USERNAME
from localization.i18n import t


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text(t("flows.add_prompt"))
    return STATE_ADD_USERNAME
