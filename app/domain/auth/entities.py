from dataclasses import dataclass, field
from typing import Optional, Dict, Any

class TokenExpired(Exception): pass
class InvalidToken(Exception): pass
class ProviderError(Exception): pass
class TransientError(Exception): pass

@dataclass
class OAuth2UserInfo:
    sub: str
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_superuser: bool = False
    provider: str = ""
    raw_info: Dict[str, Any] = field(default_factory=dict)
