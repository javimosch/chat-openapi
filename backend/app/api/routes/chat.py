from fastapi import APIRouter, WebSocket, Depends
from ...services.rag_service import RAGService
from ...services.openrouter_service import OpenRouterService
from ..ws.chat import handle_chat_websocket
from ...dependencies import get_rag_service, get_openrouter_service

router = APIRouter()

@router.websocket("/chat/ws")
async def chat_websocket(
    websocket: WebSocket
    #rag_service: RAGService = Depends(get_rag_service),
    #openrouter_service: OpenRouterService = Depends(get_openrouter_service)
):
    await handle_chat_websocket(websocket, rag_service, openrouter_service)
