"""
Dependency injection for FastAPI routes.

Used for injecting database sessions, services, etc. into route handlers.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
