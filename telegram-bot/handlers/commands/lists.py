from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.flow_views import (
    _run_flow,
    dashboard_markup,
    dashboard_text,
    lists_markup,
    settings_markup,
    settings_text,
    watch_lists_text,
)


async def lists_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    async def respond(message: str) -> None:
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=lists_markup())

    await _run_flow("lists", update, respond, lambda: watch_lists_text(context, update))
