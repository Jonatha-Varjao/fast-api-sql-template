from uuid import UUID

from typing import Optional, Union
from pydantic import BaseModel

from .base import Base

class PermissionBase(Base):
    code_name: str
    description: str
    name: str

class PermissionInDB(PermissionBase):
    id: Union[UUID]

class PermissionCreate(PermissionInDB):
    code_name: str
    description: str
    name: str

class PermissionUpdate(Base):
    name: Union[str,None]
    code_name: Union[str,None]
    description: Union[str,None]
