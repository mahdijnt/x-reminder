from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from localization.i18n import t

logger = logging.getLogger(__name__)


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)
    message = t("errors.generic")
    if isinstance(update, Update):
        if update.callback_query:
            try:
                await update.callback_query.answer(message, show_alert=True)
            except Exception:
                pass
        elif update.effective_message:
            try:
                await update.effective_message.reply_text(message)
            except Exception:
                pass
