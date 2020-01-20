from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from app.core.security import get_password_hash
from app.db_models.models import *
from sqlalchemy.orm import Session
from app.models.environment import Environment as EnvironmentSchema, EnvironmentCreateIn, EnvironmentUpdateIn


def get_environment(db: Session, *, env_id: str):
    environment = db.query(Environment).filter(Environment.id == str(env_id)).first()
    return environment

def create(db_session: Session, *, environment_in: EnvironmentCreateIn) -> Environment:
    environment = Environment(
        name=environment_in.name,
    )
    db_session.add(environment)
    db_session.commit()
    db_session.refresh(environment)
    return environment


def get_multi(db_session: Session, *, skip=0, limit=100) -> List[Optional[Environment]]:
    return db_session.query(Environment).order_by(Environment.name).offset(skip).limit(limit).all()


def delete_relations_envuser_by_id(db_session: Session, env_id) -> bool:
    try:
       db_session.query(EnvUser).filter_by(environment_id=env_id).delete()
    except Exception as error:
        print(str(error))
        raise False
    return True
