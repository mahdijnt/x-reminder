from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.commands.dashboard import dashboard_command
from handlers.commands.profile import profile_command


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await dashboard_command(update, context)
    await profile_command(update, context)
