from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .core.logging import logger
from .api.v1 import upload
from .api.routes import chat
from dotenv import load_dotenv
from .api.ws.chat import handle_chat_websocket
import os
import logging
from .core.logging import logger

from .services.rag_service import RAGService
from .services.openrouter_service import OpenRouterService
from .services.vector_storage import VectorStorageService

vector_service = VectorStorageService()
openRouterService = OpenRouterService()

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))

app = FastAPI(
    title="Chat with OpenAPI",
    description="An intelligent, context-aware chat application for exploring OpenAPI specifications",
    version="0.1.0"
)

# Configure CORS - Allow all origins for WebSocket connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for WebSocket
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
#app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    await handle_chat_websocket(websocket, RAGService(vector_service,openRouterService), openRouterService) 
    
    """ await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo the received message back with a prefix
            await websocket.send_text(f"Server received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close() """

@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    logger.info("Application starting up")

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("Application shutting down")

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "ok", "message": "Chat with OpenAPI service is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}