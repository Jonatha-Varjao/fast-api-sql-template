from fastapi import APIRouter

from app.api.api_v1.endpoints.user import router as user_router
from app.api.api_v1.endpoints.login import router as login_router

api_routers = APIRouter()
api_routers.include_router(login_router, tags=["Login"])
api_routers.include_router(user_router, tags=["Users"])