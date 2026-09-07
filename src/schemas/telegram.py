from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TelegramUser(BaseModel):
    """Telegram user information from update"""

    id: int
    is_bot: bool = False
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    """Telegram chat information from update"""

    id: int
    type: str  # "private", "group", "supergroup", "channel"
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None


class TelegramMessage(BaseModel):
    """Telegram message structure"""

    model_config = ConfigDict(populate_by_name=True)

    message_id: int
    date: int
    chat: TelegramChat
    from_user: TelegramUser = Field(alias="from")
    text: Optional[str] = None


class TelegramUpdate(BaseModel):
    """Telegram incoming update (webhook payload)"""

    model_config = ConfigDict(populate_by_name=True)

    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None


class TelegramSendMessageRequest(BaseModel):
    """Request body for sending Telegram message"""

    chat_id: int
    text: str
    parse_mode: str = "HTML"


class TelegramWebhookResponse(BaseModel):
    """Response for Telegram webhook (always OK)"""

    ok: bool = True