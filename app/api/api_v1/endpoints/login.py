import json
from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.utils.db import get_db
from app.api.utils.security import get_current_user
from app.core import config
from app.core.jwt import create_access_token
from app.core.return_messages import codes, ptBr
from app.core.security import get_password_hash

from app.crud.user import (
    authenticate,
    get_by_email,
    is_active,
    is_admin_env
)
from app.models.msg import Msg
from app.models.token import LoginOAuth
from app.models.user import User
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
        *,
        db: Session = Depends(get_db),
        data: LoginOAuth
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate(
        db, email_or_username=data.username, password=data.password
    )
    if not user:
        return Response(json.dumps({
            "messageCode": codes['validation'],
            "message": ptBr['eIncorrectDataLogin']
        }),
            status_code=422)
    if not is_active(user):
        return Response(json.dumps({
            "messageCode": codes['db'],
            "message": ptBr['eUserNotActive']
        }),
            status_code=401)
    user_response = {
        "id":str(user.id),
        "username":user.username,
        "full_name":user.full_name,
        "email":user.email,
        "is_superuser":user.is_superuser
    }
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
            "access_token": create_access_token(
                data={
                    "user_data": user_response,
                },
                expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }

@router.post("/login/test-token", response_model=User)
def test_token(current_user: User = Depends(get_current_user)):
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=Msg)
def recover_password(email: str, db: Session = Depends(get_db)):
    """
    Password Recovery
    """
    # user = get_by_email(db, email=email)

    # if not user:
    #     return Response(json.dumps({
    #         "messageCode": codes['validation'],
    #         "title": "Dados Incorretos",
    #         "message": ptBr['eDontExistsThisUser']
    #     }),
    #         status_code=422)
    # password_reset_token = generate_password_reset_token(email=email)
    # send_reset_password_email(
    #     email_to=user.email, email=email, token=password_reset_token
    # )
    return Response(json.dumps({
        "messageCode": codes['success'],
        "title": "Sucesso na Operação.",
        "message": ptBr['passwordRecoveryEmail']
    }),
        status_code=200)


@router.post("/reset-password/", response_model=Msg)
def reset_password(token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    """
    Reset password
    """
    # email = verify_password_reset_token(token)
    # if not email:
    #     return Response(json.dumps({
    #         "messageCode": codes['validation'],
    #         "title": "Erro no Token",
    #         "message": ptBr['eInvalidToken']
    #     }),
    #         status_code=400)
    # user = get_by_email(db, email=email)
    # if not user:
    #     return Response(json.dumps({
    #         "messageCode": codes['db'],
    #         "title": "Erro no banco de dados.",
    #         "message": ptBr['eUserNotFound']
    #     }),
    #         status_code=400)
    # elif not is_active(user):
    #     return Response(json.dumps({
    #         "messageCode": codes['db'],
    #         "title": "Erro no Banco de Dados",
    #         "message": ptBr['eUserNotActive']
    #     }),
    #         status_code=404)
    # hashed_password = get_password_hash(new_password)
    # user.password = hashed_password
    # db.add(user)
    # db.commit()
    return Response(json.dumps({
        "messageCode": codes['success'],
        "title": "Sucesso na Operação.",
        "message": ptBr['passwordRecoverySuccess']
    }),
        status_code=200)
