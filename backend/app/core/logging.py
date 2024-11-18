import logging
import json
import sys
from pathlib import Path
from typing import Union, Dict, Any

from .config import settings

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

def setup_logging() -> logging.Logger:
    """Configure and return the application logger"""
    logger = logging.getLogger("chat-openapi")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter based on settings
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Configure handler based on settings
    if settings.LOG_OUTPUT.lower() == "file" and settings.LOG_FILE_PATH:
        # Create log directory if it doesn't exist
        log_path = Path(settings.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        handler: Union[logging.FileHandler, logging.StreamHandler] = logging.FileHandler(
            settings.LOG_FILE_PATH
        )
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Log startup message
    logger.info(
        "Logging system initialized",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
            "log_output": settings.LOG_OUTPUT,
            "log_file": settings.LOG_FILE_PATH,
        },
    )
    
    return logger

# Create the application logger
logger = setup_logging()

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance."""
    if name:
        return logging.getLogger(f"chat-openapi.{name}")
    return logger

__all__ = ['logger', 'get_logger']
