from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Chill Marketing AI Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database (use SQLite for local development)
    DATABASE_URL: str = "sqlite:///./chillbot.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "marketing_cases"
    
    # LLM APIs
    GIGACHAT_CREDENTIALS: Optional[str] = None
    GIGACHAT_BASE_URL: str = "https://gigachat.devices.sberbank.ru/api/v1"
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"
    GIGACHAT_VERIFY_SSL_CERTS: bool = False
    GIGACHAT_MODEL: str = "GigaChat"
    GIGACHAT_TIMEOUT: float = 60.0
    GIGACHAT_PROXY: Optional[str] = None
    
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # APIs
    NEWSAPI_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()
