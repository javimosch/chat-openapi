"""
Models for OpenAPI specification chunks and metadata.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ChunkMetadata(BaseModel):
    """Metadata for a chunk of an OpenAPI specification."""
    spec_id: str = Field(..., description="ID of the OpenAPI specification")
    chunk_id: str = Field(..., description="Unique identifier for this chunk")
    path: Optional[str] = Field(None, description="API path for path-based chunks")
    method: Optional[str] = Field(None, description="HTTP method for path-based chunks")
    component_type: Optional[str] = Field(None, description="Type of component (e.g., schema, response)")
    component_name: Optional[str] = Field(None, description="Name of the component")
    parent_type: Optional[str] = Field(None, description="Type of parent element")
    parent_name: Optional[str] = Field(None, description="Name of parent element")

class Chunk(BaseModel):
    """A chunk of an OpenAPI specification with its metadata."""
    text: str = Field(..., description="The chunk text content")
    metadata: ChunkMetadata = Field(..., description="Metadata about this chunk")
    vector: Optional[list[float]] = Field(None, description="Vector embedding of the chunk")

    class Config:
        json_schema_extra = {
            "example": {
                "text": '{\n  "type": "object",\n  "properties": {...}\n}',
                "metadata": {
                    "spec_id": "petstore",
                    "chunk_id": "petstore_component_schema_Pet",
                    "component_type": "schema",
                    "component_name": "Pet"
                }
            }
        }
