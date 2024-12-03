from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # Vector settings
    VECTOR_DIMENSION: int = 384  # all-MiniLM-L6-v2 dimensions
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_BATCH_SIZE: int = 32
    USE_CUDA: bool = False
    MAX_SEQUENCE_LENGTH: int = 128
    ENABLE_PERFORMANCE_MONITORING: bool = True
    MEMORY_THRESHOLD_MB: int = 1000

    # OpenRouter Settings
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "mistralai/mistral-7b-instruct"

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"
    LOG_OUTPUT: str = "stdout"
    LOG_FILE_PATH: Optional[str] = None

    # Application Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CONTEXT_LENGTH: int = 4000

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env

settings = Settings()
