import json
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.utils.db import get_db
from app.core.return_messages import codes, ptBr
from app.crud.permission import (
    create,
    get_permission,
    get_all_paginated,
    remove,
    update
)
from app.models.permission import PermissionBase, PermissionInDB, PermissionUpdate

router = APIRouter()


@router.get('/permissions', response_model=List[Optional[PermissionInDB]])
async def retrieve_list(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        # is_super_user = UserIn = Depends(get_current_active_superuser)
):
    list_permissions = get_all_paginated(db, skip=skip, limit=limit)
    return list_permissions


@router.get('/permissions/{permission_id}')
async def retrieve_permission(
        *,
        db: Session = Depends(get_db),
        permission_id: str
):
    permission = get_permission(db, permission_id=permission_id)
    return permission


@router.post('/permissions', response_model=PermissionInDB)
async def create_permission(
        *,
        db: Session = Depends(get_db),
        permission_data: PermissionBase,
        # is_super_user = UserIn = Depends(get_current_active_superuser)
):
    permission = create(db, permission_in=permission_data)
    return permission


@router.put('/permissions/{permission_id}', response_model=PermissionInDB)
async def update_permission(
        *,
        db: Session = Depends(get_db),
        permission_id: str,
        permission_in: PermissionUpdate,
        # is_super_user = UserIn = Depends(get_current_active_superuser)
):
    permission = get_permission(db, permission_id=permission_id)
    if not permission:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Erro no Banco de Dados",
            "message": ptBr['ePermissionNotFound']
        }),
            status_code=404)
    permission = update(db, permission=permission, permission_in=permission_in)
    return permission


@router.delete('/permissions/{permission_id}', response_model=PermissionInDB)
async def delete_permission(
        *,
        db: Session = Depends(get_db),
        permission_id: str,
        # is_super_user = UserIn = Depends(get_current_active_superuser)
):
    permission_to_removed = get_permission(db, permission_id=permission_id)
    if not permission_to_removed:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Erro no Banco de Dados",
            "message": ptBr['ePermissionNotFound']
        }),
            status_code=404)
    permission_removed = remove(db, permission_id=permission_id)
    return Response(json.dumps({
        "messageCode": codes['success'],
        "title": "Permissão Removida",
        "message": ptBr['permissionDeleted']
    }),
        status_code=200)
