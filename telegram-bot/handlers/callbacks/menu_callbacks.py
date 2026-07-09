from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from components.formatters import (
    format_account_list,
    format_dashboard_message,
    format_profile,
)
from components.messages import notifications_digest, targets_achieved_message
from handlers import get_api_client, telegram_id
from keyboards.inline import (
    dashboard_menu,
    list_pagination_menu,
    main_inline_menu,
    notifications_menu,
    profile_menu,
    settings_menu,
    target_menu,
    watch_lists_menu,
)
from localization.i18n import t
from components.messages import paginate_lines


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
    api = get_api_client(context)
    tid = telegram_id(update)
    action = query.data.split(":", 1)[1]

    if action == "main":
        await query.edit_message_text(
            t("menus.main"), reply_markup=main_inline_menu()
        )
        return

    if action == "dashboard":
        stats = await api.get_dashboard_stats(tid)
        text = format_dashboard_message(stats)
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=dashboard_menu()
        )
        return

    if action == "lists":
        await query.edit_message_text(
            t("menus.watch_lists"), reply_markup=watch_lists_menu()
        )
        return

    if action == "notifications":
        items = await api.get_notifications(tid)
        text = notifications_digest(items)
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=notifications_menu()
        )
        return

    if action == "target":
        items = await api.get_target_achieved(tid)
        text = targets_achieved_message(items)
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=target_menu()
        )
        return

    if action == "profile":
        profile = await api.get_user_profile(tid)
        text = format_profile(profile)
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=profile_menu()
        )
        return

    if action == "settings":
        settings = await api.get_settings(tid)
        text = f"*{t('commands.settings_title')}*"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=settings_menu(bool(settings.get("notifications_enabled"))),
        )
        return

    if action == "connect":
        result = await api.connect_x(tid)
        await query.edit_message_text(
            t("commands.connect_ok", username=result.get("x_username", "mock")),
            reply_markup=main_inline_menu(),
        )


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
    api = get_api_client(context)
    data = await api.get_watch_lists(telegram_id(update))
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
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=list_pagination_menu(list_key, page, total_pages),
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()
    api = get_api_client(context)
    tid = telegram_id(update)
    action = query.data.split(":", 1)[1]
    settings = await api.get_settings(tid)

    if action == "toggle_notifications":
        new_val = not bool(settings.get("notifications_enabled"))
        settings = await api.update_settings(tid, {"notifications_enabled": new_val})
        note = (
            t("flows.toggle_notifications_on")
            if new_val
            else t("flows.toggle_notifications_off")
        )
        await query.edit_message_text(
            f"*{t('commands.settings_title')}*\n{note}",
            parse_mode="Markdown",
            reply_markup=settings_menu(new_val),
        )
        return

    if action == "language":
        await query.edit_message_text(
            "Language switching is mocked (EN only for now).",
            reply_markup=settings_menu(bool(settings.get("notifications_enabled"))),
        )
