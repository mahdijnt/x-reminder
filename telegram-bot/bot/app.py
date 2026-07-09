from __future__ import annotations

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.config import Settings
from bot.constants import STATE_ADD_USERNAME, STATE_REMOVE_USERNAME
from handlers.callbacks.menu_callbacks import list_callback, menu_callback, settings_callback
from handlers.commands.add import add_command
from handlers.commands.connect import connect_command
from handlers.commands.dashboard import dashboard_command
from handlers.commands.lists import lists_command
from handlers.commands.menu_router import reply_menu_router
from handlers.commands.notifications import notifications_command
from handlers.commands.profile import profile_command
from handlers.commands.remove import remove_command
from handlers.commands.settings import settings_command
from handlers.commands.start import start_command
from handlers.commands.status import status_command
from handlers.commands.target_achieved import target_achieved_command
from handlers.conversations.account_flows import add_username_received, cancel_conversation, remove_username_received
from localization.i18n import t
from middleware.error_handler import global_error_handler
from services.api_client import ApiClient, create_api_client

logger = logging.getLogger(__name__)


def build_application(settings: Settings, api_client: ApiClient | None = None) -> Application:
    client = api_client or create_api_client(use_mock=settings.use_mock_backend, settings=settings)
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.bot_data["api_client"] = client

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_command), MessageHandler(filters.Regex(f"^{t('reply.add_account')}$"), add_command)],
        states={STATE_ADD_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_username_received)]},
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
        name="add_account",
        persistent=False,
    )

    remove_conv = ConversationHandler(
        entry_points=[CommandHandler("remove", remove_command), MessageHandler(filters.Regex(f"^{t('reply.remove_account')}$"), remove_command)],
        states={STATE_REMOVE_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_username_received)]},
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
        name="remove_account",
        persistent=False,
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("connect", connect_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("dashboard", dashboard_command))
    application.add_handler(CommandHandler("lists", lists_command))
    application.add_handler(CommandHandler("notifications", notifications_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("target", target_achieved_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(add_conv)
    application.add_handler(remove_conv)

    application.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^menu:"))
    application.add_handler(CallbackQueryHandler(list_callback, pattern=r"^list:"))
    application.add_handler(CallbackQueryHandler(settings_callback, pattern=r"^settings:"))

    reply_labels = "|".join([t("reply.dashboard"), t("reply.my_lists"), t("reply.target_achieved"), t("reply.settings")])
    application.add_handler(MessageHandler(filters.Regex(f"^({reply_labels})$"), reply_menu_router))

    application.add_error_handler(global_error_handler)
    logger.info("bot_application_handlers_registered", extra={"use_mock_backend": settings.use_mock_backend})
    return application
