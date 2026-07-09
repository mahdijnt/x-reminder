from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers import get_api_client, telegram_id
from keyboards.reply import main_reply_keyboard
from localization.i18n import t


async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = await get_api_client(context).connect_x(telegram_id(update))
    msg = t("commands.connect_ok", username=result.get("x_username", "mock"))
    if update.message:
        await update.message.reply_text(msg, reply_markup=main_reply_keyboard())
