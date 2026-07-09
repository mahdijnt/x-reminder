from __future__ import annotations

import logging
from typing import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from components.formatters import format_account_list, format_dashboard_message, format_profile
from components.messages import notifications_digest, targets_achieved_message
from handlers import get_api_client, telegram_id
from keyboards.inline import dashboard_menu, notifications_menu, profile_menu, settings_menu, target_menu, watch_lists_menu
from localization.i18n import t
from services.api_client import BackendError

logger = logging.getLogger(__name__)

FlowResponder = Callable[[str], Awaitable[None]]


async def _run_flow(action: str, update: Update, respond: FlowResponder, fn: Callable[[], Awaitable[str]]) -> None:
    try:
        message = await fn()
        await respond(message)
    except BackendError:
        logger.warning(
            "bot_backend_flow_failed",
            extra={
                "action": action,
                "chat_id": update.effective_chat.id if update.effective_chat else None,
                "user_id": update.effective_user.id if update.effective_user else None,
            },
        )
        await respond(t("errors.backend_unavailable"))


async def dashboard_text(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    stats = await get_api_client(context).get_dashboard_stats(telegram_id(update))
    return format_dashboard_message(stats)


async def watch_lists_text(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    data = await get_api_client(context).get_watch_lists(telegram_id(update))
    sections = [
        f"*{t('lists.follow_targets')}*\n" + format_account_list(data.get("follow_targets", []), t("lists.empty")),
        f"*{t('lists.following')}*\n" + format_account_list(data.get("following", []), t("lists.empty")),
        f"*{t('lists.mutual')}*\n" + format_account_list(data.get("mutual_followers", []), t("lists.empty")),
    ]
    return f"*{t('commands.lists_title')}*\n\n" + "\n\n".join(sections)


async def notifications_text(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    items = await get_api_client(context).get_notifications(telegram_id(update))
    return notifications_digest(items)


async def target_achieved_text(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    items = await get_api_client(context).get_target_achieved(telegram_id(update))
    return targets_achieved_message(items)


async def profile_text(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    profile = await get_api_client(context).get_user_profile(telegram_id(update))
    return format_profile(profile)


async def settings_text(context: ContextTypes.DEFAULT_TYPE, update: Update) -> tuple[str, bool]:
    settings = await get_api_client(context).get_settings(telegram_id(update))
    text = f"*{t('commands.settings_title')}*\nNotifications: {settings.get('notifications_enabled')}"
    return text, bool(settings.get("notifications_enabled"))


def dashboard_markup():
    return dashboard_menu()


def lists_markup():
    return watch_lists_menu()


def notifications_markup():
    return notifications_menu()


def target_markup():
    return target_menu()


def profile_markup():
    return profile_menu()


def settings_markup(notifications_enabled: bool):
    return settings_menu(notifications_enabled)


__all__ = [
    "_run_flow",
    "dashboard_text",
    "watch_lists_text",
    "notifications_text",
    "target_achieved_text",
    "profile_text",
    "settings_text",
    "dashboard_markup",
    "lists_markup",
    "notifications_markup",
    "target_markup",
    "profile_markup",
    "settings_markup",
]
