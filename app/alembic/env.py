from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from sqlalchemy import pool

from app.config import settings
from app.infrastructure.persistence.base import Base

target_metadata = Base.metadata

# Import all models to ensure they are registered on Base.metadata
from app.infrastructure.persistence.models import user_model  # noqa: F401, E402

config = context.config
config.set_main_option("sqlalchemy.url", settings.alembic_url)

connectable = async_engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)

async def run_migrations_online():
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()
