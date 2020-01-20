import json
import uuid

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.utils.db import get_db
from app.api.utils.security import get_current_active_superuser
from app.core.return_messages import codes, ptBr
from app.crud.environment import (
    get_environment,
    get_multi,
    delete_relations_envuser_by_id
)
from app.db_models.models import Environment
from app.models.environment import Environment as EnvironmentSchema, EnvironmentCreateIn, EnvironmentUpdateIn
from app.models.user import UserInDB

router = APIRouter()


@router.post('/environments', response_model=EnvironmentSchema)
async def create_environment(
        request: EnvironmentCreateIn,
        db: Session = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_superuser)
):
    new_environment = Environment(
        id=uuid.uuid4(),
        name=request.name.upper(),
    )
    db.add(new_environment)
    db.commit()

    return new_environment


@router.get('/environments/{environment_id}', response_model=EnvironmentSchema)
async def retrieve_environment(
        environment_id,
        db: Session = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_superuser)
):
    environment_retrieved = get_environment(db, environment_id)
    return environment_retrieved


@router.get('/environments')
async def retrieve_environments(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: UserInDB = Depends(get_current_active_superuser)
):
    environments = get_multi(db, skip=skip, limit=limit)
    return environments


@router.put('/environments/{env_id}')
async def update_environment(
        request: EnvironmentUpdateIn,
        env_id,
        db: Session = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_superuser)
):
    environment_updated = db.query(Environment) \
        .filter(Environment.id == str(env_id)) \
        .update({
        "name": request.name.upper()
    })
    db.commit()
    return environment_updated


@router.delete('/environments/{env_id}')
async def delete_environment(
        env_id,
        db: Session = Depends(get_db),
        current_user: UserInDB = Depends(get_current_active_superuser)
):
    env = get_environment(db, env_id=env_id)
    db.delete(env)
    db.commit()
    return Response(json.dumps({
        "messageCode": codes['success'],
        "title": "Sucesso na Remoção do Ambiente",
        "message": ptBr['envDeleted']
    }),
        status_code=200)
