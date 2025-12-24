import os
from typing import Optional


class Settings:
    """Application settings"""
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "false").lower() == "true"
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # Model Settings
    DEFAULT_MODEL: str = "distilgpt2"
    MODEL_CACHE_DIR: Optional[str] = os.getenv("MODEL_CACHE_DIR", None)
    DEVICE: str = os.getenv("DEVICE", "cpu")  # cpu, cuda, mps
    
    # Compression Settings
    MAX_COMPRESSION_JOBS: int = int(os.getenv("MAX_COMPRESSION_JOBS", "5"))
    COMPRESSION_TIMEOUT: int = int(os.getenv("COMPRESSION_TIMEOUT", "3600"))  # 1 hour
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))  # seconds
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

