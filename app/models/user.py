from uuid import UUID
from typing import Optional, Union, List
from pydantic import EmailStr, BaseModel, validator

from .base import Base, UUIDList


class UserBase(Base):
    username: str
    full_name: str
    email: EmailStr
    is_superuser: bool
    is_active: Optional[bool]

class UserBaseInDB(UserBase):
    id: Union[UUID,str] = None


# Properties tro receive via API on creation
class UserCreate(Base):
    username: str
    full_name: str
    email: EmailStr
    password: str
    is_superuser: bool = None
    is_active: bool = None

class UserUpdate(Base):
    full_name: str = None
    email: EmailStr = None
    is_superuser: bool = None
    is_active: bool = None
    password: bool = None

# Additional properties to return via API
class User(UserBaseInDB):
    pass

class UserInDB(UserBaseInDB):
    password: str
