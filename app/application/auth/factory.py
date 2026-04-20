from app.config import settings
from app.infrastructure.auth.oauth2_providers.base import OAuth2ProviderBase


def get_oauth2_provider() -> OAuth2ProviderBase:
    if settings.oauth2_provider == "keycloak":
        from app.infrastructure.auth.oauth2_providers.keycloak import KeycloakProvider
        return KeycloakProvider()
    elif settings.oauth2_provider == "auth0":
        from app.infrastructure.auth.oauth2_providers.auth0 import Auth0Provider
        return Auth0Provider()
    elif settings.oauth2_provider == "okta":
        from app.infrastructure.auth.oauth2_providers.okta import OktaProvider
        return OktaProvider()
    elif settings.oauth2_provider == "authentik":
        from app.infrastructure.auth.oauth2_providers.authentik import AuthentikProvider
        return AuthentikProvider()
    elif settings.oauth2_provider == "zitadel":
        from app.infrastructure.auth.oauth2_providers.zitadel import ZitadelProvider
        return ZitadelProvider()
    raise ValueError(f"Unknown OAUTH2_PROVIDER: {settings.oauth2_provider}")
