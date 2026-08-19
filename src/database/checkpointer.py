from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from langgraph.checkpoint.postgres import AsyncPostgresSaver
from src.config import settings


async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  
)


async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_checkpointer():
    """Get a checkpointer for the agent"""
    return AsyncPostgresSaver(
        sync_connection=settings.database_url,
        
    )


async def init_db():
    """Initialize the database"""
    from src.database.models import Base
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)