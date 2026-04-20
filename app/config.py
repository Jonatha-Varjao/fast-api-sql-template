from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_settings() -> Settings:
    return Settings()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_port: int = 5432
    database_server: str = "localhost"
    database_user: str = "app_user"
    database_password: str = "app_password"
    database_db: str = "app_db"

    # Redis
    redis_url: str = "redis://redis:6379"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672"

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"

    # OAuth2
    oauth2_provider: str = "keycloak"
    oauth2_server_url: str = ""
    oauth2_realm: str = ""
    oauth2_client_id: str = ""
    oauth2_client_secret: str = ""
    oauth2_audience: str = ""

    # App
    backend_cors_origins: str = ""
    project_name: str = "FastAPI App"
    api_v1_str: str = "/api/v1"
    secret_key: str = ""

    # Computed properties
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_server}:{self.database_port}/{self.database_db}"
        )

    @property
    def alembic_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.database_user}:{self.database_password}"
            f"@{self.database_server}:{self.database_port}/{self.database_db}"
        )


settings = get_settings()
