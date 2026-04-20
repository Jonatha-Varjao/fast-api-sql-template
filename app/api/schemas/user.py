from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    username: str
    email: str
    is_superuser: bool
    is_active: bool


class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    is_superuser: bool = False
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_superuser: Optional[bool] = None
    is_active: Optional[bool] = None
