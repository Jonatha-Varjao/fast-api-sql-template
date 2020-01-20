from uuid import UUID

from typing import Optional, Union
from pydantic import BaseModel

from .base import Base


class Environment(Base):
    id: UUID
    name: str


class EnvironmentCreateIn(BaseModel):
    name: str


class EnvironmentUpdateIn(BaseModel):
    name: Optional[str]

