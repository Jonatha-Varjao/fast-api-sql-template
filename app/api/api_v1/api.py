from fastapi import APIRouter

from app.api.api_v1.endpoints.group import router as group_router
from app.api.api_v1.endpoints.environment import router as enviroment_router
from app.api.api_v1.endpoints.user import router as user_router
from app.api.api_v1.endpoints.permission import router as permission_router
from app.api.api_v1.endpoints.login import router as login_router

api_routers = APIRouter()
api_routers.include_router(login_router, tags=["Login"])
api_routers.include_router(user_router, tags=["Users"])
api_routers.include_router(group_router, tags=["Groups"])
api_routers.include_router(permission_router, tags=["Permissions"])
api_routers.include_router(enviroment_router, tags=["Environments"])