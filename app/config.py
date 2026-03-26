import os
from pathlib import Path

from pydantic_settings import BaseSettings

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Centralized application configuration. All values loaded from .env file."""

    # Ollama
    OLLAMA_BASE_URL: str
    LLM_MODEL: str

    # ChromaDB
    CHROMA_PERSIST_DIR: str
    CHROMA_COLLECTION_NAME: str

    # PDF processing
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int

    # File uploads
    UPLOAD_DIR: str
    MAX_FILE_SIZE_MB: int

    @property
    def chroma_persist_path(self) -> str:
        """Resolve CHROMA_PERSIST_DIR relative to project root."""
        path = Path(self.CHROMA_PERSIST_DIR)
        if not path.is_absolute():
            path = BASE_DIR / path
        return str(path)

    @property
    def upload_path(self) -> str:
        """Resolve UPLOAD_DIR relative to project root."""
        path = Path(self.UPLOAD_DIR)
        if not path.is_absolute():
            path = BASE_DIR / path
        return str(path)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
