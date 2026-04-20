from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json
from sqlalchemy.exc import SQLAlchemyError


class DBException(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except SQLAlchemyError as e:
            return Response(json.dumps({"messageCode": "db", "error": str(e)}), status_code=422)
