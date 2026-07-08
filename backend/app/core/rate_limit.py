"""Rate limiting structure (placeholder; no Redis backend)."""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from time import monotonic

from fastapi import Request

from app.core.config import Settings


@dataclass
class RateLimitState:
    """In-memory sliding window counters per client key."""

    windows: dict[str, deque[float]] = field(default_factory=lambda: defaultdict(deque))


class RateLimiter:
    """Placeholder rate limiter for future Redis-backed implementation."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._state = RateLimitState()

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def is_allowed(self, request: Request) -> bool:
        if not self._settings.RATE_LIMIT_ENABLED:
            return True

        key = self._client_key(request)
        now = monotonic()
        window = self._settings.RATE_LIMIT_WINDOW_SECONDS
        limit = self._settings.RATE_LIMIT_REQUESTS
        bucket = self._state.windows[key]

        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            return False

        bucket.append(now)
        return True


def get_rate_limiter(settings: Settings) -> RateLimiter:
    return RateLimiter(settings)
