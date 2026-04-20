from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: str
    full_name: str
    username: str
    email: str
    is_superuser: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
