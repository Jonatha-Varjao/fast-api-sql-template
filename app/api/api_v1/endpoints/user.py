import json

from fastapi import APIRouter, Depends
from googletrans import Translator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.utils.db import get_db
from app.api.utils.security import check_superuser_or_admin, get_environment_from_token
from app.core.return_messages import codes, ptBr
from app.core.security import get_password_hash
from app.models.user import User as UserSchema, UserInDB, UserBulk, UserUpdate, UserCreate, UserBulkUpdate, UUIDList
from app.db_models.models import User, EnvUser, UserGroup, UserPermission, Group, Permission
from app.crud.user import (
    get,
    is_active,
    get_multi,
    update,
    deactivate_user,
    is_admin_env
)

router = APIRouter()
translator = Translator()


@router.get(
    '/users/has-permission/{permission_id}',
    summary="Verificar se Usuario tem Permissao"
)
async def has_permission(
        *,
        user_id: str,
        permission_id: str,
        db: Session = Depends(get_db),
        environment: str = Depends(get_environment_from_token),
        #user: str = Depends(get_user_from_token)
):
    # grab user
    # check if it's superuser -> True
    # check = check_user_permission(db, user_id, permission_id)
    # if not check:
    #     return False
    
    return True


@router.get(
    '/users/{user_id}'
)
async def retrieve_user(
        user_id,
        db: Session = Depends(get_db),
        environment: str = Depends(get_environment_from_token),
        current_user: UserInDB = Depends(check_superuser_or_admin)
):
    print(environment)
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Erro no Banco de Dados",
            "message": ptBr['eUserNotFound']
        }),
            status_code=400)
    
    for i in range(len(user.permissions)):
        user.permissions[i].permission

    for i in range(len(user.groups)):
        user.groups[i].group

    return user


@router.get(
    '/users/user-permissions-groups/{user_id}',
    summary="Listar Usuario com os seus Grupos e Permissiões"
)
async def retrieve_full_user(
        user_id,
        db: Session = Depends(get_db),
        # environment: str = Depends(get_environment_from_token)
):
    user = get(db, str(user_id))
    if not user:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Erro no Banco de Dados",
            "message": ptBr['eUserNotFound']
        }),
            status_code=404)
    if is_active(user):
        groups = user.groups
        # print(groups[0].group)
        user.environments
        user.permissions
        return user
    else:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Erro no Banco de Dados",
            "message": ptBr['eUserNotActive']
        }),
            status_code=404)


@router.get(
    '/users'
)
async def list_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        environment: str = Depends(get_environment_from_token),
        current_user: UserInDB = Depends(check_superuser_or_admin)
):
    users = get_multi(db, skip=skip, limit=limit, environment=environment)
    if not users:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Dados inexistentes",
            "message": ptBr['eNotAnyUsers']
        }),
            status_code=404)
    
    for i in range(len(users)):
        for j in range(len(users[i].permissions)):
            users[i].permissions[j].permission

    for i in range(len(users)):
        for j in range(len(users[i].groups)):
            users[i].groups[j].group

    return users


