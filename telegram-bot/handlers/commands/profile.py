from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.flow_views import _run_flow, profile_markup, profile_text


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    async def respond(message: str) -> None:
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=profile_markup())

    await _run_flow("profile", update, respond, lambda: profile_text(context, update))
