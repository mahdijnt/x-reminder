from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.flow_views import _run_flow, dashboard_markup, dashboard_text


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    async def respond(message: str) -> None:
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=dashboard_markup())

    await _run_flow("dashboard", update, respond, lambda: dashboard_text(context, update))
