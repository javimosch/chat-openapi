import uuid
import yaml
import json
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
from fastapi import UploadFile, HTTPException
from datetime import datetime

from ..core.logging import logger
from ..core.utils import log_function
from ..models.openapi import OpenAPISpec
from app.services.chunking_service import OpenAPIChunker
from app.services.vector_storage import VectorStorageService

class FileService:
    """Service for handling file operations."""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.chunking_service = OpenAPIChunker()
        self.vector_service = VectorStorageService()
        logger.info(f"FileService initialized with upload directory: {upload_dir}")
    
    @log_function
    async def save_file(self, file: UploadFile) -> Tuple[Path, int]:
        """Save an uploaded file and return its path and size"""
        if not file.filename:
            raise HTTPException(status_code=400, message="No filename provided")
        
        # Generate unique filename
        ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = self.upload_dir / unique_filename
        
        size = 0
        try:
            with file_path.open("wb") as f:
                while chunk := await file.read(8192):
                    size += len(chunk)
                    f.write(chunk)
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail="Error saving file")
            
        logger.info(
            "File saved successfully",
            extra={
                "file_name": file.filename,
                "file_size": size,
                "file_path": str(file_path)
            }
        )
        return file_path, size
    
    @log_function
    def parse_openapi_spec(self, file_path: Path) -> Dict[str, Any]:
        """Parse OpenAPI spec from file and extract metadata"""
        try:
            content = file_path.read_text()
            
            # Try JSON first
            try:
                spec = json.loads(content)
                content_type = "json"
            except json.JSONDecodeError:
                # Try YAML if JSON fails
                try:
                    spec = yaml.safe_load(content)
                    content_type = "yaml"
                except yaml.YAMLError as e:
                    logger.error(f"Error parsing YAML: {str(e)}")
                    raise HTTPException(
                        status_code=400,
                        detail="File is neither valid JSON nor YAML"
                    )
            
            # Validate basic OpenAPI structure
            if not isinstance(spec, dict):
                raise HTTPException(
                    status_code=400,
                    detail="OpenAPI spec must be a JSON/YAML object"
                )
            
            if "openapi" not in spec:
                raise HTTPException(
                    status_code=400,
                    detail="File is not a valid OpenAPI specification"
                )
            
            logger.info(
                "OpenAPI spec parsed successfully",
                extra={
                    "spec_version": spec.get("openapi"),
                    "spec_title": spec.get("info", {}).get("title"),
                    "spec_format": content_type
                }
            )
            
            return {
                "content_type": content_type,
                "title": spec.get("info", {}).get("title"),
                "version": spec.get("info", {}).get("version"),
                "description": spec.get("info", {}).get("description")
            }
            
        except Exception as e:
            logger.error(f"Error processing OpenAPI spec: {str(e)}")
            if not isinstance(e, HTTPException):
                raise HTTPException(
                    status_code=500,
                    detail="Error processing OpenAPI specification"
                )
            raise

    @log_function
    async def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """Process an uploaded file."""
        try:
            # Save the file
            saved_path, size = await self.save_file(file)
            
            # Parse the OpenAPI spec
            spec_info = self.parse_openapi_spec(saved_path)
            
            # Process the file
            await self._process_file(saved_path, saved_path.stem)
            
            logger.info(
                "File processed successfully",
                extra={
                    "spec_id": saved_path.stem,
                    "file_size": size
                }
            )
            
            return {
                "spec_id": saved_path.stem,
                "size": size,
                **spec_info
            }
            
        except Exception as e:
            logger.error("Error processing file", extra={"error": str(e)})
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    async def _process_file(self, file_path: Path, spec_id: str) -> None:
        """Process uploaded file: parse, chunk, and store vectors"""
        try:
            # Read and parse the file
            logger.info(f"Processing file {file_path}")
            content = file_path.read_text()
            spec = json.loads(content) if file_path.suffix == '.json' else yaml.safe_load(content)
            
            # Generate chunks
            logger.info("Generating chunks")
            chunks = []
            for chunk_text, metadata in self.chunking_service.chunk_specification(spec, spec_id):
                chunks.append({
                    'text': chunk_text,
                    'metadata': metadata.to_dict()
                })
            
            logger.info(f"Generated {len(chunks)} chunks")
            
            # Store chunks in vector storage
            logger.info("Storing chunks in vector storage")
            await self.vector_service.store_chunks(chunks, spec_id)
            
            logger.info(f"Successfully processed file {file_path} with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    async def delete_file(self, spec_id: str) -> None:
        """Delete a file and its associated chunks"""
        try:
            # Find and delete the file
            found = False
            for file_path in self.upload_dir.glob("*"):
                if file_path.stem == spec_id:
                    file_path.unlink()
                    found = True
                    break
            
            if not found:
                raise FileNotFoundError(f"Specification {spec_id} not found")
            
            # Delete from vector storage
            await self.vector_service.delete_spec_chunks(spec_id)
            
            logger.info(f"Successfully deleted file and chunks for spec {spec_id}")
            
        except Exception as e:
            logger.error(f"Error deleting file {spec_id}: {str(e)}")
            raise

    def _get_file_path(self, spec_id: str) -> Path:
        return self.upload_dir / spec_id

    def list_files(self) -> List[Dict[str, Any]]:
        """List all specification files in the upload directory."""
        specs = []
        for file_path in self.upload_dir.glob("*"):
            if file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
                stats = file_path.stat()
                specs.append({
                    "id": file_path.stem,
                    "filename": file_path.name,
                    "size_formatted": f"{stats.st_size / 1024:.1f} KB",
                    "size": stats.st_size,
                    "modified_at": datetime.fromtimestamp(stats.st_mtime),
                    "created_at": datetime.fromtimestamp(stats.st_ctime),
                    "content_type": file_path.suffix.lstrip('.').upper()
                })
        return sorted(specs, key=lambda x: x['modified_at'], reverse=True)

    def get_file_info(self, spec_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific file."""
        for ext in ['.json', '.yaml', '.yml']:
            file_path = self.upload_dir / f"{spec_id}{ext}"
            if file_path.exists():
                stats = file_path.stat()
                return {
                    "id": spec_id,
                    "filename": file_path.name,
                    "size_formatted": f"{stats.st_size / 1024:.1f} KB",
                    "size": stats.st_size,
                    "modified_at": datetime.fromtimestamp(stats.st_mtime),
                    "created_at": datetime.fromtimestamp(stats.st_ctime),
                    "content_type": file_path.suffix.lstrip('.').upper()
                }
        raise FileNotFoundError(f"Specification not found: {spec_id}")
