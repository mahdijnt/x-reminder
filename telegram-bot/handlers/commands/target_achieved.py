from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.flow_views import _run_flow, target_achieved_text, target_markup


async def target_achieved_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    async def respond(message: str) -> None:
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=target_markup())

    await _run_flow("target_achieved", update, respond, lambda: target_achieved_text(context, update))
