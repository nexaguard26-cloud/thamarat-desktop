"""
Configuration settings for Thamarat ERP Desktop
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Thamarat ERP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    JWT_SECRET: str = "thamarat-erp-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.expanduser('~'), '.thamarat', 'thamarat.db')}"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
