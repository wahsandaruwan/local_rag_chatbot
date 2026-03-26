import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized application configuration."""

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.1"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_data"
    )
    CHROMA_COLLECTION_NAME: str = "rag_documents"

    # PDF processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # File uploads
    UPLOAD_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
    )
    MAX_FILE_SIZE_MB: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
