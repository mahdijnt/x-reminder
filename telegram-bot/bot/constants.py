"""Shared constants for callback data and conversation states."""

CB_MENU = "menu"
CB_LIST = "list"
CB_SETTINGS = "settings"
CB_NOTIF = "notif"
CB_PROFILE = "profile"
CB_TARGET = "target"
CB_PAGE = "page"

STATE_ADD_USERNAME = 1
STATE_REMOVE_USERNAME = 2
STATE_SETTINGS_NOTIFY = 3
STATE_SETTINGS_LANG = 4

REPLY_KEYS = (
    "reply.dashboard",
    "reply.my_lists",
    "reply.add_account",
    "reply.remove_account",
    "reply.target_achieved",
    "reply.settings",
)
