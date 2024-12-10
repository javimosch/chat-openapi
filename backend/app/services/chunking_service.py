"""
Service for chunking OpenAPI specifications into manageable pieces for vector storage.
"""
import json
from typing import Dict, List, Any, Generator, Optional
from pathlib import Path

from ..core.logging import get_logger
from ..core.utils import log_function

logger = get_logger(__name__)

class ChunkMetadata:
    """Metadata for a chunk of an OpenAPI specification."""
    def __init__(
        self,
        spec_id: str,
        chunk_id: str,
        path: Optional[str] = None,
        method: Optional[str] = None,
        component_type: Optional[str] = None,
        component_name: Optional[str] = None,
        parent_type: Optional[str] = None,
        parent_name: Optional[str] = None
    ):
        self.spec_id = spec_id
        self.chunk_id = chunk_id
        self.path = path
        self.method = method
        self.component_type = component_type
        self.component_name = component_name
        self.parent_type = parent_type
        self.parent_name = parent_name

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

class OpenAPIChunker:
    """Handles chunking of OpenAPI specifications."""

    @log_function
    def chunk_specification(
        self, 
        spec: Dict[str, Any], 
        spec_id: str
    ) -> Generator[tuple[str, ChunkMetadata], None, None]:
        """
        Chunk an OpenAPI specification into meaningful pieces.
        
        Args:
            spec: The OpenAPI specification dictionary
            spec_id: The unique identifier for this specification
            
        Yields:
            Tuple of (chunk_text, chunk_metadata)
        """
        # Chunk 1: Basic Info
        if "info" in spec:
            info_text = json.dumps(spec["info"], indent=2)
            metadata = ChunkMetadata(
                spec_id=spec_id,
                chunk_id=f"{spec_id}_info",
                component_type="info"
            )
            yield info_text, metadata
            logger.debug("Generated info chunk", extra={"spec_id": spec_id})

        # Chunk 2: Paths
        if "paths" in spec:
            for path, path_spec in spec["paths"].items():
                for method, operation in path_spec.items():
                    if method in ["get", "post", "put", "delete", "patch"]:
                        operation_text = json.dumps(operation, indent=2)
                        metadata = ChunkMetadata(
                            spec_id=spec_id,
                            chunk_id=f"{spec_id}_path_{path}_{method}",
                            path=path,
                            method=method
                        )
                        yield operation_text, metadata
                        logger.debug(
                            "Generated path chunk", 
                            extra={
                                "spec_id": spec_id,
                                "path": path,
                                "method": method
                            }
                        )

        # Chunk 3: Components
        if "components" in spec:
            for component_type, components in spec["components"].items():
                for component_name, component_spec in components.items():
                    component_text = json.dumps(component_spec, indent=2)
                    metadata = ChunkMetadata(
                        spec_id=spec_id,
                        chunk_id=f"{spec_id}_component_{component_type}_{component_name}",
                        component_type=component_type,
                        component_name=component_name
                    )
                    yield component_text, metadata
                    logger.debug(
                        "Generated component chunk",
                        extra={
                            "spec_id": spec_id,
                            "component_type": component_type,
                            "component_name": component_name
                        }
                    )

    @log_function
    def process_specification(self, spec_path: Path) -> List[tuple[str, Dict[str, Any]]]:
        """
        Process an OpenAPI specification file and return its chunks.
        
        Args:
            spec_path: Path to the specification file
            
        Returns:
            List of (chunk_text, metadata) tuples
        """
        try:
            # Read and parse the specification
            with open(spec_path, 'r') as f:
                spec = json.load(f)
            
            spec_id = spec_path.stem
            chunks = list(self.chunk_specification(spec, spec_id))
            
            logger.info(
                "Successfully chunked specification",
                extra={
                    "spec_id": spec_id,
                    "num_chunks": len(chunks),
                    "spec_path": str(spec_path)
                }
            )
            
            return [(text, meta.to_dict()) for text, meta in chunks]
            
        except Exception as e:
            logger.error(
                "Error chunking specification",
                extra={
                    "spec_path": str(spec_path),
                    "error": str(e)
                }
            )
            raise
