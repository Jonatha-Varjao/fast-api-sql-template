from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

async_engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True, pool_size=20, max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession,
    expire_on_commit=False, autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
