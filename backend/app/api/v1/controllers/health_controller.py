"""Thin controller delegating to HealthService."""

from app.schemas.health import HealthData
from app.schemas.responses import APIResponse
from app.services.health_service import HealthService


class HealthController:
    def __init__(self, health_service: HealthService) -> None:
        self._health_service = health_service

    async def get_health(self) -> APIResponse[HealthData]:
        data = await self._health_service.get_health()
        if data.status == "degraded":
            return APIResponse.ok(data=data, message="Service is degraded")
        return APIResponse.ok(data=data, message="Service is healthy")