@router.post(
    '/users',
    response_model=UserSchema
)
async def create_user(
        data: UserBulk,
        db: Session = Depends(get_db),
        current_user: UserInDB = Depends(check_superuser_or_admin),
        environment: str = Depends(get_environment_from_token)
):
    new_user = data.user_data
    new_user_permissions = data.permissions
    new_user_groups = data.groups
    new_user_environment = environment

    # Creating and saving User
    new_user.password = get_password_hash(new_user.password)
    user_validated = UserCreate(**new_user.dict())
    user = User(
        **user_validated.dict()
    )
    db.add(user)
    db.commit()
    # Creating relations between User and Environment
    if new_user_environment:
        try:
            # Creating relations between User and Environment
            user_env = EnvUser(
                environment_id=str(new_user_environment),
                user_id=str(user.id),
                is_admin=data.is_env_admin,
                extra_data="Teste de relacao endpoint.")
            db.add(user_env)
        except IntegrityError as error:
            return Response(json.loads({"messageCode": codes['db'],
                                        "title": "Erro no Banco de Dados", "error": error.orig}), status_code=422)
    # Creating relations between User and Permission
    if new_user_permissions:
        for permission_id in new_user_permissions:
            try:
                print(f'PERMISSIONS {permission_id}')
                user_permission = UserPermission(permission_id=str(permission_id), user_id=str(user.id),
                                                 extra_data="Teste de relacao endpoint")
                db.add(user_permission)
            except IntegrityError as error:
                return Response(json.loads({"messageCode": codes['db'],
                                            "title": "Erro no Banco de Dados", "error": error.orig}), status_code=422)
    # Creating relations between User and Group
    if new_user_groups:
        for group_id in new_user_groups:
            try:
                print(f'GROUPS {group_id}')
                user_group = UserGroup(group_id=str(group_id), user_id=str(user.id),
                                       extra_data="Teste de relacao endpoint")
                db.add(user_group)
            except IntegrityError as error:
                return Response(json.loads({"messageCode": codes['db'],
                                            "title": "Erro no Banco de Dados", "error": error.orig}), status_code=50)
    # Saving on database
    db.commit()
    db.refresh(user)

    return user


@router.put(
    '/users/{user_id}',
    response_model=UserSchema
)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: str,
        user_in: UserBulkUpdate,
        environment: str = Depends(get_environment_from_token),
        current_user: UserInDB = Depends(check_superuser_or_admin),
):
    """
    Update a user.
    """
    user = get(db, user_id=user_id)
    if not user:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Erro no Banco de Dados",
            "message": ptBr['eUserNotFound']
        }),
            status_code=404)
    if not user.is_active:
        return Response(json.dumps({
            "messageCode": codes['db'],
            "title": "Erro no Banco de Dados",
            "message": ptBr['eUserNotActive']
        }),
            status_code=404)
    if user.is_active:
        
        user = update(db, user=user, user_in=user_in.user_data)
        return user


@router.delete(
    '/users/{user_id}',
)
def delete_user(
        *,
        db: Session = Depends(get_db),
        user_id: str,
        current_user: UserInDB = Depends(check_superuser_or_admin),
        environment: str = Depends(get_environment_from_token)
):
    if current_user.is_superuser or is_admin_env(db, environment = environment, user_id = str(current_user.id)):
        user = get(db, user_id=user_id)
        if not user.is_active:
            return Response(json.dumps({
                "messageCode": codes['validation'],
                "title": "Usuario já desativado.",
                "message": ptBr['eAlreadyDelete']
            }),
                status_code=200)
        deactivating_user = deactivate_user(db, user=user)
        if deactivating_user:
            return Response(json.dumps({
                "messageCode": codes['success'],
                "title": "Sucesso na Operação.",
                "message": ptBr['userDeleted']
            }),
                status_code=200)
        else:
            
            return Response(json.dumps({
                "messageCode": codes['db'],
                "title": "Erro no Banco de Dados",
                "message": ptBr['eNotDeleteUser']
            }),
                status_code=404)
    else:
        return Response(json.dumps({
            "messageCode": codes['authorization'],
            "title": "Erro de Autorização",
            "message": ptBr['eNotAuthorized']
        }),
            status_code=401)


@router.delete(
    '/users/{user_id}/groups/{group_id}'
)
async def remove_group(
    db: Session = Depends(get_db),
    *,
    user_id: str,
    group_id: str,
    current_user: UserInDB = Depends(check_superuser_or_admin),
):
    # checo se o grupo existe
    group = db.query(Group).filter_by(id=group_id).first()

    if not group:
        # GRUPO NAO EXISTE
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eGroupNotFound']
        }),
            status_code=422) 
    
    # checo se o user ja tem esse grupo
    user_group = db.query(UserGroup)\
    .filter(
        UserGroup.group_id == group_id,
        UserGroup.user_id == user_id
    ).first()
    if not user_group:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eUserNotInGroup']
        }),
            status_code=422) 

    db.delete(user_group)
    db.commit()
    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na remoção do Grupo no Usuário",
            "message": ptBr['userGroupDeleted']
        }),
            status_code=200) 


