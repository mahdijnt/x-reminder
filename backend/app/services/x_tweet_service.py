"""Tweet retrieval with original/reply/retweet/quote filtering."""

from __future__ import annotations

from app.core.config import Settings
from app.integrations.x.client import XAPIClient
from app.infrastructure.x.rate_limit_state import XRateLimitStateStore
from app.models.x.tweet import FilteredTweet
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository
from app.schemas.x.tweets import TweetItem, TweetListResponse
from app.services.x_token_service import XTokenService


class XTweetService:
    def __init__(
        self,
        settings: Settings,
        token_service: XTokenService,
        rate_limit_store: XRateLimitStateStore,
        processed_repo: ProcessedTweetRepository,
    ) -> None:
        self._settings = settings
        self._token_service = token_service
        self._rate_limit_store = rate_limit_store
        self._processed_repo = processed_repo

    @staticmethod
    def _is_original_tweet(tweet) -> bool:
        if tweet.in_reply_to_user_id:
            return False
        refs = tweet.referenced_tweets or []
        for ref in refs:
            ref_type = ref.get("type")
            if ref_type in {"retweeted", "quoted", "replied_to"}:
                return False
        return True

    def _username_map(self, includes: dict | None) -> dict[str, str]:
        users = (includes or {}).get("users") or []
        return {str(u.get("id")): str(u.get("username", "")) for u in users}

    async def fetch_user_tweets(
        self,
        app_user_id: str,
        user_id: str,
        *,
        since_id: str | None = None,
        pagination_token: str | None = None,
        record_processed: bool = False,
    ) -> TweetListResponse:
        access = await self._token_service.get_access_token(app_user_id)
        async with XAPIClient(self._settings, access_token=access, rate_limit_store=self._rate_limit_store) as client:
            response = await client.get_user_tweets(
                user_id,
                since_id=since_id,
                pagination_token=pagination_token,
            )

        usernames = self._username_map(response.includes)
        items: list[TweetItem] = []
        for tweet in response.data or []:
            if not self._is_original_tweet(tweet):
                continue
            author_id = tweet.author_id or user_id
            username = usernames.get(author_id, "")
            url = f"https://x.com/{username}/status/{tweet.id}" if username else f"https://x.com/i/web/status/{tweet.id}"
            item = TweetItem(
                tweet_id=tweet.id,
                author_id=author_id,
                username=username,
                text=tweet.text,
                created_at=tweet.created_at,
                url=url,
            )
            items.append(item)
            if record_processed:
                await self._processed_repo.touch_pending(app_user_id, tweet.id, author_id)

        next_token = response.meta.next_token if response.meta else None
        return TweetListResponse(items=items, next_token=next_token)
