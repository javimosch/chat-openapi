"""
API endpoints for file upload and processing.
"""
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ...core.logging import get_logger
from ...services.file_service import FileService
from ...models.openapi import UploadResponse

router = APIRouter()
logger = get_logger(__name__)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload an OpenAPI specification file"""
    try:
        # Validate file
        if not file.filename.lower().endswith(('.json', '.yaml', '.yml')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Must be JSON or YAML"
            )
            
        file_service = FileService()
        
        # Save file and get spec ID
        spec_id = await file_service.save_file(file)
        
        # Process file asynchronously
        file_path = file_service._get_file_path(spec_id)
        await file_service.process_file(file_path, spec_id)
        
        # Get file info for response
        file_info = file_service.get_file_info(spec_id)
        chunk_count = await file_service.vector_service.get_chunk_count(spec_id)
        
        return UploadResponse(
            spec_id=spec_id,
            filename=file_info.filename,
            size=file_info.size,
            content_type=file_info.content_type,
            num_chunks=chunk_count
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
