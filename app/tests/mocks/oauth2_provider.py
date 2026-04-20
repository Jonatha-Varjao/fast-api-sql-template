from app.domain.auth.entities import OAuth2UserInfo, InvalidToken


class MockOAuth2Provider:
    async def validate_token(self, token: str) -> OAuth2UserInfo:
        if token == "valid_token":
            return OAuth2UserInfo(
                sub="test-user",
                email="test@example.com",
                username="testuser",
                full_name="Test User",
                is_superuser=True,
                provider="mock",
                raw_info={},
            )
        raise InvalidToken("Invalid token")
