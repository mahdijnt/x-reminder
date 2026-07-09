from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from components.messages import paginate_lines
from handlers import get_api_client, telegram_id
from handlers.flow_views import (
    _run_flow,
    dashboard_markup,
    dashboard_text,
    lists_markup,
    notifications_markup,
    notifications_text,
    profile_markup,
    profile_text,
    settings_markup,
    settings_text,
    target_achieved_text,
    target_markup,
)
from keyboards.inline import list_pagination_menu, main_inline_menu, watch_lists_menu
from localization.i18n import t
from services.api_client import BackendError

logger = logging.getLogger(__name__)

LIST_KEY_MAP = {
    "follow_targets": ("follow_targets", "lists.follow_targets"),
    "following": ("following", "lists.following"),
    "mutual": ("mutual_followers", "lists.mutual"),
}


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()
    action = query.data.split(":", 1)[1]

    async def respond(message: str) -> None:
        markup = main_inline_menu()
        if action == "dashboard":
            markup = dashboard_markup()
        elif action == "lists":
            markup = lists_markup()
        elif action == "notifications":
            markup = notifications_markup()
        elif action == "target":
            markup = target_markup()
        elif action == "profile":
            markup = profile_markup()
        elif action == "settings":
            enabled = bool(context.chat_data.get("_settings_enabled", False))
            markup = settings_markup(enabled)
        await query.edit_message_text(message, parse_mode="Markdown", reply_markup=markup)

    if action == "main":
        await query.edit_message_text(t("menus.main"), reply_markup=main_inline_menu())
        return
    if action == "dashboard":
        await _run_flow(action, update, respond, lambda: dashboard_text(context, update))
        return
    if action == "lists":
        await query.edit_message_text(t("menus.watch_lists"), reply_markup=watch_lists_menu())
        return
    if action == "notifications":
        await _run_flow(action, update, respond, lambda: notifications_text(context, update))
        return
    if action == "target":
        await _run_flow(action, update, respond, lambda: target_achieved_text(context, update))
        return
    if action == "profile":
        await _run_flow(action, update, respond, lambda: profile_text(context, update))
        return
    if action == "settings":
        async def compose() -> str:
            text, enabled = await settings_text(context, update)
            context.chat_data["_settings_enabled"] = enabled
            return text

        await _run_flow(action, update, respond, compose)
        return
    if action == "connect":
        try:
            result = await get_api_client(context).connect_x(telegram_id(update))
            auth_url = result.get("authorization_url", "")
            text = t("commands.connect_ok", username=result.get("x_username", "authorized"))
            if auth_url:
                text = f"{text}\n{auth_url}"
            await query.edit_message_text(text, reply_markup=main_inline_menu())
        except BackendError:
            await query.edit_message_text(t("errors.backend_unavailable"), reply_markup=main_inline_menu())


async def list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()
    parts = query.data.split(":")
    if len(parts) != 3:
        return
    _, list_key, page_s = parts
    page = int(page_s)
    try:
        data = await get_api_client(context).get_watch_lists(telegram_id(update))
    except BackendError:
        await query.edit_message_text(t("errors.backend_unavailable"), reply_markup=watch_lists_menu())
        return

    bucket_key, title_key = LIST_KEY_MAP.get(list_key, ("follow_targets", "lists.follow_targets"))
    accounts = data.get(bucket_key, [])
    lines = [f"@{a.get('username')}" for a in accounts]
    if not lines:
        text = f"*{t(title_key)}*\n{t('lists.empty')}"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=watch_lists_menu())
        return
    page_lines, page, total_pages = paginate_lines(lines, page)
    body = "\n".join(page_lines)
    text = f"*{t(title_key)}* (page {page + 1}/{total_pages})\n{body}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=list_pagination_menu(list_key, page, total_pages))


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()
    action = query.data.split(":", 1)[1]
    api = get_api_client(context)
    tid = telegram_id(update)

    try:
        settings = await api.get_settings(tid)
        if action == "toggle_notifications":
            new_val = not bool(settings.get("notifications_enabled"))
            settings = await api.update_settings(tid, {"notifications_enabled": new_val})
            note = t("flows.toggle_notifications_on") if new_val else t("flows.toggle_notifications_off")
            await query.edit_message_text(
                f"*{t('commands.settings_title')}*\n{note}",
                parse_mode="Markdown",
                reply_markup=settings_markup(bool(settings.get("notifications_enabled"))),
            )
            return

        if action == "language":
            await query.edit_message_text(
                t("settings.language_not_supported"),
                reply_markup=settings_markup(bool(settings.get("notifications_enabled"))),
            )
    except BackendError:
        logger.warning("bot_settings_callback_failed")
        await query.edit_message_text(t("errors.backend_unavailable"), reply_markup=main_inline_menu())

