from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.user import UserSchema, UserCreate, UserUpdate
from app.api.endpoints.auth.dependencies import require_superuser
from app.domain.auth.entities import OAuth2UserInfo
from app.domain.users.entities import User
from app.application.users.use_cases import list_users, get_user, create_user, update_user
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.user_repository import SQLAlchemyUserRepository

router = APIRouter()


@router.get("/users", response_model=list[UserSchema])
async def list_users_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: OAuth2UserInfo = Depends(require_superuser),
    skip: int = 0,
    limit: int = 100,
):
    repo = SQLAlchemyUserRepository(db)
    return await list_users(repo, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_endpoint(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: OAuth2UserInfo = Depends(require_superuser),
):
    repo = SQLAlchemyUserRepository(db)
    try:
        return await get_user(repo, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/users", response_model=UserSchema, status_code=201)
async def create_user_endpoint(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: OAuth2UserInfo = Depends(require_superuser),
):
    repo = SQLAlchemyUserRepository(db)
    user = User(
        id="",
        full_name=user_data.full_name,
        username=user_data.username,
        email=user_data.email,
        is_superuser=user_data.is_superuser,
        is_active=user_data.is_active,
    )
    try:
        return await create_user(repo, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user_endpoint(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: OAuth2UserInfo = Depends(require_superuser),
):
    repo = SQLAlchemyUserRepository(db)
    try:
        updated = await update_user(
            repo, user_id,
            full_name=user_data.full_name,
            email=user_data.email,
            is_superuser=user_data.is_superuser,
            is_active=user_data.is_active,
        )
        return updated
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/users/{user_id}", status_code=204)
async def delete_user_endpoint(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: OAuth2UserInfo = Depends(require_superuser),
):
    # Delete functionality would go here
    pass
