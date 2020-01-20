from uuid import UUID
from typing import Optional, Union, List
from pydantic import EmailStr, BaseModel, validator

from .base import Base, UUIDList


class UserBase(Base):
    username: str
    full_name: str
    email: EmailStr
    document: str
    phone_number: str
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
    document: str
    phone_number: str
    is_superuser: bool = None
    is_active: bool = None

    @validator('document')
    def validateCPF(cls, value):

        def dv_maker(v):
            if v >= 2:
                return 11 - v
            return 0
        if(len(value) == 11):
            if not value.isdigit():
                raise ValueError("CPF Inválido")

            if len(value) != 11:
                raise ValueError("CPF Inválido")

            orig_dv = value[-2:]

            new_1dv = sum([i * int(value[idx])
                           for idx, i in enumerate(range(10, 1, -1))])
            new_1dv = dv_maker(new_1dv % 11)
            value = value[:-2] + str(new_1dv) + value[-1]
            new_2dv = sum([i * int(value[idx])
                           for idx, i in enumerate(range(11, 1, -1))])
            new_2dv = dv_maker(new_2dv % 11)
            value = value[:-1] + str(new_2dv)
            if value[-2:] != orig_dv:
                raise ValueError("CPF Inválido")
            if value.count(value[0]) == 11:
                raise ValueError("CPF Inválido")
            return value
        if(len(value) == 14):

            value = ''
            if not value.isdigit():
                raise ValueError("CNPJ Inválido")

            if len(value) != 14:
                raise ValueError("CNPJ Inválido")

            orig_dv = value[-2:]

            new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(list(range(5, 1, -1)) + list(range(9, 1, -1)))])
            new_1dv = dv_maker(new_1dv % 11)
            value = value[:-2] + str(new_1dv) + value[-1]
            new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(list(range(6, 1, -1)) + list(range(9, 1, -1)))])
            new_2dv = dv_maker(new_2dv % 11)
            value = value[:-1] + str(new_2dv)
            if value[-2:] != orig_dv:
                raise ValueError("CNPJ Inválido")

            return value


class UserUpdate(Base):
    full_name: str = None
    email: EmailStr = None
    phone_number: str = None
    is_superuser: bool = None
    is_active: bool = None
    password: bool = None

# Additional properties to return via API
class User(UserBaseInDB):
    pass

class UserInDB(UserBaseInDB):
    password: str

class UserBulk(Base):
    environment: Union[str] = None
    user_data: UserCreate
    is_env_admin: bool = None
    groups: List[Union[str]] = None
    permissions: List[Union[str]] = None

class UserBulkUpdate(Base):
    user_data: Optional[UserUpdate]
    is_env_admin: Optional[bool]
    