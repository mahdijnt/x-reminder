"""X API v2 path constants."""

from app.core.config import get_settings


def api_base() -> str:
    return get_settings().X_API_BASE_URL.rstrip("/")


def oauth_authorize_url() -> str:
    return get_settings().X_OAUTH_AUTHORIZE_URL


def oauth_token_url() -> str:
    return get_settings().X_OAUTH_TOKEN_URL


def oauth_revoke_url() -> str:
    return get_settings().X_OAUTH_REVOKE_URL


USERS_ME = "/2/users/me"
USER_BY_USERNAME = "/2/users/by/username/{username}"
USER_BY_ID = "/2/users/{user_id}"
USER_FOLLOWERS = "/2/users/{user_id}/followers"
USER_FOLLOWING = "/2/users/{user_id}/following"
USER_TWEETS = "/2/users/{user_id}/tweets"


def url(path: str, **params: str) -> str:
    formatted = path.format(**params) if params else path
    if not formatted.startswith("/"):
        formatted = "/" + formatted
    return api_base() + formatted
