from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.users.entities import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]: pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: pass

    @abstractmethod
    async def get_multi(self, skip: int, limit: int) -> List[User]: pass

    @abstractmethod
    async def create(self, user: User) -> User: pass

    @abstractmethod
    async def update(self, user: User) -> User: pass
