# Telegram бот на FastAPI, що слухає вебхук від Telegram і передає повідомлення LangChain агенту. Агент з tools розумно відповідає, 
# а вся історія зберігається в PostgreSQL через checkpointer.
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    force=True  
)

logger = logging.getLogger(__name__)

from src.core.logging_config import setup_logging
from src.config import settings
from src.database.checkpointer import init_db
from src.services.agent_service import AgentService
from src.services.telegram_service import TelegramService
from src.services.health_service import HealthService
from src.api.routes import telegram as telegram_routes

setup_logging()

# Global service instances
agent_service: AgentService = None
telegram_service: TelegramService = None
health_service: HealthService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    logger.info("🚀 Starting application...")
    
    global agent_service, telegram_service, health_service
    
    
    logger.info(f"Connecting to database: {settings.db_name}")

    await init_db()
    agent_service = AgentService()
    await agent_service.initialize()
    telegram_service = TelegramService()
    await telegram_service.get_me()
    health_service = HealthService()
    telegram_routes.set_services(agent_service, telegram_service)
    
    logger.info("✅ Application started")
    yield
    
    
    logger.info("🛑 Application shutting down...")



app = FastAPI(
    title="Enterprise Telegram Agent",
    version=settings.version,
    lifespan=lifespan
)


app.include_router(telegram_routes.router)

# Health endpoints
@app.get("/health")
async def health():
    return health_service.get_health_status()

@app.get("/")
async def root():
    return {"status": "ok", "version": settings.version}