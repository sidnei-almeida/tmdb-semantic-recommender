"""
Configuration settings for the application.
"""
import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Model paths
    MODEL_DIR: Path = Path("models")
    MODEL_PATH: Path = MODEL_DIR / "model_quantized" / "model_quantized.onnx"
    INDEX_PATH: Path = MODEL_DIR / "movies.ann"
    MOVIES_MAP_PATH: Path = MODEL_DIR / "movies_map.pkl"
    
    # Model configuration
    EMBEDDING_SIZE: int = 384  # Based on BERT model hidden_size
    MAX_SEQUENCE_LENGTH: int = 512
    TOP_K: int = 10  # Number of recommendations to return
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://*.render.com",  # Render deployments
        "*",  # Allow all origins in production (adjust as needed)
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

