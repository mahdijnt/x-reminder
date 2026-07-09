from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.constants import CB_LIST, CB_MENU, CB_NOTIF, CB_PROFILE, CB_SETTINGS, CB_TARGET
from localization.i18n import t


def _back_button(data: str = f"{CB_MENU}:main") -> InlineKeyboardButton:
    return InlineKeyboardButton(t("menus.back"), callback_data=data)


def main_inline_menu(locale: str | None = None) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                t("menus.dashboard", locale=locale), callback_data=f"{CB_MENU}:dashboard"
            ),
            InlineKeyboardButton(
                t("menus.watch_lists", locale=locale), callback_data=f"{CB_MENU}:lists"
            ),
        ],
        [
            InlineKeyboardButton(
                t("menus.notifications", locale=locale), callback_data=f"{CB_MENU}:notifications"
            ),
            InlineKeyboardButton(
                t("menus.target_achieved", locale=locale), callback_data=f"{CB_MENU}:target"
            ),
        ],
        [
            InlineKeyboardButton(
                t("menus.profile", locale=locale), callback_data=f"{CB_MENU}:profile"
            ),
            InlineKeyboardButton(
                t("menus.settings", locale=locale), callback_data=f"{CB_MENU}:settings"
            ),
        ],
        [
            InlineKeyboardButton(
                t("menus.connect_x", locale=locale), callback_data=f"{CB_MENU}:connect"
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def dashboard_menu(locale: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("menus.refresh", locale=locale), callback_data=f"{CB_MENU}:dashboard"
                )
            ],
            [_back_button()],
        ]
    )


def watch_lists_menu(locale: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("lists.follow_targets", locale=locale),
                    callback_data=f"{CB_LIST}:follow_targets:0",
                )
            ],
            [
                InlineKeyboardButton(
                    t("lists.following", locale=locale),
                    callback_data=f"{CB_LIST}:following:0",
                )
            ],
            [
                InlineKeyboardButton(
                    t("lists.mutual", locale=locale),
                    callback_data=f"{CB_LIST}:mutual:0",
                )
            ],
            [_back_button()],
        ]
    )


def list_pagination_menu(list_key: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    nav = []
    if page > 0:
        nav.append(
            InlineKeyboardButton("Prev", callback_data=f"{CB_LIST}:{list_key}:{page - 1}")
        )
    if page < total_pages - 1:
        nav.append(
            InlineKeyboardButton("Next", callback_data=f"{CB_LIST}:{list_key}:{page + 1}")
        )
    rows = [nav] if nav else []
    rows.append([_back_button(f"{CB_MENU}:lists")])
    return InlineKeyboardMarkup(rows)


def settings_menu(notifications_on: bool, locale: str | None = None) -> InlineKeyboardMarkup:
    toggle_label = t("settings.notifications", locale=locale) + (
        " ON" if notifications_on else " OFF"
    )
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    toggle_label, callback_data=f"{CB_SETTINGS}:toggle_notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    t("settings.language", locale=locale),
                    callback_data=f"{CB_SETTINGS}:language",
                )
            ],
            [_back_button()],
        ]
    )


def notifications_menu(locale: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    t("menus.refresh", locale=locale), callback_data=f"{CB_MENU}:notifications"
                )
            ],
            [_back_button()],
        ]
    )


def target_menu(locale: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_back_button()]])


def profile_menu(locale: str | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_back_button()]])
