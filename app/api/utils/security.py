import jwt
import json
import app.crud.user as crud_user

from jwt import PyJWTError
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import Response
from sqlalchemy.orm import Session

from app.api.utils.db import get_db
from app.core import config
from app.core.jwt import ALGORITHM
from app.db_models.models import User
from app.models.token import TokenPayload
from app.core.return_messages import codes, ptBr


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

def get_environment_from_token(
    db: Session = Depends(get_db),
    token: str = Security(reusable_oauth2)
    ):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Token expirou/invalido"
        )
    return payload.get("environment")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Security(reusable_oauth2)
    ):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Token expirou/invalido"
        )
    user = crud_user.get(db, user_id=token_data.user_data.id)
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: User = Security(get_current_user)
    ):
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Usuario inativo")
    return current_user

def check_superuser_or_admin(
    db: Session = Depends(get_db),
    token: str = Security(reusable_oauth2)
):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Token expirou/invalido"
        )
    environment = token_data.environment
    env_user = db.query(EnvUser).\
    filter_by(environment_id = str(environment), user_id = str(token_data.user_data.id)).first()
    user = crud_user.get(db, user_id=str(token_data.user_data.id))
       
    if env_user:
        env_user = env_user.is_admin
    env_user = env_user

    if token_data.user_data.is_superuser or env_user:
        return user    
    
    raise HTTPException(
            status_code=403, detail="Usuario não tem permissão"
        )

def get_current_active_superuser(
    current_user: User = Security(get_current_user)
    ):
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user