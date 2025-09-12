from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Calendar Booking API"
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/calendar_db")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS
    # ### 本番環境ドメイン ###
    BACKEND_CORS_ORIGINS: List[str] = [
        # "http://localhost",
        # "http://localhost:3000",
        # "http://localhost:8000",
        # "http://localhost:8080",
        # "http://localhost:53231",
        # "http://mattya3340.tplinkdns.com",
        "*",
    ]
    
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "changethis")
    
    API_PREFIX: str = "/api"
    PROJECT_VERSION: str = "1.0.0"
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()