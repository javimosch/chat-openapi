from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.logging import logger
from .api.v1 import upload
from .api.routes import chat

app = FastAPI(
    title="Chat with OpenAPI",
    description="An intelligent, context-aware chat application for exploring OpenAPI specifications",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # React dev server and all other origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

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
