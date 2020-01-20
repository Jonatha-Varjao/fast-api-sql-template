from pydantic import BaseModel
from typing import Union
from uuid import UUID

from .user import UserBaseInDB

class Token(BaseModel):
    access_token: str = None
    token_type: str = None


class TokenPayload(BaseModel):
    user_data: UserBaseInDB
    environment: Union[UUID,str] = None


class LoginOAuth(BaseModel):
    grant_type: str = None
    username: str
    password: str
    client_id: str = None
    client_secret: str = None