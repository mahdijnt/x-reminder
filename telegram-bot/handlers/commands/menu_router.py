from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from components.formatters import format_dashboard_message
from components.messages import notifications_digest, targets_achieved_message
from handlers import get_api_client, telegram_id
from handlers.commands.lists import lists_command
from handlers.commands.settings import settings_command
from keyboards.inline import dashboard_menu
from localization.i18n import reply_label_to_key


async def reply_menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    key = reply_label_to_key(update.message.text.strip())
    if key == "reply.dashboard":
        stats = await get_api_client(context).get_dashboard_stats(telegram_id(update))
        await update.message.reply_text(
            format_dashboard_message(stats),
            parse_mode="Markdown",
            reply_markup=dashboard_menu(),
        )
        return
    if key == "reply.my_lists":
        await lists_command(update, context)
        return
    if key == "reply.target_achieved":
        items = await get_api_client(context).get_target_achieved(telegram_id(update))
        await update.message.reply_text(
            targets_achieved_message(items), parse_mode="Markdown"
        )
        return
    if key == "reply.settings":
        await settings_command(update, context)
        return
