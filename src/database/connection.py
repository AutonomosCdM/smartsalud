"""
Database connection and session management.

Async SQLAlchemy engine with connection pooling.
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import structlog

from src.core.config import get_settings
from src.database.models import Base

logger = structlog.get_logger(__name__)

# Global engine and session factory
engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create async engine.

    Configuration:
    - pool_pre_ping: Verify connections before use (Railway safety)
    - pool_recycle: Recycle connections after 1 hour
    - pool_size: 20 base connections (optimized for 20K patients / 200 doctors)
    - max_overflow: 30 additional connections under load
    """
    global engine

    if engine is None:
        settings = get_settings()
        # Test environment uses NullPool (no connection pooling)
        if settings.app_env == "test":
            engine = create_async_engine(
                settings.database_url,
                echo=False,
                poolclass=NullPool
            )
        else:
            # Development/Production with connection pooling
            # Optimized for 20K patients / 200 doctors
            # Formula: (requests_per_second × avg_query_time) × 2
            # = (8 × 0.1) × 2 = 16 → rounded to 20
            engine = create_async_engine(
                settings.database_url,
                echo=(settings.app_env == "development"),
                pool_size=20,        # Base connections (increased from 10)
                max_overflow=30,     # Additional under load (increased from 5)
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle after 1 hour
            )

        logger.info(
            "database_engine_created",
            environment=settings.app_env,
            url=settings.database_url.split("@")[1] if "@" in settings.database_url else "***"
        )

    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create async session factory.

    Configuration:
    - expire_on_commit=False: Objects remain usable after commit
    - autoflush=False: Manual flush control
    - autocommit=False: Explicit transactions
    """
    global AsyncSessionLocal

    if AsyncSessionLocal is None:
        engine = get_engine()
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )

        logger.info("database_session_factory_created")

    return AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes.

    Provides async database session with automatic cleanup.

    Usage:
        @router.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models.
    Only for development - production uses Alembic migrations.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("database_tables_created")


async def close_db() -> None:
    """
    Close database connections.

    Call this on application shutdown.
    """
    global engine

    if engine is not None:
        await engine.dispose()
        logger.info("database_connections_closed")
        engine = None
