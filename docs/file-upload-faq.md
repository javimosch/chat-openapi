# File Upload FAQ

## Storage and Persistence

### Q: Where are files persisted before the 2.2 implementation?

Currently, uploaded files are stored in the `uploads` directory within the application's working directory. This is a temporary solution before implementing text chunking and vector storage in Phase 2.2.

**Details:**
- Location: `./uploads/` directory
- File naming: UUID-based unique filenames (e.g., `550e8400-e29b-41d4-a716-446655440000.yaml`)
- Storage structure:
  ```
  uploads/
  ├── [uuid1].yaml
  ├── [uuid2].json
  └── [uuid3].yml
  ```

**Important Notes:**
1. This is a temporary storage solution
2. Files are not automatically cleaned up
3. No database persistence of file metadata yet
4. Directory is created if it doesn't exist
5. Files retain their original extension but get a new UUID-based name

**Limitations:**
- No file deduplication
- No version control
- Files persist until manually deleted
- Metadata only exists in memory
- No backup mechanism

### Q: How do I manage the uploaded files?

1. **Accessing Files**:
   ```python
   # Files are stored in the uploads directory
   file_path = Path("uploads") / f"{spec_id}{extension}"
   ```

2. **Manual Cleanup**:
   ```bash
   # Remove all files in uploads directory
   rm -rf uploads/*
   
   # Remove specific file
   rm uploads/[uuid].yaml
   ```

3. **Finding a File**:
   ```python
   from pathlib import Path
   
   def find_spec(spec_id: str) -> Path:
       uploads_dir = Path("uploads")
       for ext in [".json", ".yaml", ".yml"]:
           file_path = uploads_dir / f"{spec_id}{ext}"
           if file_path.exists():
               return file_path
       return None
   ```

### Q: What happens to files during container restarts?

1. **Default Behavior**:
   - Files persist if using a mounted volume
   - Files are lost if no volume is mounted
   - No automatic cleanup on restart

2. **Docker Configuration**:
   ```yaml
   services:
     api:
       volumes:
         - ./uploads:/app/uploads  # Persists files across restarts
   ```

3. **Recommendations**:
   - Mount a volume for development
   - Implement cleanup routines
   - Monitor disk usage
   - Back up important files

### Q: How to implement file cleanup?

**Short-term Solution** (before Phase 2.2):
```python
from pathlib import Path
import time

def cleanup_old_files(max_age_hours: int = 24):
    """Remove files older than specified hours"""
    uploads_dir = Path("uploads")
    current_time = time.time()
    
    for file_path in uploads_dir.glob("*"):
        file_age = current_time - file_path.stat().st_mtime
        if file_age > (max_age_hours * 3600):
            file_path.unlink()
```

**Usage**:
```python
# In your FastAPI application
@app.on_event("startup")
async def startup_event():
    # Clean files older than 24 hours
    cleanup_old_files(24)
```

### Q: What happens after Phase 2.2?

After implementing text chunking and vector storage:

1. **File Processing Flow**:
   ```
   Upload → Parse → Chunk → Vectorize → Store → Delete Original
   ```

2. **Storage Changes**:
   - Files will be processed immediately
   - Original files optionally retained
   - Chunks stored in vector database
   - Metadata stored in structured format

3. **Benefits**:
   - Reduced disk usage
   - Better organization
   - Improved searchability
   - Proper version control

### Q: How to monitor storage usage?

1. **Check Directory Size**:
   ```python
   def get_uploads_size():
       total = 0
       uploads_dir = Path("uploads")
       for file_path in uploads_dir.glob("*"):
           total += file_path.stat().st_size
       return total
   ```

2. **Monitor via Logs**:
   ```python
   logger.info(
       "Storage status",
       extra={
           "total_files": len(list(Path("uploads").glob("*"))),
           "total_size_mb": get_uploads_size() / (1024 * 1024)
       }
   )
   ```

3. **Set Up Alerts**:
   ```python
   def check_storage_limits(max_size_mb: int = 1000):
       current_size = get_uploads_size() / (1024 * 1024)
       if current_size > max_size_mb:
           logger.warning(
               "Storage limit exceeded",
               extra={"current_size_mb": current_size, "limit_mb": max_size_mb}
           )
   ```

### Q: How to handle large files?

1. **Current Approach**:
   - Chunked upload processing
   - 8KB buffer size
   - No strict size limits

2. **Recommended Limits**:
   ```python
   # In your settings
   MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
   
   # In upload endpoint
   if file.size > MAX_UPLOAD_SIZE:
       raise HTTPException(status_code=413, detail="File too large")
   ```

3. **Future Improvements**:
   - Streaming processing
   - Progress tracking
   - Resume capability
   - Compression support
