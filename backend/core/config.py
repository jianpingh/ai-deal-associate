"""
Application Configuration

Centralized configuration management using environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Deal Associate API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: str = ""
    
    # LangGraph
    LANGGRAPH_API_URL: Optional[str] = None
    LANGGRAPH_API_KEY: Optional[str] = None
    LANGGRAPH_ASSISTANT_ID: str = "agent"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        custom = [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
        defaults = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://ai-deal-associate-u8hv.vercel.app",
        ]
        return list(set(defaults + custom))
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra env vars like OPENAI_API_KEY, PINECONE_API_KEY, etc.


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
