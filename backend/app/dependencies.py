from .services.rag_service import RAGService
from .services.openrouter_service import OpenRouterService
from .core.config import settings
import os

def get_rag_service():
    """Dependency to get RAG service."""
    return RAGService()

def get_openrouter_service():
    """Dependency to get OpenRouter service."""
    return OpenRouterService(
        api_key=os.getenv("OPENROUTER_API_KEY"),  # Use environment variable for API key
        model=os.getenv("OPENROUTER_MODEL")        # Use environment variable for model
    )
