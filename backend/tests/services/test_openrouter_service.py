"""Tests for OpenRouter service."""

import pytest
from app.services.openrouter_service import OpenRouterService, ChatMessage

pytestmark = pytest.mark.asyncio

async def test_chat_completion():
    """Test basic chat completion functionality."""
    service = OpenRouterService()
    async with service as s:
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Say hello!")
        ]
        
        response = await s.chat_completion(messages)
        
        # Basic validation of response structure
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]
        assert "content" in response["choices"][0]["message"]
        assert isinstance(response["choices"][0]["message"]["content"], str)
        
async def test_missing_api_key():
    """Test missing API key."""
    from unittest.mock import patch
    
    with patch("app.services.openrouter_service.settings") as mock_settings:
        mock_settings.OPENROUTER_API_KEY = None
        with pytest.raises(ValueError, match="OpenRouter API key not configured"):
            OpenRouterService()
