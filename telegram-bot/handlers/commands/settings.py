from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.flow_views import _run_flow, settings_markup, settings_text


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    enabled_holder = {"value": False}

    async def compose() -> str:
        text, enabled = await settings_text(context, update)
        enabled_holder["value"] = enabled
        return text

    async def respond(message: str) -> None:
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=settings_markup(enabled_holder["value"]),
        )

    await _run_flow("settings", update, respond, compose)
