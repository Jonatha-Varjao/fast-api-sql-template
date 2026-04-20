from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.application.auth.factory import get_oauth2_provider
from app.config import settings


class OAuth2Middleware(BaseHTTPMiddleware):
    PUBLIC_PATHS = ["/health", "/docs", "/redoc",
                    f"{settings.api_v1_str}/openapi.json",
                    f"{settings.api_v1_str}/login"]

    def __init__(self, app, provider=None):
        super().__init__(app)
        self.provider = provider or get_oauth2_provider()

    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(p) for p in self.PUBLIC_PATHS):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        token = auth_header[7:]
        try:
            user_info = await self.provider.validate_token(token)
            request.state.user_info = user_info
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

        return await call_next(request)
