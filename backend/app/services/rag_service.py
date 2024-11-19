from typing import AsyncGenerator, List, Optional
import logging
from app.services.openrouter_service import OpenRouterService, ChatMessage
from app.services.vector_storage import VectorStorageService

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, vector_store: VectorStorageService, llm_service: OpenRouterService):
        self.vector_store = vector_store
        self.llm_service = llm_service

    async def get_context(self, query: str, k: int = 5) -> List[str]:
        """Retrieve relevant context for the query."""
        try:
            # Add relevant keywords for better context retrieval
            enhanced_query = query
            if "auth" in query.lower():
                enhanced_query = f"{query} authentication authorization token jwt api_key"
            elif "endpoint" in query.lower():
                enhanced_query = f"{query} operationId path method"
                
            results = await self.vector_store.search_similar(enhanced_query, limit=k)
            return [result["text"] for result in results]
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def clean_context(self, context: List[str]) -> List[str]:
        """Clean and filter context to improve readability while preserving OpenAPI information."""
        cleaned = []
        for ctx in context:
            # Keep OpenAPI endpoint information even if it's JSON
            if any(keyword in ctx.lower() for keyword in ["operationid", "endpoint", "path", "get", "post", "put", "delete"]):
                # Clean up the context by removing extra whitespace and newlines
                ctx = ' '.join(ctx.split())
                cleaned.append(ctx)
                continue
                
            # Skip if context is too long and not API related
            if len(ctx.split()) > 100 and not any(keyword in ctx.lower() for keyword in ["endpoint", "api", "auth", "path"]):
                continue
                
            # Clean up the context by removing extra whitespace and newlines
            ctx = ' '.join(ctx.split())
            cleaned.append(ctx)
        return cleaned

    def build_messages(self, query: str, context: List[str], is_cli: bool = True) -> List[ChatMessage]:
        """Build chat messages with retrieved context."""
        # Clean and filter context
        cleaned_context = self.clean_context(context)
        context_str = "\n".join(cleaned_context) if cleaned_context else "No relevant context found."
        
        # Base system prompt
        system_content = """You are an AI assistant helping with OpenAPI specifications. Your role is to:
1. Provide clear, concise, and natural responses about API endpoints
2. When describing endpoints, use this format:
   ```
   [HTTP METHOD] [PATH]
   Description: [Brief description]
   Parameters: [Required parameters]
   Authentication: [Auth requirements if any]
   ```
3. Always include the complete endpoint path
4. Format code blocks and endpoints with markdown backticks
5. Use proper spacing and formatting for readability
6. Ask clarifying questions when needed"""

        # Add CLI-specific formatting if used from CLI
        if is_cli:
            system_content += """
7. Format your response for CLI display:
   - Use markdown headers (# ## ###) for sections
   - Use bullet points (- or *) for lists
   - Use `code` for endpoint paths, parameters, and values
   - Use ```language``` for code blocks
   - Use **bold** for important terms
   - Use > for notable information
   - Add empty lines between sections for readability"""
        
        system_msg = ChatMessage(
            role="system",
            content=system_content + "\n\nUse the provided OpenAPI specification context to guide your responses."
        )
        
        user_msg = ChatMessage(
            role="user",
            content=f"Using this OpenAPI specification context:\n\n{context_str}\n\nQuestion: {query}"
        )
        return [system_msg, user_msg]

    async def generate_response(self, query: str) -> AsyncGenerator[str, None]:
        """Generate a streaming response using RAG."""
        try:
            # Get relevant context
            context = await self.get_context(query)
            if not context:
                yield "I couldn't find relevant information in the OpenAPI specification to answer your question. Could you please try rephrasing your question or being more specific?"
                return

            # Check if query is too broad for endpoints
            if query.lower().strip() in ["what endpoints are available?", "what endpoints are there?", "show me the endpoints", "list endpoints"]:
                yield "I can see there are many endpoints available. To help you better, could you please specify what type of endpoints you're interested in? For example:\n\n- Authentication endpoints\n- Data management endpoints\n- Specific resource endpoints (e.g., users, orders)\n- Specific operations (e.g., search, create, update)"
                return

            # If there are too many endpoints in the context, ask for clarification
            if len(context) > 5 and any("endpoint" in c.lower() for c in context):
                yield "I notice there are quite a few endpoints that might be relevant. To provide you with the most helpful information, could you please:\n\n1. Specify the type of operation you're interested in (e.g., GET, POST, PUT)\n2. Indicate the resource type you're looking for\n3. Mention any specific functionality you need"
                return

            # Build messages with context
            messages = self.build_messages(query, context)

            # Stream response using OpenRouter
            llm = self.llm_service  # Store reference to avoid context manager
            await llm.__aenter__()  # Enter context manually
            try:
                buffer = []  # Buffer to accumulate response chunks
                async for token in llm.stream_chat_completion(messages):
                    buffer.append(token)
                    # Only yield when we have a complete sentence or reasonable chunk
                    combined = "".join(buffer)
                    if len(combined) >= 100 or any(c in token for c in [".", "!", "?", "\n"]):
                        yield combined
                        buffer = []
                if buffer:  # Yield any remaining buffered content
                    yield "".join(buffer)
            finally:
                await llm.__aexit__(None, None, None)  # Always exit context
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            yield f"I encountered an error while generating the response: {str(e)}"

    async def get_response_with_context(self, query: str) -> tuple[AsyncGenerator[str, None], List[str]]:
        """Get response with context."""
        try:
            # Get relevant context
            context = await self.get_context(query)
            if not context:
                async def empty_stream():
                    yield "I couldn't find relevant information in the OpenAPI specification to answer your question. Could you please try rephrasing your question or being more specific?"
                return empty_stream(), []

            # Check if query is too broad for endpoints
            if query.lower().strip() in ["what endpoints are available?", "what endpoints are there?", "show me the endpoints", "list endpoints"]:
                async def broad_query_stream():
                    yield "I can see there are many endpoints available. To help you better, could you please specify what type of endpoints you're interested in? For example:\n\n- Authentication endpoints\n- Data management endpoints\n- Specific resource endpoints (e.g., users, orders)\n- Specific operations (e.g., search, create, update)"
                return broad_query_stream(), []

            # If there are too many endpoints in the context, ask for clarification
            if len(context) > 5 and any("endpoint" in c.lower() for c in context):
                async def many_endpoints_stream():
                    yield "I notice there are quite a few endpoints that might be relevant. To provide you with the most helpful information, could you please:\n\n1. Specify the type of operation you're interested in (e.g., GET, POST, PUT)\n2. Indicate the resource type you're looking for\n3. Mention any specific functionality you need"
                return many_endpoints_stream(), []

            # Build messages with context
            messages = self.build_messages(query, context)

            # Create stream with OpenRouter
            llm = self.llm_service  # Store reference to avoid context manager
            await llm.__aenter__()  # Enter context manually
            try:
                stream = llm.stream_chat_completion(messages)
                return stream, self.clean_context(context)
            except Exception as e:
                await llm.__aexit__(type(e), e, e.__traceback__)
                raise

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            async def error_stream():
                yield f"I encountered an error while generating the response: {str(e)}"
            return error_stream(), []
