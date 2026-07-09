from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.commands.dashboard import dashboard_command
from handlers.commands.lists import lists_command
from handlers.commands.settings import settings_command
from handlers.commands.target_achieved import target_achieved_command
from localization.i18n import reply_label_to_key


async def reply_menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    key = reply_label_to_key(update.message.text.strip())
    if key == "reply.dashboard":
        await dashboard_command(update, context)
        return
    if key == "reply.my_lists":
        await lists_command(update, context)
        return
    if key == "reply.target_achieved":
        await target_achieved_command(update, context)
        return
    if key == "reply.settings":
        await settings_command(update, context)
        return
