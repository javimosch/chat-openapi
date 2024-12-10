from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os
import logging

logger = logging.getLogger(__name__)
