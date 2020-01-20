from app.crud import user as db_user
from app.core import config
from app.models.user import UserCreate

# make sure all SQL Alchemy models are imported before initializing DB
# otherwise, SQL Alchemy might fail to initialize properly relationships
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28
from app.db import base
from app.core.security import get_password_hash

def init_db(db_session):
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    user = db_user.get_by_email(db_session, email=config.FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = UserCreate(
            username=config.FIRST_SUPERUSER,
            full_name=config.FIRST_SUPERUSER_FULLNAME,
            email=config.FIRST_SUPERUSER_EMAIL,
            password=get_password_hash(config.FIRST_SUPERUSER_PASSWORD),
            document="01311104542",
            phone_number="9023819283",
            is_superuser=True,
            is_active=True
        )
        user = db_user.create(db_session, user_in=user_in)
