from fastapi import FastAPI
from sqlalchemy.schema import MetaData

from app.core.config import DATABASE_CONFIG

app: FastAPI = FastAPI()

from app.db.base import Base
db = Base.metadata
