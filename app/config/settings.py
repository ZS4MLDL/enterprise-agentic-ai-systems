"""
Central settings — reads MODE and all env vars in one place.
Every other module imports from here; nothing reads os.environ directly.
"""
import os
from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeMode(str, Enum):
    STUDENT = "student"
    ENTERPRISE = "enterprise"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Runtime
    MODE: RuntimeMode = RuntimeMode.STUDENT

    # LLM
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_CHEAP: str = "openai/gpt-4o-mini"
    MODEL_DEFAULT: str = "openai/gpt-4o"
    MODEL_POWERFUL: str = "anthropic/claude-sonnet-4-6"

    # Database
    SQLITE_PATH: str = "./data/app.db"
    DATABASE_URL: str = ""

    # Vector store
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # Queue
    REDIS_URL: str = "redis://localhost:6379/0"

    # Secrets (enterprise)
    VAULT_ADDR: str = "http://localhost:8200"
    VAULT_TOKEN: str = ""

    # Observability
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Document storage
    DOCUMENT_STORE_PATH: str = "./data/documents"
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER: str = "enterprise-ai-docs"

    @property
    def is_enterprise(self) -> bool:
        return self.MODE == RuntimeMode.ENTERPRISE

    @property
    def db_url(self) -> str:
        """Return the active DB URL based on MODE."""
        if self.is_enterprise:
            return self.DATABASE_URL
        return f"sqlite:///{self.SQLITE_PATH}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
