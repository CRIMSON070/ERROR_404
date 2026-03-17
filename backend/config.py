"""
Configuration settings for FastAPI backend
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "IPL Auction Strategy Platform API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered IPL auction strategy and team analysis platform"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ]
    
    # Data Paths
    DATA_DIR: str = "data"
    PROCESSED_DATA_PATH: str = "data/processed/auction_players"
    FEATURES_PATH: str = "data/features/engineered_features"
    MODELS_DIR: str = "models/saved_models"
    
    # Model Settings
    DEVICE: str = "cpu"  # or "cuda"
    MAX_PLAYERS_IN_TEAM: int = 25
    BUDGET_LIMIT_CRORE: float = 120.0
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/backend.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings
