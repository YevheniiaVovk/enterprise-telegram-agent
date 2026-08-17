from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres_dev"
    db_name: str = "enterprise_agent"
    
  
    telegram_token: str = "your_telegram_token"
    
   
    openai_api_key: str = "your_openai_key"
    google_api_key: str = "your_google_key"
    
   
    environment: Literal["development", "production"] = "development"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

