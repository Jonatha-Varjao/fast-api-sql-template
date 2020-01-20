from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db_models.models import User
from app.models.user import UserCreate, UserUpdate


def get(db_session: Session, user_id: str) -> Optional[User]:
    return db_session.query(User).filter(User.id == user_id).first()


def get_by_email(db_session: Session, *, email: str) -> Optional[User]:
    return db_session.query(User).filter(User.email == email).first()


def get_by_username(db_session: Session, *, username: str) -> Optional[User]:
    return db_session.query(User).filter(User.username == username).first()


def authenticate(db_session: Session, *, email_or_username: str, password: str) -> Optional[User]:
    user = get_by_email(db_session, email=email_or_username)
    if not user:
        user = get_by_username(db_session, username=email_or_username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def is_active(user) -> bool:
    return user.is_active


def is_superuser(user) -> bool:
    return user.is_superuser


def get_multi(
    db_session: Session,
    *,
    skip=0,
    limit=100,
    environment: str
    ) -> List[Optional[User]]:
    return db_session.query(User)\
        .filter(User.environments.any( Environment.id == environment ))\
        .filter_by(is_active=True)\
        .order_by(User.full_name)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
def get_all_multi(db_session: Session, *, skip=0, limit=100) -> List[Optional[User]]:
    return db_session.query(User)\
        .order_by(User.full_name)\
        .offset(skip)\
        .limit(limit)\
        .all()

def is_admin_env(db_session: Session, *, environment: str, user_id: str) -> bool:
    env_user = db_session.query(EnvUser).\
    filter_by(environment_id = environment, user_id = user_id ).first()
    if not env_user:
        return False
    return env_user.is_admin

def create(db_session: Session, *, user_in: UserCreate) -> User:
    user = User(
        **user_in.dict()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def update(db_session: Session, *, user: User, user_in: UserUpdate) -> User:
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(skip_defaults=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])
    if user_in.password:
        passwordhash = get_password_hash(user_in.password)
        user.password = passwordhash
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def deactivate_user(db_session: Session, *, user: User):
    user.is_active = False
    db_session.commit()
    db_session.refresh(user)
    return True


def check_user_permission(db_session: Session, *, user_id: str, permission_id: str) -> bool:
    has_permission = db_session.query(UserPermission)\
                        .filter(UserPermission.user_id == user_id,
                                                             UserPermission.permission_id == permission_id).first()
    if has_permission:
        return True
    return False
