from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.RETURN_DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True
)

async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
