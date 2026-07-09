"""FastAPI dependency injection helpers."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.core.rate_limit import RateLimiter, get_rate_limiter
from app.infrastructure.redis.connection import RedisManager, get_redis_manager
from app.infrastructure.qdrant.connection import QdrantManager, get_qdrant_manager
from app.infrastructure.redis.session_store import SessionStore
from app.infrastructure.redis.temp_store import TempStore
from app.infrastructure.redis.user_cache import UserCache
from app.infrastructure.x.rate_limit_state import XRateLimitStateStore
from app.infrastructure.x.token_store import XTokenStore
from app.repositories.base import InMemoryRepository
from app.repositories.redis_repository import RedisRepository
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository
from app.repositories.x_profile_repository import XProfileRepository
from app.repositories.x_watch_list_repository import WatchListRepository
from app.services.analytics_service import AnalyticsService
from app.services.cache_service import CacheService
from app.services.health_service import HealthService
from app.services.redis_health_service import RedisHealthService
from app.services.watch_list_service import WatchListService
from app.services.x_oauth_service import XOAuthService
from app.services.x_profile_service import XProfileService
from app.services.x_relationship_service import XRelationshipService
from app.services.x_sync_service import XSyncService
from app.services.x_token_service import XTokenService
from app.services.x_tweet_service import XTweetService
from app.ai.recommendation_engine import StubRecommendationEngine
from app.integrations.embeddings.service import EmbeddingsService
from app.repositories.qdrant_repository import QdrantRepository
from app.services.conversation_memory_service import ConversationMemoryService
from app.services.interest_detection_service import InterestDetectionService
from app.services.relationship_scoring_service import RelationshipScoringService
from app.services.semantic_search_service import SemanticSearchService
from app.services.smart_search_service import SmartSearchService
from app.services.topic_detection_service import TopicDetectionService
from app.services.tweet_memory_service import TweetMemoryService

SettingsDep = Annotated[Settings, Depends(get_settings)]


def _manager_from_request(request: Request) -> RedisManager:
    manager = getattr(request.app.state, "redis_manager", None)
    if manager is not None:
        return manager
    return get_redis_manager()


RedisManagerDep = Annotated[RedisManager, Depends(_manager_from_request)]

def _qdrant_manager_from_request(request: Request) -> QdrantManager:
    manager = getattr(request.app.state, "qdrant_manager", None)
    if manager is not None:
        return manager
    return get_qdrant_manager()


QdrantManagerDep = Annotated[QdrantManager, Depends(_qdrant_manager_from_request)]


def _build_embeddings(settings: Settings) -> EmbeddingsService:
    return EmbeddingsService(settings)


def _build_qdrant_repository(settings: Settings, manager: QdrantManager) -> QdrantRepository:
    return QdrantRepository(settings, manager)


async def get_embeddings_service(settings: SettingsDep) -> AsyncGenerator[EmbeddingsService, None]:
    yield _build_embeddings(settings)


async def get_qdrant_repository(
    settings: SettingsDep,
    manager: QdrantManagerDep,
) -> AsyncGenerator[QdrantRepository, None]:
    yield _build_qdrant_repository(settings, manager)


async def get_semantic_search_service(
    settings: SettingsDep,
    repository: Annotated[QdrantRepository, Depends(get_qdrant_repository)],
    embeddings: Annotated[EmbeddingsService, Depends(get_embeddings_service)],
) -> AsyncGenerator[SemanticSearchService, None]:
    yield SemanticSearchService(settings, repository, embeddings)


async def get_topic_detection_service(
    settings: SettingsDep,
    embeddings: Annotated[EmbeddingsService, Depends(get_embeddings_service)],
) -> AsyncGenerator[TopicDetectionService, None]:
    yield TopicDetectionService(settings, embeddings)


async def get_smart_search_service(
    settings: SettingsDep,
    semantic: Annotated[SemanticSearchService, Depends(get_semantic_search_service)],
    topics: Annotated[TopicDetectionService, Depends(get_topic_detection_service)],
) -> AsyncGenerator[SmartSearchService, None]:
    yield SmartSearchService(settings, semantic, topics)


async def get_interest_detection_service(
    settings: SettingsDep,
    repository: Annotated[QdrantRepository, Depends(get_qdrant_repository)],
    topics: Annotated[TopicDetectionService, Depends(get_topic_detection_service)],
) -> AsyncGenerator[InterestDetectionService, None]:
    yield InterestDetectionService(settings, repository, topics)


async def get_relationship_scoring_service(settings: SettingsDep) -> AsyncGenerator[RelationshipScoringService, None]:
    yield RelationshipScoringService(settings)


async def get_tweet_memory_service(
    settings: SettingsDep,
    repository: Annotated[QdrantRepository, Depends(get_qdrant_repository)],
    embeddings: Annotated[EmbeddingsService, Depends(get_embeddings_service)],
) -> AsyncGenerator[TweetMemoryService, None]:
    yield TweetMemoryService(settings, repository, embeddings)


async def get_conversation_memory_service(
    settings: SettingsDep,
    repository: Annotated[QdrantRepository, Depends(get_qdrant_repository)],
    embeddings: Annotated[EmbeddingsService, Depends(get_embeddings_service)],
) -> AsyncGenerator[ConversationMemoryService, None]:
    yield ConversationMemoryService(settings, repository, embeddings)


async def get_recommendation_engine() -> AsyncGenerator[StubRecommendationEngine, None]:
    yield StubRecommendationEngine()



async def get_health_repository() -> AsyncGenerator[InMemoryRepository, None]:
    yield InMemoryRepository()


async def get_redis_repository(
    manager: RedisManagerDep,
) -> AsyncGenerator[RedisRepository, None]:
    yield RedisRepository(manager)


async def get_cache_service(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[CacheService, None]:
    yield CacheService(repository)


async def get_session_store(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[SessionStore, None]:
    yield SessionStore(repository)


async def get_user_cache(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[UserCache, None]:
    yield UserCache(repository)


async def get_temp_store(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[TempStore, None]:
    yield TempStore(repository)


RedisRepositoryDep = Annotated[RedisRepository, Depends(get_redis_repository)]
TempStoreDep = Annotated[TempStore, Depends(get_temp_store)]


async def get_x_token_store(
    repository: RedisRepositoryDep,
    settings: SettingsDep,
) -> AsyncGenerator[XTokenStore, None]:
    yield XTokenStore(repository, settings)


async def get_x_rate_limit_store(
    repository: RedisRepositoryDep,
) -> AsyncGenerator[XRateLimitStateStore, None]:
    yield XRateLimitStateStore(repository)


async def get_x_profile_repository(
    repository: RedisRepositoryDep,
) -> AsyncGenerator[XProfileRepository, None]:
    yield XProfileRepository(repository)


async def get_watch_list_repository(
    repository: RedisRepositoryDep,
) -> AsyncGenerator[WatchListRepository, None]:
    yield WatchListRepository(repository)


async def get_processed_tweet_repository(
    repository: RedisRepositoryDep,
) -> AsyncGenerator[ProcessedTweetRepository, None]:
    yield ProcessedTweetRepository(repository)


async def get_x_token_service(
    settings: SettingsDep,
    token_store: Annotated[XTokenStore, Depends(get_x_token_store)],
) -> AsyncGenerator[XTokenService, None]:
    yield XTokenService(settings, token_store)


async def get_x_oauth_service(
    settings: SettingsDep,
    temp_store: TempStoreDep,
    token_store: Annotated[XTokenStore, Depends(get_x_token_store)],
) -> AsyncGenerator[XOAuthService, None]:
    yield XOAuthService(settings, temp_store, token_store)


async def get_x_profile_service(
    settings: SettingsDep,
    token_service: Annotated[XTokenService, Depends(get_x_token_service)],
    profile_repository: Annotated[XProfileRepository, Depends(get_x_profile_repository)],
    rate_limit_store: Annotated[XRateLimitStateStore, Depends(get_x_rate_limit_store)],
) -> AsyncGenerator[XProfileService, None]:
    yield XProfileService(settings, token_service, profile_repository, rate_limit_store)


async def get_x_relationship_service(
    settings: SettingsDep,
    token_service: Annotated[XTokenService, Depends(get_x_token_service)],
    rate_limit_store: Annotated[XRateLimitStateStore, Depends(get_x_rate_limit_store)],
) -> AsyncGenerator[XRelationshipService, None]:
    yield XRelationshipService(settings, token_service, rate_limit_store)


async def get_x_tweet_service(
    settings: SettingsDep,
    token_service: Annotated[XTokenService, Depends(get_x_token_service)],
    rate_limit_store: Annotated[XRateLimitStateStore, Depends(get_x_rate_limit_store)],
    processed_repo: Annotated[ProcessedTweetRepository, Depends(get_processed_tweet_repository)],
) -> AsyncGenerator[XTweetService, None]:
    yield XTweetService(settings, token_service, rate_limit_store, processed_repo)


async def get_watch_list_service(
    repository: Annotated[WatchListRepository, Depends(get_watch_list_repository)],
) -> AsyncGenerator[WatchListService, None]:
    yield WatchListService(repository)


async def get_analytics_service(
    settings: SettingsDep,
    profile_repository: Annotated[XProfileRepository, Depends(get_x_profile_repository)],
    watch_list_repository: Annotated[WatchListRepository, Depends(get_watch_list_repository)],
) -> AsyncGenerator[AnalyticsService, None]:
    yield AnalyticsService(settings, profile_repository, watch_list_repository)


async def get_x_sync_service(
    settings: SettingsDep,
    token_service: Annotated[XTokenService, Depends(get_x_token_service)],
    profile_service: Annotated[XProfileService, Depends(get_x_profile_service)],
    relationship_service: Annotated[XRelationshipService, Depends(get_x_relationship_service)],
    profile_repository: Annotated[XProfileRepository, Depends(get_x_profile_repository)],
    watch_list_repository: Annotated[WatchListRepository, Depends(get_watch_list_repository)],
) -> AsyncGenerator[XSyncService, None]:
    yield XSyncService(
        settings,
        token_service,
        profile_service,
        relationship_service,
        profile_repository,
        watch_list_repository,
    )


def _monitoring_engine_from_request(request: Request):
    return getattr(request.app.state, "monitoring_engine", None)


def _notification_engine_from_request(request: Request):
    return getattr(request.app.state, "notification_engine", None)


async def get_health_service(
    request: Request,
    settings: SettingsDep,
    repository: Annotated[InMemoryRepository, Depends(get_health_repository)],
    manager: RedisManagerDep,
    qdrant_manager: QdrantManagerDep,
) -> AsyncGenerator[HealthService, None]:
    yield HealthService(
        settings=settings,
        repository=repository,
        redis_manager=manager,
        monitoring_engine=_monitoring_engine_from_request(request),
        notification_engine=_notification_engine_from_request(request),
        qdrant_manager=qdrant_manager,
    )


async def get_rate_limiter_dep(
    settings: SettingsDep,
    manager: RedisManagerDep,
) -> AsyncGenerator[RateLimiter, None]:
    yield get_rate_limiter(settings, redis_manager=manager)


async def get_redis_health_service(
    settings: SettingsDep,
    manager: RedisManagerDep,
) -> AsyncGenerator[RedisHealthService, None]:
    yield RedisHealthService(settings, manager)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
RedisHealthServiceDep = Annotated[RedisHealthService, Depends(get_redis_health_service)]
RedisRepositoryDep = Annotated[RedisRepository, Depends(get_redis_repository)]
CacheServiceDep = Annotated[CacheService, Depends(get_cache_service)]
SessionStoreDep = Annotated[SessionStore, Depends(get_session_store)]
UserCacheDep = Annotated[UserCache, Depends(get_user_cache)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter_dep)]

XOAuthServiceDep = Annotated[XOAuthService, Depends(get_x_oauth_service)]
XProfileServiceDep = Annotated[XProfileService, Depends(get_x_profile_service)]
XRelationshipServiceDep = Annotated[XRelationshipService, Depends(get_x_relationship_service)]
XTweetServiceDep = Annotated[XTweetService, Depends(get_x_tweet_service)]
WatchListServiceDep = Annotated[WatchListService, Depends(get_watch_list_service)]
XSyncServiceDep = Annotated[XSyncService, Depends(get_x_sync_service)]
AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]


EmbeddingsServiceDep = Annotated[EmbeddingsService, Depends(get_embeddings_service)]
QdrantRepositoryDep = Annotated[QdrantRepository, Depends(get_qdrant_repository)]
SemanticSearchServiceDep = Annotated[SemanticSearchService, Depends(get_semantic_search_service)]
TopicDetectionServiceDep = Annotated[TopicDetectionService, Depends(get_topic_detection_service)]
SmartSearchServiceDep = Annotated[SmartSearchService, Depends(get_smart_search_service)]
InterestDetectionServiceDep = Annotated[InterestDetectionService, Depends(get_interest_detection_service)]
RelationshipScoringServiceDep = Annotated[RelationshipScoringService, Depends(get_relationship_scoring_service)]
TweetMemoryServiceDep = Annotated[TweetMemoryService, Depends(get_tweet_memory_service)]
ConversationMemoryServiceDep = Annotated[ConversationMemoryService, Depends(get_conversation_memory_service)]
RecommendationEngineDep = Annotated[StubRecommendationEngine, Depends(get_recommendation_engine)]
