from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import logging
from ...services.rag_service import RAGService
from ...services.openrouter_service import OpenRouterService, ChatMessage

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(json.dumps({
            "type": "token",
            "content": message
        }))

    async def send_error(self, error: str, websocket: WebSocket):
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": error
        }))

    async def send_end(self, websocket: WebSocket):
        await websocket.send_text(json.dumps({
            "type": "end"
        }))

manager = ConnectionManager()

async def stream_handler(token: str, websocket: WebSocket):
    """Handle streaming tokens from the LLM."""
    try:
        await manager.send_message(token, websocket)
    except Exception as e:
        logger.error(f"Error streaming token: {e}")
        await manager.send_error(str(e), websocket)

async def handle_chat_websocket(
    websocket: WebSocket,
    rag_service: RAGService,
    openrouter_service: OpenRouterService
):
    """Handle WebSocket connection for chat."""
    logger.info(f'WebSocket connection attempt from origin: {websocket.headers.get("origin")}')
    logger.info(f'WebSocket headers: {websocket.headers}')
    try:
        await manager.connect(websocket)
        logger.info('WebSocket connection accepted')

        async with openrouter_service as service:
            while True:
                try:
                    # Receive message from client
                    data = await websocket.receive_text()
                    logger.info(f'Received data: {data}')
                    message_data = json.loads(data)
                    user_message = message_data.get("content", "")

                    if not user_message.strip():
                        continue

                    # Generate response using RAG service
                    async for token in rag_service.generate_response(user_message):
                        await stream_handler(token, websocket)
                    
                    # Send end message
                    await manager.send_end(websocket)
                    logger.info('End message sent')

                except json.JSONDecodeError:
                    await manager.send_error("Invalid message format", websocket)
                    logger.error('Invalid message format received')
                except Exception as e:
                    logger.error(f'Error processing message: {e}')
                    await manager.send_error(str(e), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info('WebSocket disconnected')
    except Exception as e:
        logger.error(f'WebSocket connection error: {e}')
