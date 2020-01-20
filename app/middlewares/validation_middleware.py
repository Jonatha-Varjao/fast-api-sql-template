import json

from googletrans import Translator
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.return_messages import codes

translator = Translator()


class FieldValidation(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response

        except ValidationError as error:
            error_json = error.json()
            error_json_pt = translator.translate(error_json, dest='pt')
            return Response(json.dumps({
                        "messageCode": codes['validation'], 
                        "title": "Validation Error", 
                        "message": error_json_pt.text
                    }),
                        status_code=422)
