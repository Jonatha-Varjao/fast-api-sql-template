from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json
from pydantic import ValidationError


class FieldValidation(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except ValidationError as e:
            return Response(
                json.dumps({"messageCode": "validation", "error": str(e)}),
                status_code=422,
            )
