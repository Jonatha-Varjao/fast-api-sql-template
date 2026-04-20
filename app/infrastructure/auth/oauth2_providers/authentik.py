import httpx
import jwt
from jwt import PyJWKClient
from app.domain.auth.entities import OAuth2UserInfo
from app.infrastructure.auth.oauth2_providers.base import OAuth2ProviderBase
from app.config import settings


class AuthentikProvider(OAuth2ProviderBase):
    def __init__(self):
        self.server_url = settings.oauth2_server_url
        self.client_id = settings.oauth2_client_id
        self._jwks_uri = f"{self.server_url}/application/oauth2/token_keys"
        self._userinfo_endpoint = f"{self.server_url}/oauth2/userinfo"

    @property
    def provider_name(self) -> str:
        return "authentik"

    async def validate_token(self, token: str) -> OAuth2UserInfo:
        jwks_client = PyJWKClient(self._jwks_uri)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=["RS256"],
                            audience=self.client_id)
        return OAuth2UserInfo(
            sub=payload["sub"],
            email=payload.get("email"),
            username=payload.get("preferred_username"),
            full_name=payload.get("name"),
            is_superuser=payload.get("groups", []).count("admin") > 0,
            provider=self.provider_name,
            raw_info=payload,
        )
