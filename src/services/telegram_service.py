import logging
import httpx
from src.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """
    Service for Telegram API operations.
    Handles sending messages to Telegram users.
    """
    
    TELEGRAM_API_URL = "https://api.telegram.org"
    DEFAULT_TIMEOUT = 30.0  
    
    def __init__(self):
        """Initialize Telegram service"""
        self.token = settings.telegram_token
        self.base_url = f"{self.TELEGRAM_API_URL}/bot{self.token}"
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to Telegram chat.
        Includes a fallback mechanism to plain text if HTML parsing fails.
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
            }
            if parse_mode:
                payload["parse_mode"] = parse_mode
            
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    logger.info(f"✅ Message sent to chat {chat_id}")
                    return True
                
                # Фолбек: якщо Telegram відхилив розбір HTML (помилка 400), відправляємо як чистий текст
                if response.status_code == 400 and parse_mode:
                    logger.warning(f"⚠️ Failed parse_mode='{parse_mode}', retrying as plain text...")
                    payload.pop("parse_mode", None)
                    retry_resp = await client.post(url, json=payload)
                    if retry_resp.status_code == 200:
                        logger.info(f"✅ Message sent to chat {chat_id} (plain text fallback)")
                        return True

                logger.error(f"❌ Failed to send message: {response.text}")
                return False
                    
        except httpx.TimeoutException:
            logger.error(f"❌ Telegram API timeout for chat {chat_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}", exc_info=True)
            return False
    
    async def setup_webhook(self, webhook_url: str) -> bool:
        """Setup webhook for receiving Telegram updates."""
        try:
            url = f"{self.base_url}/setWebhook"
            payload = {
                "url": webhook_url,
                "drop_pending_updates": True
            }
            
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    logger.info(f"✅ Webhook set to: {webhook_url}")
                    return True
                else:
                    logger.error(f"❌ Failed to set webhook: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Webhook setup error: {e}", exc_info=True)
            return False
    
    async def get_me(self) -> dict:
        """Get bot information."""
        try:
            url = f"{self.base_url}/getMe"
            
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        bot_info = data.get("result", {})
                        logger.info(f"✅ Bot verified: @{bot_info.get('username')}")
                        return bot_info
                    
                logger.error(f"❌ Failed to get bot info: {response.text}")
                return None
                
        except httpx.TimeoutException:
            logger.error("❌ Telegram API timeout during get_me call")
            return None
        except Exception as e:
            logger.error(f"❌ Get me error: {e}", exc_info=True)
            return None
    
    async def delete_webhook(self) -> bool:
        """Delete webhook (stop receiving updates)."""
        try:
            url = f"{self.base_url}/deleteWebhook"
            
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(url)
                
                if response.status_code == 200:
                    logger.info("✅ Webhook deleted")
                    return True
                else:
                    logger.error(f"❌ Failed to delete webhook: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Delete webhook error: {e}", exc_info=True)
            return False