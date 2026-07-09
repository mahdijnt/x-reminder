from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers import get_api_client, telegram_id
from keyboards.inline import main_inline_menu
from keyboards.reply import main_reply_keyboard
from localization.i18n import t


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await get_api_client(context).get_user_profile(telegram_id(update))
    text = t("commands.start_welcome", app_name=t("app_name"))
    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=main_reply_keyboard(),
            parse_mode="Markdown",
        )
        await update.message.reply_text(
            t("menus.main"),
            reply_markup=main_inline_menu(),
        )