@router.post(
    '/users/{user_id}/groups/{group_id}'
)
async def add_group(
    db: Session = Depends(get_db),
    *,
    user_id: str,
    group_id: str,
    current_user: UserInDB = Depends(check_superuser_or_admin),
):
    # checo se o grupo existe
    group = db.query(Group).filter_by(id=group_id).first()

    if not group:
        # GRUPO NAO EXISTE
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eGroupNotFound']
        }),
            status_code=422) 
    
    # checo se o user ja tem esse grupo
    user_group = db.query(UserGroup)\
    .filter(
        UserGroup.group_id == group_id,
        UserGroup.user_id == user_id
    ).first()
    if user_group:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eUserAlreadyInGroup']
        }),
            status_code=422) 
    user_group = UserGroup(group_id=group_id, user_id=user_id)
    db.add(user_group)
    db.commit()
    
    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na remoção do Grupo no Usuário",
            "message": ptBr['userGroupDeleted']
        }),
            status_code=200) 



@router.delete(
    '/users/{user_id}/permissions/{permission_id}'
)
async def remove_permission(
    db: Session = Depends(get_db),
    *,
    user_id: str,
    permission_id: str,
    current_user: UserInDB = Depends(check_superuser_or_admin),
):
    print(user_id)
    print(permission_id)

    permission = db.query(Permission).filter_by(id=permission_id).first()
    
    if not permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['ePermissionNotFound']
        }),
            status_code=422) 

    # checo se o user nao tem essa permissao
    user_permission = db.query(UserPermission)\
    .filter(
        UserPermission.permission_id == permission_id,
        UserPermission.user_id == user_id
    ).first()

    if not user_permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eUserDontHavePermission']
        }),
            status_code=422) 
    # removo a permissao
    db.delete(user_permission)
    db.commit()
    
    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na remoção da Permissão no Usuário",
            "message": ptBr['userPermissionDeleted']
        }),
            status_code=200) 

@router.post(
    '/users/{user_id}/permissions/{permission_id}'
)
async def add_permission(
    db: Session = Depends(get_db),
    *,
    user_id: str,
    permission_id: str,
    current_user: UserInDB = Depends(check_superuser_or_admin),
):
        # checo se a permissao existe
    permission = db.query(Permission).filter_by(id=permission_id).first()

    if not permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['ePermissionNotFound']
        }),
            status_code=422) 

    # checo se o user nao tem essa permissao
    user_permission = db.query(UserPermission)\
    .filter(
        UserPermission.permission_id == permission_id,
        UserPermission.user_id == user_id
    ).first()

    if user_permission:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eUserAlreadyHasPermission']
        }),
            status_code=422) 
    # removo a permissao
    user_permission = UserPermission(permission_id=permission_id, user_id=user_id)
    db.add(user_permission)
    db.commit()
    
    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso na adição de Permissão no Usuário",
            "message": ptBr['userPermissionAdded']
        }),
            status_code=200) 


@router.post(
    '/user/delete-list',
    summary="Desativar Lista de Usuarios"
)
async def remove_list_group(
    db: Session = Depends(get_db),
    *,
    list_group: UUIDList,
    current_user: UserInDB = Depends(check_superuser_or_admin)
):
    users = db.query(User).filter(User.id.in_(
        list_group.id_list
    )).all()
    
    if len(users) is not len(list_group.id_list):
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "title": "Erro de Validação",
            "message": ptBr['eUserAlreadyHasPermission']
        }),
            status_code=422) 

    [ deactivate_user(db, user=user) for user in users ]
    db.commit()
    
    return Response(json.dumps({
            "messageCode": codes['success'],
            "title": "Sucesso das desativações de usuários",
            "message": ptBr['usersDeleted']
        }),
            status_code=200) 


