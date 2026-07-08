from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.constants import STATE_ADD_USERNAME, STATE_REMOVE_USERNAME
from handlers import get_api_client, telegram_id
from localization.i18n import t


async def add_username_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if not update.message or not update.message.text:
        return STATE_ADD_USERNAME
    username = update.message.text.strip()
    result = await get_api_client(context).add_account(telegram_id(update), username)
    if not result.get("ok"):
        err = result.get("error")
        if err == "already_exists":
            await update.message.reply_text(t("errors.account_exists"))
        else:
            await update.message.reply_text(t("errors.invalid_username"))
        return STATE_ADD_USERNAME
    await update.message.reply_text(
        t("flows.add_success", username=result["account"]["username"])
    )
    return ConversationHandler.END


async def remove_username_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if not update.message or not update.message.text:
        return STATE_REMOVE_USERNAME
    username = update.message.text.strip()
    result = await get_api_client(context).remove_account(telegram_id(update), username)
    if not result.get("ok"):
        await update.message.reply_text(t("errors.account_not_found"))
        return STATE_REMOVE_USERNAME
    await update.message.reply_text(t("flows.remove_success", username=result["removed"]))
    return ConversationHandler.END


async def cancel_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if update.message:
        await update.message.reply_text(t("errors.cancelled"))
    return ConversationHandler.END
