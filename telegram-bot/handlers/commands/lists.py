from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from components.formatters import format_account_list
from handlers import get_api_client, telegram_id
from keyboards.inline import watch_lists_menu
from localization.i18n import t


async def lists_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api = get_api_client(context)
    data = await api.get_watch_lists(telegram_id(update))
    sections = [
        f"*{t('lists.follow_targets')}*\n"
        + format_account_list(data["follow_targets"], t("lists.empty")),
        f"*{t('lists.following')}*\n"
        + format_account_list(data["following"], t("lists.empty")),
        f"*{t('lists.mutual')}*\n"
        + format_account_list(data["mutual_followers"], t("lists.empty")),
    ]
    text = f"*{t('commands.lists_title')}*\n\n" + "\n\n".join(sections)
    if update.message:
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=watch_lists_menu()
        )
