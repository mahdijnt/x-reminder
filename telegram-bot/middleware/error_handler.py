from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import get_settings
from bot.error_reporting import report_exception
from localization.i18n import t
from services.api_client import BackendRequestError, BackendResponseError, BackendUnavailableError

logger = logging.getLogger(__name__)


def _friendly_message(error: Exception) -> str:
    if isinstance(error, BackendUnavailableError):
        return t("errors.backend_unavailable")
    if isinstance(error, (BackendRequestError, BackendResponseError)):
        return t("errors.backend_request_failed")
    return t("errors.generic")


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if context.error:
        report_exception(settings, context.error, context={"scope": "telegram_global_handler"})
    logger.exception(
        "bot_unhandled_error",
        exc_info=context.error,
        extra={
            "chat_id": update.effective_chat.id if isinstance(update, Update) and update.effective_chat else None,
            "user_id": update.effective_user.id if isinstance(update, Update) and update.effective_user else None,
        },
    )
    message = _friendly_message(context.error) if isinstance(context.error, Exception) else t("errors.generic")
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
