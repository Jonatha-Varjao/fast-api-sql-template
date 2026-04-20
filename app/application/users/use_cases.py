from typing import List, Optional
from app.domain.users.entities import User
from app.application.users.ports import UserRepository


async def list_users(repo: UserRepository, skip: int = 0, limit: int = 100) -> List[User]:
    return await repo.get_multi(skip=skip, limit=limit)


async def get_user(repo: UserRepository, user_id: str) -> User:
    user = await repo.get_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    return user


async def create_user(repo: UserRepository, user: User) -> User:
    existing = await repo.get_by_email(user.email)
    if existing:
        raise ValueError(f"User with email {user.email} already exists")
    return await repo.create(user)


async def update_user(repo: UserRepository, user_id: str, **kwargs) -> User:
    user = await repo.get_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    for key, value in kwargs.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    return await repo.update(user)
