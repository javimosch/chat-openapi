"""
Models for OpenAPI specifications and responses.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class OpenAPISpec(BaseModel):
    """OpenAPI specification model."""
    id: str = Field(..., description="Unique identifier for the specification")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="Content type (json/yaml)")
    size_bytes: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    title: str = Field(..., description="API title from spec")
    version: str = Field(..., description="API version from spec")
    description: Optional[str] = Field(None, description="API description from spec")
    num_chunks: Optional[int] = Field(None, description="Number of chunks generated")

class UploadResponse(BaseModel):
    """Response model for successful file uploads"""
    spec_id: str = Field(..., description="ID of the uploaded spec")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    message: str = Field(..., description="Success message")

class OpenAPIResponse(BaseModel):
    """Response model for OpenAPI operations."""
    spec_id: str = Field(..., description="Unique identifier for the specification")
    size: int = Field(..., description="File size in bytes")
    num_chunks: int = Field(..., description="Number of chunks generated")
    title: str = Field(..., description="API title")
    version: str = Field(..., description="API version")
    description: Optional[str] = Field(None, description="API description")
    content_type: str = Field(..., description="Content type (json/yaml)")

    class Config:
        json_schema_extra = {
            "example": {
                "spec_id": "550e8400-e29b-41d4-a716-446655440000",
                "size": 1234,
                "num_chunks": 15,
                "title": "Petstore API",
                "version": "1.0.0",
                "description": "A sample API for managing pets",
                "content_type": "yaml"
            }
        }
