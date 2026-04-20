from abc import ABC, abstractmethod
from app.domain.auth.entities import OAuth2UserInfo


class OAuth2ProviderBase(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: pass

    @abstractmethod
    async def validate_token(self, token: str) -> OAuth2UserInfo: pass

    @property
    def jwks_uri(self) -> str | None:
        return None

    @property
    def userinfo_endpoint(self) -> str | None:
        return None
