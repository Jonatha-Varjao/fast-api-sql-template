from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.users.entities import User
from app.application.users.ports import UserRepository
from app.infrastructure.persistence.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(UserModel).where(UserModel.id == UUID(user_id)))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(
            select(UserModel).offset(skip).limit(limit).order_by(UserModel.full_name)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        result = await self.db.execute(select(UserModel).where(UserModel.id == UUID(user.id)))
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User {user.id} not found")
        model.full_name = user.full_name
        model.username = user.username
        model.email = user.email
        model.is_superuser = user.is_superuser
        model.is_active = user.is_active
        await self.db.commit()
        await self.db.refresh(model)
        return self._to_domain(model)

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=str(model.id),
            full_name=model.full_name,
            username=model.username,
            email=model.email,
            is_superuser=model.is_superuser,
            is_active=model.is_active,
            created_at=model.created,
            updated_at=model.updated,
        )

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=UUID(user.id) if user.id else None,
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
        )
