"""Version 1 health endpoints."""

from fastapi import APIRouter

from app.api.v1.controllers.health_controller import HealthController
from app.core.dependencies import HealthServiceDep, RedisHealthServiceDep
from app.schemas.health import HealthData, RedisHealthData
from app.schemas.responses import APIResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=APIResponse[HealthData],
    summary="Health check",
    description="Returns service status including Redis connectivity.",
)
async def health_check(health_service: HealthServiceDep) -> APIResponse[HealthData]:
    controller = HealthController(health_service)
    return await controller.get_health()


@router.get(
    "/health/redis",
    response_model=APIResponse[RedisHealthData],
    summary="Redis health check",
    description="Returns Redis connectivity, latency, pool status, and server version.",
)
async def redis_health_check(service: RedisHealthServiceDep) -> APIResponse[RedisHealthData]:
    data = await service.get_health()
    message = "Redis is connected" if data.connected else "Redis is unavailable"
    return APIResponse.ok(data=data, message=message)
