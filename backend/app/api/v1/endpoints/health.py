"""Version 1 health endpoints."""

from fastapi import APIRouter

from app.api.v1.controllers.health_controller import HealthController
from app.core.dependencies import HealthServiceDep
from app.schemas.health import HealthData
from app.schemas.responses import APIResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=APIResponse[HealthData],
    summary="Health check",
    description="Returns service status without external dependencies.",
)
async def health_check(health_service: HealthServiceDep) -> APIResponse[HealthData]:
    controller = HealthController(health_service)
    return await controller.get_health()
