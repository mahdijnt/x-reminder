"""Tweet retrieval with original/reply/retweet/quote filtering."""

from __future__ import annotations

from app.core.config import Settings
from app.integrations.x.client import XAPIClient
from app.infrastructure.x.rate_limit_state import XRateLimitStateStore
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
    def _tweet_flags(tweet) -> tuple[bool, bool, bool]:
        is_reply = bool(tweet.in_reply_to_user_id)
        is_retweet = False
        is_quote = False
        for ref in tweet.referenced_tweets or []:
            ref_type = ref.get("type")
            if ref_type == "retweeted":
                is_retweet = True
            elif ref_type == "quoted":
                is_quote = True
            elif ref_type == "replied_to":
                is_reply = True
        return is_reply, is_retweet, is_quote

    @classmethod
    def _include_tweet(
        cls,
        tweet,
        *,
        include_replies: bool,
        include_retweets: bool,
        include_quotes: bool,
        original_only: bool,
    ) -> bool:
        is_reply, is_retweet, is_quote = cls._tweet_flags(tweet)
        is_original = not is_reply and not is_retweet and not is_quote
        if original_only:
            return is_original
        if is_reply and not include_replies:
            return False
        if is_retweet and not include_retweets:
            return False
        if is_quote and not include_quotes:
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
        include_replies: bool = False,
        include_retweets: bool = False,
        include_quotes: bool = False,
        original_only: bool = True,
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
            if not self._include_tweet(
                tweet,
                include_replies=include_replies,
                include_retweets=include_retweets,
                include_quotes=include_quotes,
                original_only=original_only,
            ):
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
                await self._processed_repo.touch_pending(
                    app_user_id,
                    tweet.id,
                    author_id,
                    username=username or None,
                    url=url,
                    tweet_created_at=tweet.created_at,
                )

        next_token = response.meta.next_token if response.meta else None
        return TweetListResponse(items=items, next_token=next_token)
