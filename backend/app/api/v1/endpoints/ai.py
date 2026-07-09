"""AI / vector search endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.dependencies import (
    AccountMemoryServiceDep,
    InterestDetectionServiceDep,
    RelationshipScoringServiceDep,
    SimilaritySearchServiceDep,
    SmartSearchServiceDep,
    TopicDetectionServiceDep,
    TweetMemoryServiceDep,
    RecommendationEngineDep,
)
from app.schemas.ai import (
    AccountStoreRequest,
    InterestProfile,
    RecommendationsResponse,
    RelationshipScore,
    SearchResponse,
    SearchType,
    SimilarityResponse,
    TopicResult,
    TweetStoreRequest,
)
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/search", response_model=APIResponse[SearchResponse])
async def ai_search(
    service: SmartSearchServiceDep,
    q: str = Query(min_length=1),
    type: SearchType = SearchType.ALL,
    user_id: str | None = None,
    limit: int = Query(default=10, ge=1, le=50),
    score_threshold: float | None = None,
):
    data = await service.search(
        q,
        search_type=type,
        user_id=user_id,
        limit=limit,
        score_threshold=score_threshold,
    )
    return APIResponse.ok(data=data)


@router.get("/interests/{user_id}", response_model=APIResponse[InterestProfile])
async def get_user_interests(user_id: str, service: InterestDetectionServiceDep):
    profile = await service.get_interests(user_id)
    return APIResponse.ok(data=profile)


@router.get("/topics", response_model=APIResponse[TopicResult])
async def detect_topics(service: TopicDetectionServiceDep, text: str = Query(min_length=1)):
    topics = await service.detect_topics(text)
    return APIResponse.ok(data=TopicResult(text=text, topics=topics))


@router.get("/relationship-score", response_model=APIResponse[RelationshipScore])
async def relationship_score(
    service: RelationshipScoringServiceDep,
    user_id: str = Query(min_length=1),
    account_id: str = Query(min_length=1),
):
    score = await service.score_relationship(user_id, account_id)
    return APIResponse.ok(data=score)


@router.post("/tweets/store", response_model=APIResponse[dict])
async def store_tweet_embedding(body: TweetStoreRequest, service: TweetMemoryServiceDep):
    await service.store_tweet(body)
    return APIResponse.ok(data={"stored": True, "tweet_id": body.tweet_id})




@router.get("/similar", response_model=APIResponse[SimilarityResponse])
async def similar_search(
    service: SimilaritySearchServiceDep,
    q: str = Query(min_length=1),
    target: SearchType = SearchType.TWEETS,
    user_id: str | None = None,
    limit: int = Query(default=10, ge=1, le=50),
    score_threshold: float | None = None,
):
    data = await service.find_similar(
        q,
        target=target,
        user_id=user_id,
        limit=limit,
        score_threshold=score_threshold,
    )
    return APIResponse.ok(data=data)


@router.post("/accounts/store", response_model=APIResponse[dict])
async def store_account_embedding(body: AccountStoreRequest, service: AccountMemoryServiceDep):
    await service.store_account(body)
    return APIResponse.ok(data={"stored": True, "user_id": body.user_id})


@router.get("/recommendations/{user_id}", response_model=APIResponse[RecommendationsResponse])
async def get_recommendations(user_id: str, engine: RecommendationEngineDep, limit: int = Query(default=10, ge=1, le=50)):
    items = await engine.recommend(user_id, limit=limit)
    return APIResponse.ok(data=RecommendationsResponse(user_id=user_id, items=items, source="stub"))