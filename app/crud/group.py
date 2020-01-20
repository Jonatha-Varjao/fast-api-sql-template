from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db_models.models import Group, GroupPermission
from app.models.group import Group as GroupSchema, GroupCreate, GroupUpdate, GroupPermissionSchema
from app.models.permission import PermissionBase as PermissionSchema

"""
TODO:
    - add group 
    - list all groups
    - list one group (showing all user in it) and the permissions
    - remove group
"""


def get_all_paginated(
    db: Session,
    *,
    skip=0,
    limit=100,
    environment_id: str
    ) -> List[Optional[GroupSchema]]:
    return db.query(Group).filter_by(environment_id=environment_id).offset(skip).limit(limit).all()


def get_group(
        db: Session,
        *,
        group_id: str
) -> List[Optional[GroupSchema]]:
    return db.query(Group).filter(Group.id == group_id).first()


def get_group_permissions(
        db: Session,
        *,
        group_id: str
) -> List[Optional[PermissionSchema]]:
    # grab the group
    group = db.query(Group).filter(Group.id == group_id).first()
    #
    return


def create_group(
        db: Session,
        *,
        group_in: GroupCreate
) -> Group:
    group_in_data = jsonable_encoder(group_in)
    group = Group(**group_in_data)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def remove_group(
        db: Session,
        *,
        id: str,
):
    # grab all group_permission association table and delete
    # grab all user_groups association table and delete
    # delete group 
    group = db.query(Group).filter(Group.id == id).first()
    db.delete(group)
    db.commit()

    return group


def update_group(
        db: Session,
        *,
        group: Group,
        group_in: GroupUpdate
):
    group_data = jsonable_encoder(group)
    update_data = group_in.dict(skip_defaults=True)
    
    if not group_data:
        return group
    
    for field in group_data:
        if field in update_data:
            setattr(group, field, update_data[field])
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def create_group_with_permission(
        db: Session,
        *,
        group_permission: GroupPermissionSchema  # add pydantic schema
):
    group_permission_list = []
    
    for permission in group_permission.permissions_id:
        group_id = str(group_permission.group)
        _group_permission = GroupPermission(group_id=group_id, permission_id=str(permission))
        group_permission_list.append(_group_permission)

    db.add_all(group_permission_list)
    db.commit()
    return True
