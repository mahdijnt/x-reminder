from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.flow_views import _run_flow, notifications_markup, notifications_text


async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    async def respond(message: str) -> None:
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=notifications_markup())

    await _run_flow("notifications", update, respond, lambda: notifications_text(context, update))
