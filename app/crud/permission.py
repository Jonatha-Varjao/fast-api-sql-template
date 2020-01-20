from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db_models.models import Permission
from app.models.permission import PermissionCreate, PermissionUpdate

"""
TODO:
    - add permission
    - list all permissions
    - delete permission
    - update permission
"""


def get_permission(
    db: Session,
    *,
    permission_id: str
    ) -> Optional[Permission]:
    permission = db.query(Permission).filter( Permission.id == permission_id).first()
    return permission


def get_all(
        db: Session,
) -> List[Permission]:
    return db.query(Permission).all()


def get_all_paginated(
        db: Session,
        *,
        skip=0,
        limit=100
) -> List[Optional[Permission]]:
    return db.query(Permission).order_by(Permission.code_name).offset(skip).limit(limit).all()


def create(
        db: Session,
        *,
        permission_in: PermissionCreate,
):
    permission_in_data = jsonable_encoder(permission_in)
    permission = Permission(**permission_in_data)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def update(
        db: Session,
        *,
        permission: Permission,
        permission_in: PermissionUpdate
) -> Permission:
    permission_data = jsonable_encoder(permission)
    update_data = permission_in.dict(skip_defaults=True)
    for field in permission_data:
        if field in update_data:
            setattr(permission, field, update_data[field])
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def remove(
        db: Session,
        *,
        permission_id: str
):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    db.delete(permission)
    db.commit()
    return permission
