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
from app.models.user import User as UserSchema, UserInDB, UserUpdate, UserCreate, UUIDList
from app.db_models.models import User
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
            "message": ptBr['eUserNotFound']
        }),
            status_code=404)
    
    return user

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
            "message": ptBr['eNotAnyUsers']
        }),
            status_code=404)
    
    return users


@router.post(
    '/users',
    response_model=UserSchema
)
async def create_user(
        data: UserCreate,
        db: Session = Depends(get_db),
        current_user: UserInDB = Depends(check_superuser_or_admin),
        environment: str = Depends(get_environment_from_token)
):
    new_user = data.user_data
    new_user.password = get_password_hash(new_user.password)
    user_validated = UserCreate(**new_user.dict())
    user = User(**user_validated.dict())
    db.add(user)
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
        user_in: UserUpdate,
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
    if current_user.is_superuser :
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
                "title": "Erro",
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
