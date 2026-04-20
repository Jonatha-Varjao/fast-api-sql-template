from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class DomainEvent:
    event_id: str
    event_type: str
    occurred_at: datetime
    metadata: Dict[str, Any]

@dataclass
class UserCreatedEvent(DomainEvent):
    user_id: str
    username: str
    email: str

@dataclass
class UserUpdatedEvent(DomainEvent):
    user_id: str
    changes: Dict[str, Any]

@dataclass
class UserDeletedEvent(DomainEvent):
    user_id: str
