from pathlib import Path

from starlette.config import Config

from app.models.database import DatabaseURL
from pathlib import Path

from starlette.config import Config

from app.models.database import DatabaseURL


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = config(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result

p: Path = Path(__file__).parents[2] / ".env"
config: Config = Config(p if p.exists() else None)

DATABASE_PORT: int = config("DATABASE_PORT", cast=int)
DATABASE_SERVER = config("DATABASE_SERVER", cast=str)
DATABASE_USER = config("DATABASE_USER", cast=str)
DATABASE_PASSWORD = config("DATABASE_PASSWORD", cast=str)
DATABASE_DB = config("DATABASE_DB", cast=str)
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_DB}"
)

DATABASE_CONFIG: DatabaseURL = DatabaseURL(drivername="asyncpg", username=DATABASE_USER, password=DATABASE_PASSWORD,
                                          host=DATABASE_SERVER, port=DATABASE_PORT, database=DATABASE_DB)
ALEMBIC_CONFIG: DatabaseURL = DatabaseURL(drivername="postgresql+psycopg2", username=DATABASE_USER, password=DATABASE_PASSWORD,
                                          host=DATABASE_SERVER, port=DATABASE_PORT, database=DATABASE_DB)
API_V1_STR = "/api/v1"

SECRET_KEY = config("SECRET_KEY", cast=str)

ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)  # 60 minutes * 24 hours * 8 days = 8 days

BACKEND_CORS_ORIGINS = config(
    "BACKEND_CORS_ORIGINS"
)  # a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200, http://localhost:3000, http://localhost:8080, http://local.dockertoolbox.tiangolo.com"
PROJECT_NAME = config("PROJECT_NAME")

FIRST_SUPERUSER = config("FIRST_SUPERUSER")
FIRST_SUPERUSER_PASSWORD = config("FIRST_SUPERUSER_PASSWORD")
FIRST_SUPERUSER_EMAIL = config("FIRST_SUPERUSER_EMAIL")
FIRST_SUPERUSER_FULLNAME = config("FIRST_SUPERUSER_FULLNAME")