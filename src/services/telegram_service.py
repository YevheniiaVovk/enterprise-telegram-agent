import logging
import re
import httpx
from src.config import settings

logger = logging.getLogger(__name__)


def clean_telegram_html(text: str) -> str:
    """
    Converts Markdown syntax into HTML tags and removes invalid or unsupported tags.
    Telegram HTML supports only the following: <b>, <i>, <code>, <s>, <u>, <a href="...">, <pre>.
    """
    if not text:
        return ""

   
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    
    text = re.sub(r"(?<!\w)\*(.*?)\*(?!\w)", r"<i>\1</i>", text)
    #
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)
    
    
    forbidden_tags = r"</?(?:p|br|ul|ol|li|h[1-6]|div|span)[^>]*>"
    text = re.sub(forbidden_tags, "", text, flags=re.IGNORECASE)
    
    return text


class TelegramService:
    """
    Service for Telegram API operations.
    Handles sending messages and chat actions to Telegram users.
    """
    
    TELEGRAM_API_URL = "https://api.telegram.org"
    DEFAULT_TIMEOUT = 30.0  
    
    def __init__(self):
        """Initialize Telegram service"""
        self.token = settings.telegram_token
        self.base_url = f"{self.TELEGRAM_API_URL}/bot{self.token}"

    async def send_chat_action(self, chat_id: int, action: str = "typing") -> bool:
        """
        Send chat action (e.g., 'typing') to signal that the bot is processing request.
        """
        try:
            url = f"{self.base_url}/sendChatAction"
            payload = {"chat_id": chat_id, "action": action}
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(url, json=payload)
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"⚠️ Failed to send chat action '{action}': {e}")
            return False
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to Telegram chat.
        Includes HTML sanitization and fallback mechanism to plain text if parsing fails.
        """
        try:
            url = f"{self.base_url}/sendMessage"
            cleaned_text = clean_telegram_html(text) if parse_mode == "HTML" else text

            payload = {
                "chat_id": chat_id,
                "text": cleaned_text,
            }
            if parse_mode:
                payload["parse_mode"] = parse_mode
            
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    logger.info(f"✅ Message sent to chat {chat_id}")
                    return True
                
             
                if response.status_code == 400 and parse_mode:
                    logger.warning(f"⚠️ Failed parse_mode='{parse_mode}', retrying as plain text...")
                    payload.pop("parse_mode", None)
                    payload["text"] = text
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

    async def edit_message_text(self, chat_id: int, message_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Edit an existing message text."""
        try:
            url = f"{self.base_url}/editMessageText"
            cleaned_text = clean_telegram_html(text) if parse_mode == "HTML" else text
            
            payload = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": cleaned_text,
            }
            if parse_mode:
                payload["parse_mode"] = parse_mode

            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return True
                
                if response.status_code == 400 and parse_mode:
                    payload.pop("parse_mode", None)
                    payload["text"] = text
                    retry_resp = await client.post(url, json=payload)
                    return retry_resp.status_code == 200
                return False
        except Exception as e:
            logger.error(f"❌ Telegram edit error: {e}")
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
    
    async def get_me(self) -> dict | None:
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