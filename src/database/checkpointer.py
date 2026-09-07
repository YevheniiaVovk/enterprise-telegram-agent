import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from langgraph.checkpoint.memory import MemorySaver
from src.config import settings

logger = logging.getLogger(__name__)


async_engine = None
AsyncSessionLocal = None


def _ensure_engine():
    """Створює engine та sessionmaker, якщо вони ще не ініціалізовані."""
    global async_engine, AsyncSessionLocal
    if async_engine is None:
        async_engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


def get_checkpointer():
    """
    Get a checkpointer for the agent.
    Currently using MemorySaver for development.
    Will be replaced with PostgresSaver soon.
    """
    return MemorySaver()

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    _ensure_engine()
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize the database"""
    logger.info(f"Connecting to database: {settings.db_name}")
    _ensure_engine()
    from src.database.models import Base
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)