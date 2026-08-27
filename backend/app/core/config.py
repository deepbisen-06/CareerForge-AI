from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import os
from pathlib import Path

# Resolve base workspace directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "careerbridge.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerBridge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-careerbridge-ai-jwt-key-development-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database (uses absolute path for seamless multi-cwd consistency)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")
    
    # Redis / Task Queue
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # AI Providers
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")  # 'gemini', 'openai', 'fallback', or 'auto'
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
