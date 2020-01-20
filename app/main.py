import uvicorn

from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_routers
from app.core import config
from app.db.session import Session

from app.middlewares.validation_middleware import FieldValidation
from app.middlewares.db_middleware import DBConnection
from app.middlewares.db_exceptions import DBException

app = FastAPI(title=config.PROJECT_NAME, openapi_url="/api/v1/openapi.json")


# CORS
origins = []

# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
# ROUTES
app.include_router(api_routers, prefix=config.API_V1_STR)

# MIDDLEWARES
app.add_middleware(DBConnection)
app.add_middleware(DBException)
app.add_middleware(FieldValidation)
     
# Function to create a initial super_user
from app.db.init_db import init_db
from app.db.session import db_session
init_db(db_session)