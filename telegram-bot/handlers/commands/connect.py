from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers import get_api_client, telegram_id
from keyboards.reply import main_reply_keyboard
from localization.i18n import t
from services.api_client import BackendError


async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    try:
        result = await get_api_client(context).connect_x(telegram_id(update))
    except BackendError:
        await update.message.reply_text(t("errors.backend_unavailable"), reply_markup=main_reply_keyboard())
        return

    msg = t("commands.connect_ok", username=result.get("x_username", "authorized"))
    auth_url = result.get("authorization_url", "")
    if auth_url:
        msg = f"{msg}\n{auth_url}"
    await update.message.reply_text(msg, reply_markup=main_reply_keyboard())
