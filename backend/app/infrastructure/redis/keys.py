"""Centralized Redis key builders and TTL constants."""

from app.core.config import Settings, get_settings


class RedisTTL:
    """Default TTL values in seconds (overridable via settings)."""

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


    def scheduler_lock(self, name: str) -> str:
        return self._key("scheduler", "lock", name)

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
    def monitoring_queue(self) -> str:
        return self._key("monitoring", "queue")

    def monitoring_retry(self) -> str:
        return self._key("monitoring", "retry")

    def monitoring_job(self, job_id: str) -> str:
        return self._key("monitoring", "job", job_id)

    def monitoring_job_index(self) -> str:
        return self._key("monitoring", "job_index")

    def monitoring_metrics(self) -> str:
        return self._key("monitoring", "metrics")

    def monitoring_last_poll(self, app_user_id: str, list_type: str) -> str:
        return self._key("monitoring", "last_poll", app_user_id, list_type)

    def monitoring_last_processed_tweet(self, app_user_id: str, list_type: str, x_user_id: str) -> str:
        return self._key("monitoring", "last_tweet", app_user_id, list_type, x_user_id)



    def notifications_queue(self) -> str:
        return self._key("notifications", "queue")

    def notifications_queue_priority(self, level: str) -> str:
        return self._key("notifications", "queue", "priority", level)

    def notifications_retry(self) -> str:
        return self._key("notifications", "retry")

    def notifications_failures(self) -> str:
        return self._key("notifications", "failures")

    def notifications_failure_item(self, failure_id: str) -> str:
        return self._key("notifications", "failures", "item", failure_id)

    def notifications_history(self, notification_id: str) -> str:
        return self._key("notifications", "history", notification_id)

    def notifications_history_index(self) -> str:
        return self._key("notifications", "history", "index")

    def notifications_metrics(self) -> str:
        return self._key("notifications", "metrics")

    def notifications_dedup(self, user_id: str, tweet_id: str) -> str:
        return self._key("notifications", "dedup", user_id, tweet_id)

    def notifications_pending_index(self) -> str:
        return self._key("notifications", "pending")



def get_redis_keys(settings: Settings | None = None) -> RedisKeys:
    if settings is not None:
        return RedisKeys(prefix=settings.REDIS_KEY_PREFIX)
    return RedisKeys()


class ConfigurableRedisTTL:
    def __init__(self, settings: Settings) -> None:
        self.cache_default = settings.REDIS_TTL_CACHE
        self.session = settings.REDIS_TTL_SESSION
        self.temp_token = settings.REDIS_TTL_TEMP
        self.scheduler_lock = settings.REDIS_TTL_SCHEDULER_LOCK
        self.cache_short = min(settings.REDIS_TTL_CACHE, 60) or 60
        self.cache_long = max(settings.REDIS_TTL_CACHE, 3600)
        self.user_cache = settings.REDIS_TTL_CACHE * 2


def get_redis_ttl(settings: Settings | None = None) -> ConfigurableRedisTTL:
    return ConfigurableRedisTTL(settings or get_settings())
