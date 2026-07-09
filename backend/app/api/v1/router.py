"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth_x, health, watch_lists, x_profile

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth_x.router)
api_router.include_router(x_profile.router)
api_router.include_router(watch_lists.router)
