import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.utils.db import get_db
from app.api.utils.security import check_superuser_or_admin, get_environment_from_token
from app.core.return_messages import codes, ptBr
from app.db_models.models import Group as GroupDB, GroupPermission
from app.models.group import GroupBulk, GroupList, GroupPermissionSchema, GroupListInfo, GroupUpdateList, UUIDList
from app.models.user import UserInDB

from app.crud.group import (
    create_group,
    create_group_with_permission,
    get_group,
    get_all_paginated,
    update_group
)

from app.crud.permission import (
    get_permission
)

from app.crud.permission import (
    get_permission,
)

router = APIRouter()

@router.delete(
    "/groups/{group_id}/permissions/{permission_id}"
)
async def remove_group_permission(
    db: Session = Depends(get_db),
    *,
    group_id: str,
    permission_id: str,
    current_user: UserInDB = Depends(check_superuser_or_admin)
):
    permission = get_permission(db, permission_id=permission_id)
    
    if not permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['ePermissionNotFound']
        }),
            status_code=422) 

    group_permission = db.query(GroupPermission)\
    .filter(
        GroupPermission.group_id == str(group_id), 
        GroupPermission.permission_id == str(permission_id) 
    ).first()

    if not group_permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eGroupPermissionNotFound']
        }),
            status_code=422) 

    db.delete(group_permission)
    db.commit()

    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na remoção de Permissão no Grupo",
            "message": ptBr['groupPermissionDeleted']
        }),
            status_code=200) 

@router.post(
    '/groups/{group_id}/permissions/{permission_id}'
)
async def add_group_permission(
    db: Session = Depends(get_db),
    *,
    group_id: str,
    permission_id: str,
    current_user: UserInDB = Depends(check_superuser_or_admin)
):
    permission = get_permission(db, permission_id=permission_id)
    
    if not permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['ePermissionNotFound']
        }),
            status_code=404) 

    group_permission = db.query(GroupPermission)\
    .filter(
        GroupPermission.group_id == str(group_id), 
        GroupPermission.permission_id == str(permission_id) 
    ).first()
    
    if group_permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eGroupPermissionFound']
        }),
            status_code=422) 
    
    group_permission = GroupPermission(group_id=group_id, permission_id=permission_id)
    db.add(group_permission)
    db.commit()

    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na adesão de Permissão no Grupo",
            "message": ptBr['groupPermissionAdded']
        }),
            status_code=200) 

@router.post(
    '/groups',
    summary="Criar Grupo com Permissoes"
)
async def create_group_endpoint(
        db: Session = Depends(get_db),
        *,
        group_bulk: GroupBulk,
        environment: str = Depends(get_environment_from_token),
        current_user: UserInDB = Depends(check_superuser_or_admin)
):
    group_in = group_bulk.group_data
    group_in.environment_id = environment
    # crio o grupo 
    group_create = create_group(db, group_in=group_in)

    if group_bulk.list_permissions:
        group_permission_data = GroupPermissionSchema(
            group=group_create.id,
            permissions_id=group_bulk.list_permissions
            )
        group_permissions = create_group_with_permission(db, group_permission=group_permission_data)

    return group_create


@router.get(
    '/groups',
    summary="Listar Grupos"
)
async def list_groups_paginated(
        db: Session = Depends(get_db),
        *,
        skip: int = 0,
        limit: int = 100,
        environment: str = Depends(get_environment_from_token),
        current_user: UserInDB = Depends(check_superuser_or_admin)
):
    groups = get_all_paginated(db, skip=skip, limit=limit, environment_id=environment)

    for i in range(len(groups)):
        for j in range(len(groups[i].permissions)):
            groups[i].permissions[j].permission

    return groups


@router.get(
    '/groups/{group_id}',
    # response_model=GroupListInfo,
    summary="Listar o Grupo e suas Permissões"
)
async def list_group(
    db: Session = Depends(get_db),
    *,
    group_id: str,
    environment: str = Depends(get_environment_from_token),
    current_user: UserInDB = Depends(check_superuser_or_admin)
):
    group = get_group(db, group_id=group_id)
    if not group:
       return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eGroupNotFound']
        }),
            status_code=404) 
    [ group.permissions[i].permission for i in range(len(group.permissions)) ]
    [ group.users[i].user for i in range(len(group.users)) ] 
    return group


@router.put(
    '/groups/{group_id}',
    summary="Atualizar Grupo"
)
async def update_group_endpoint(
        db: Session = Depends(get_db),
        *,
        group_id: str,
        group_update: GroupUpdateList,
        current_user: UserInDB = Depends(check_superuser_or_admin)
):
    # find group
    group = get_group(db, group_id=group_id)
    
    if not group:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eGroupNotFound']
        }),
            status_code=404)
    
    # CHECO SE TEM DADO PRA ATUALIZAR NO GRUPO
    if group_update.group:
        group = update_group(db, group=group, group_in=group_update.group)

    
    db.commit()
    db.refresh(group)
    [ group.permissions[i].permission for i in range(len(group.permissions)) ]
    [ group.users[i].user for i in range(len(group.users)) ] 
    return group


@router.delete(
    '/groups/{group_id}',
    summary="Remover Grupo"
)
async def remove_group(
        db: Session = Depends(get_db),
        *,
        group_id: str,
        current_user: UserInDB = Depends(check_superuser_or_admin)
):
    group = get_group(db, group_id=group_id)
    
    if not group:
       return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eGroupNotFound']
        }),
            status_code=404)
    
    db.delete(group)
    db.commit()
    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na Operação.",
            "message": ptBr['groupDeleted']
        }),
            status_code=200)

@router.post(
    '/groups/delete-list',
    summary="Remover Lista de Grupos"
)
async def remove_list_group(
    db: Session = Depends(get_db),
    *,
    list_group: UUIDList,
    current_user: UserInDB = Depends(check_superuser_or_admin)
):
    
    groups = db.query(GroupDB).filter(GroupDB.id.in_(
        list_group.id_list
    )).all()
    
    if len(groups) is not len(list_group.id_list):
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação dos Dados",
            "message": ptBr['eGroupNotFound']
        }),
            status_code=422)

    [ db.delete(group) for group in groups ]

    db.commit()
    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na Operação.",
            "message": ptBr['groupsDeleted']
        }),
            status_code=200)
