"""Centralized Redis key builders and TTL constants."""

from app.core.config import Settings, get_settings


class RedisTTL:
    """Default TTL values in seconds."""

    CACHE_SHORT = 60
    CACHE_DEFAULT = 300
    CACHE_LONG = 3600
    SESSION = 86400
    RATE_LIMIT_WINDOW = 60
    TEMP_TOKEN = 300
    USER_CACHE = 600


class RedisKeys:
    """Namespaced Redis key builders."""

    def __init__(self, prefix: str | None = None) -> None:
        settings = get_settings()
        self._prefix = (prefix or settings.REDIS_KEY_PREFIX).strip(":")

    def _key(self, *parts: str) -> str:
        return ":".join([self._prefix, *parts])

    def cache(self, key: str) -> str:
        return self._key("cache", key)

    def session(self, session_id: str) -> str:
        return self._key("session", session_id)

    def ratelimit(self, client_key: str, window_id: str | int) -> str:
        return self._key("ratelimit", client_key, str(window_id))

    def ratelimit_sliding(self, client_key: str) -> str:
        return self._key("ratelimit", "sliding", client_key)

    def user(self, user_id: str) -> str:
        return self._key("user", user_id)

    def temp(self, purpose: str, token_id: str) -> str:
        return self._key("temp", purpose, token_id)

    def x_oauth_tokens(self, app_user_id: str) -> str:
        return self._key("x", "oauth", app_user_id)

    def x_rate_limit(self, endpoint: str) -> str:
        return self._key("x", "ratelimit", endpoint)

    def x_profile(self, app_user_id: str) -> str:
        return self._key("x", "profile", app_user_id)

    def x_last_scan(self, app_user_id: str) -> str:
        return self._key("x", "last_scan", app_user_id)

    def x_watch_list(self, app_user_id: str, list_type: str) -> str:
        return self._key("x", "watchlist", app_user_id, list_type)

    def x_processed_tweet(self, app_user_id: str, tweet_id: str) -> str:
        return self._key("x", "processed", app_user_id, tweet_id)


def get_redis_keys(settings: Settings | None = None) -> RedisKeys:
    if settings is not None:
        return RedisKeys(prefix=settings.REDIS_KEY_PREFIX)
    return RedisKeys()
