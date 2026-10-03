import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "AI English Tutor Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_tutor_db",
        description="Async PostgreSQL Database Connection String"
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/ai_tutor_db",
        description="Sync PostgreSQL Database Connection String for Alembic"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis Connection String"
    )

    # LLM Configuration
    LLM_PROVIDER: str = Field(default="mock", description="llm provider: mock, openai, gemini, ollama")
    LLM_BASE_URL: str = Field(default="", description="Base URL for custom OpenAI/Ollama endpoints")
    LLM_MODEL: str = Field(default="gpt-4o-mini", description="LLM model name")
    LLM_API_KEY: str = Field(default="", description="API key for LLM provider")

    # TTS Configuration
    TTS_PROVIDER: str = Field(default="gtts", description="tts provider: gtts, mock, elevenlabs, piper, kokoro")
    TTS_MODEL: str = Field(default="standard", description="TTS model identifier")
    TTS_BASE_URL: str = Field(default="", description="TTS API base URL if applicable")
    TTS_API_KEY: str = Field(default="", description="TTS API Key")
    DEFAULT_VOICE: str = Field(default="female_01", description="Default voice ID")
    DEFAULT_TTS_SPEED: float = Field(default=0.95, description="Default playback speed multiplier")

    # Language & Grammar
    LANGUAGE_DETECTION_PROVIDER: str = Field(default="fast", description="fast, polyglot")
    GRAMMAR_PROVIDER: str = Field(default="rule_llm", description="rule_llm, languagetool")

    # Security & CORS
    CORS_ORIGINS: List[str] = Field(default=["*"], description="CORS allowed origins")
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production-12345", description="JWT/Session secret key")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Max requests per minute per IP")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="DEBUG, INFO, WARNING, ERROR")


settings = Settings()
