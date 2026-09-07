import time
import logging
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from src.schemas.telegram import TelegramUpdate, TelegramWebhookResponse
from src.services.agent_service import AgentService
from src.services.telegram_service import TelegramService
from src.repositories.user_repository import UserRepository
from src.database.checkpointer import get_async_session

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Global service instances (initialized in main.py)
agent_service: AgentService = None
telegram_service: TelegramService = None

PROCESSED_UPDATES: set[int] = set()
MAX_CACHE_SIZE = 10000


def clear_old_updates():
    if len(PROCESSED_UPDATES) > MAX_CACHE_SIZE:
        PROCESSED_UPDATES.clear()


def set_services(agent_svc: AgentService, telegram_svc: TelegramService):
    global agent_service, telegram_service
    agent_service = agent_svc
    telegram_service = telegram_svc


@router.post("/webhook", response_model=TelegramWebhookResponse)
async def telegram_webhook(
    update: TelegramUpdate,
    background_tasks: BackgroundTasks
):
    try:
        logger.info(f"📥 Received Telegram update: {update.update_id}")

        if update.update_id in PROCESSED_UPDATES:
            logger.warning(f"⚠️ Duplicate update_id {update.update_id} received. Skipping background task.")
            return TelegramWebhookResponse()

        PROCESSED_UPDATES.add(update.update_id)
        clear_old_updates()
        
        if not update.message:
            logger.debug("Update has no message, skipping")
            return TelegramWebhookResponse()
        
        message = update.message
        user_id = message.from_user.id
        chat_id = message.chat.id
        text = message.text or ""
        
        if not text:
            logger.debug(f"Message from {user_id} has no text, skipping")
            return TelegramWebhookResponse()
        
        logger.info(f"📨 Message from user {user_id}: {text[:50]}...")
        
        background_tasks.add_task(
            process_telegram_message,
            user_id=user_id,
            chat_id=chat_id,
            text=text,
            update_id=update.update_id
        )
        
        return TelegramWebhookResponse()
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return TelegramWebhookResponse()


@router.post("/setup-webhook")
async def setup_webhook_endpoint():
    try:
        if not telegram_service:
            return {"status": "error", "message": "Telegram service not initialized"}
        
        from src.config import settings
        webhook_url = f"{settings.webhook_base_url}/telegram/webhook"
        
        success = await telegram_service.setup_webhook(webhook_url)
        
        if success:
            bot_info = await telegram_service.get_me()
            if bot_info:
                return {
                    "status": "success",
                    "webhook_url": webhook_url,
                    "bot": bot_info.get("username"),
                    "message": "Webhook configured successfully"
                }
        
        return {"status": "error", "message": "Failed to setup webhook"}
        
    except Exception as e:
        logger.error(f"❌ Setup webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.post("/delete-webhook")
async def delete_webhook_endpoint():
    try:
        if not telegram_service:
            return {"status": "error", "message": "Telegram service not initialized"}
        
        success = await telegram_service.delete_webhook()
        return {
            "status": "success" if success else "error",
            "message": "Webhook deleted" if success else "Failed to delete webhook"
        }
    except Exception as e:
        logger.error(f"❌ Delete webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.get("/bot-info")
async def get_bot_info():
    try:
        if not telegram_service:
            return {"status": "error", "message": "Telegram service not initialized"}
        
        bot_info = await telegram_service.get_me()
        if bot_info:
            return {"status": "success", "bot": bot_info}
        
        return {"status": "error", "message": "Failed to get bot info"}
    except Exception as e:
        logger.error(f"❌ Get bot info error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def process_telegram_message(
    user_id: int,
    chat_id: int,
    text: str,
    update_id: int
):
    t_start = time.perf_counter()
    logger.info(f"⏱️ [START] Processing update_id: {update_id} for user_id: {user_id}")

    try:
        if not agent_service:
            logger.error("❌ Agent service not initialized!")
            if telegram_service:
                await telegram_service.send_message(
                    chat_id=chat_id,
                    text="❌ Agent is not initialized. Please try again later."
                )
            return

        # 1. Запит до БД: створення/перевірка користувача (сесія закривається одразу)
        t_db_start = time.perf_counter()
        async with get_async_session() as session:
            repo = UserRepository(session)
            await repo.get_or_create_user(user_id)
        logger.info(f"⏱️ [DB USER CHECK] Took: {time.perf_counter() - t_db_start:.3f} sec")

        # 2. Виклик LLM Агента (БД не задіяна)
        t_agent_start = time.perf_counter()
        agent_response = await agent_service.process_message(
            user_id=user_id,
            message=text
        )
        logger.info(f"⏱️ [AGENT CORE EXECUTION] Took: {time.perf_counter() - t_agent_start:.3f} sec")

        # 3. Запит до БД: оновлення останньої взаємодії
        t_db_update = time.perf_counter()
        async with get_async_session() as session:
            repo = UserRepository(session)
            await repo.update_last_interaction(user_id)
        logger.info(f"⏱️ [DB UPDATE INTERACTION] Took: {time.perf_counter() - t_db_update:.3f} sec")

        # 4. Відправка відповіді
        t_send_start = time.perf_counter()
        await telegram_service.send_message(
            chat_id=chat_id,
            text=agent_response
        )
        logger.info(f"⏱️ [TELEGRAM SEND] Took: {time.perf_counter() - t_send_start:.3f} sec")

    except Exception as e:
        logger.error(f"❌ Agent processing error (update_id {update_id}): {e}", exc_info=True)
        if telegram_service:
            error_str = str(e).lower()
            if "429" in error_str or "resource_exhausted" in error_str:
                user_msg = "⚠️ Вибачте, ліміт запитів до AI тимчасово вичерпано. Спробуйте через кілька хвилин."
            else:
                user_msg = "❌ Вибачте, виникла помилка під час обробки вашого повідомлення. Спробуйте пізніше."
                
            try:
                await telegram_service.send_message(
                    chat_id=chat_id,
                    text=user_msg
                )
            except Exception as send_err:
                logger.error(f"Failed to send error notification: {send_err}")
    finally:
        t_total = time.perf_counter() - t_start
        logger.info(f"🏁 [TOTAL TIME] Update {update_id} processed in {t_total:.3f} sec")