from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints.auth.login import router as auth_router
from app.api.endpoints.users.user import router as users_router
from app.api.endpoints.websocket import router as websocket_router
from app.config import settings
from app.middleware.db_exceptions import DBException
from app.middleware.validation import FieldValidation
from app.middleware.auth import OAuth2Middleware
from app.infrastructure.persistence.database import async_engine
from app.infrastructure.cache.redis_client import redis_client
from app.application.auth.factory import get_oauth2_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()
    yield
    await redis_client.disconnect()
    await async_engine.dispose()


app = FastAPI(title=settings.project_name, openapi_url=f"{settings.api_v1_str}/openapi.json", lifespan=lifespan)

origins = [o.strip() for o in settings.backend_cors_origins.split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.add_middleware(DBException)
app.add_middleware(FieldValidation)
app.add_middleware(OAuth2Middleware, provider=get_oauth2_provider())

app.include_router(auth_router, prefix=settings.api_v1_str)
app.include_router(users_router, prefix=settings.api_v1_str)
app.include_router(websocket_router, prefix=settings.api_v1_str)
