"""OpenRouter service for chat completions."""

import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

class ChatMessage:
    """Chat message model."""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        
    def model_dump(self) -> Dict[str, str]:
        """Convert to dict format."""
        return {
            "role": self.role,
            "content": self.content
        }

class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize OpenRouter service."""
        self.api_key = settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
            
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = settings.OPENROUTER_MODEL
        self.client = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/your-username/chat-openapi",
                "X-Title": "Chat OpenAPI"
            },
            timeout=30.0
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a chat completion from OpenRouter.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Chat completion response
        """
        try:
            payload = {
                "model": self.model,
                "messages": [msg.model_dump() for msg in messages],
                "temperature": temperature,
                "stream": False
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
                
            logger.debug(f"Starting chat completion: {json.dumps(payload)}")
            
            response = await self.client.post(
                "/chat/completions",
                json=payload
            )
            
            if response.status_code >= 400:
                response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error during chat completion: {str(e)}")
            raise

    async def stream_chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion from OpenRouter.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Chunks of the generated text
        """
        try:
            payload = {
                "model": self.model,
                "messages": [msg.model_dump() for msg in messages],
                "temperature": temperature,
                "stream": True
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
                
            logger.debug(f"Starting streaming chat completion: {json.dumps(payload)}")
            
            async with self.client.stream(
                "POST",
                "/chat/completions",
                json=payload,
                timeout=60.0  # Increased timeout for streaming
            ) as response:
                if response.status_code >= 400:
                    error_text = await response.text()
                    logger.error(f"Error from OpenRouter API: {error_text}")
                    response.raise_for_status()
                
                buffer = []  # Buffer to accumulate tokens
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                        
                    line = line.removeprefix("data: ")
                    if line == "[DONE]":
                        if buffer:  # Yield any remaining buffered content
                            yield "".join(buffer)
                        break
                        
                    try:
                        data = json.loads(line)
                        if not isinstance(data, dict):
                            continue
                            
                        choices = data.get("choices", [])
                        if not choices:
                            continue
                            
                        delta = choices[0].get("delta", {})
                        if content := delta.get("content"):
                            buffer.append(content)
                            # Only yield when we have a reasonable amount of text
                            if len("".join(buffer)) >= 20 or any(c in content for c in [".", "!", "?", "\n"]):
                                yield "".join(buffer)
                                buffer = []
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode line: {line}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing chunk: {e}")
                        continue
                            
        except Exception as e:
            logger.error(f"Error during streaming chat completion: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
