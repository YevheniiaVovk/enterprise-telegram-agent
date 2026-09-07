from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Application configuration loaded strictly from environment variables (.env).
    """

    # Project settings
    project_name: str = "Enterprise Telegram Agent"
    version: str = "0.1.0"
    debug: bool = False

    # Telegram settings
    telegram_token: str = Field(validation_alias="TELEGRAM_TOKEN")
    webhook_base_url: str = "http://localhost:8000"

    # OpenAI API
    openai_api_key: Optional[str] = Field(None, validation_alias="OPENAI_API_KEY")

    # Google Gemini API
    google_api_key: Optional[str] = Field(None, validation_alias="GOOGLE_API_KEY")

    # Database
    db_host: str = Field("localhost", validation_alias="DB_HOST")
    db_port: int = Field(5432, validation_alias="DB_PORT")
    db_user: str = Field("postgres", validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    db_name: str = Field("enterprise_agent", validation_alias="DB_NAME")

    # LangSmith (optional)
    langsmith_api_key: Optional[str] = Field(None, validation_alias="LANGSMITH_API_KEY")

    @property
    def database_url(self) -> str:
        """
        Construct PostgreSQL connection URL.
        Format: postgresql+asyncpg://user:password@host:port/dbname
        """
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings instance
settings = Settings()