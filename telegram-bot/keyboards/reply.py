from __future__ import annotations

from telegram import KeyboardButton, ReplyKeyboardMarkup

from localization.i18n import t


def main_reply_keyboard(locale: str | None = None) -> ReplyKeyboardMarkup:
    rows = [
        [
            KeyboardButton(t("reply.dashboard", locale=locale)),
            KeyboardButton(t("reply.my_lists", locale=locale)),
        ],
        [
            KeyboardButton(t("reply.add_account", locale=locale)),
            KeyboardButton(t("reply.remove_account", locale=locale)),
        ],
        [
            KeyboardButton(t("reply.target_achieved", locale=locale)),
            KeyboardButton(t("reply.settings", locale=locale)),
        ],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)
