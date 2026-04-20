from abc import ABC, abstractmethod
from app.domain.auth.entities import OAuth2UserInfo


class TokenValidator(ABC):
    @abstractmethod
    async def validate_token(self, token: str) -> OAuth2UserInfo: pass


class UserInfoFetcher(ABC):
    @abstractmethod
    async def get_userinfo(self, access_token: str) -> OAuth2UserInfo: pass
