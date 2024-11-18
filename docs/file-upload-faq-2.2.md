# File Upload FAQ (Phase 2.2)

## Overview

### Q: How does file upload work after Phase 2.2 implementation?

The file upload process now includes automatic text chunking:

1. **Upload Process**:
   ```
   Upload → Validate → Parse → Chunk → Store → Response
   ```

2. **Processing Steps**:
   - File validation (JSON/YAML)
   - OpenAPI spec parsing
   - Text chunking
   - Metadata extraction
   - Response generation

3. **Output**:
   ```json
   {
     "spec_id": "550e8400-e29b-41d4-a716-446655440000",
     "size": 1234,
     "num_chunks": 15,
     "title": "Petstore API",
     "version": "1.0.0",
     "description": "A sample API for managing pets",
     "content_type": "yaml"
   }
   ```

### Q: What happens to uploaded files?

1. **Initial Storage**:
   - Files are saved in `uploads/` directory
   - UUID-based filenames
   - Original extension preserved

2. **Chunking**:
   - File is parsed into OpenAPI spec
   - Spec is divided into logical chunks
   - Each chunk gets metadata
   - Chunks prepared for vector storage

3. **Cleanup**:
   - Original file remains for reference
   - Automatic cleanup after configurable period
   - Chunks stored separately from original

### Q: What are the chunks created from my file?

The system creates three types of chunks:

1. **Info Chunks**:
   ```json
   {
     "text": {
       "title": "Petstore API",
       "version": "1.0.0",
       "description": "..."
     },
     "metadata": {
       "spec_id": "petstore",
       "chunk_id": "petstore_info",
       "component_type": "info"
     }
   }
   ```

2. **Path Chunks**:
   ```json
   {
     "text": {
       "summary": "Get pet by ID",
       "parameters": [...],
       "responses": {...}
     },
     "metadata": {
       "spec_id": "petstore",
       "path": "/pets/{id}",
       "method": "get"
     }
   }
   ```

3. **Component Chunks**:
   ```json
   {
     "text": {
       "type": "object",
       "properties": {...}
     },
     "metadata": {
       "spec_id": "petstore",
       "component_type": "schema",
       "component_name": "Pet"
     }
   }
   ```

### Q: How do I manage uploaded files through the CLI?

The CLI now shows chunk information:

1. **Upload**:
   ```bash
   $ ./chatapi upload petstore.yaml
   Successfully uploaded petstore.yaml
   Specification ID: 550e8400-e29b-41d4-a716-446655440000
   Chunks generated: 15
   ```

2. **Info**:
   ```bash
   $ ./chatapi info 550e8400-e29b-41d4-a716-446655440000
   File Name: 550e8400-e29b-41d4-a716-446655440000.yaml
   Size: 45.2 KB
   Chunks: 15
   Created: 2024-01-20 10:30:15
   Modified: 2024-01-20 10:30:15
   Format: YAML
   ```

3. **List**:
   ```bash
   $ ./chatapi list
   Name                                     Size    Chunks  Modified
   petstore.yaml                           45.2 KB  15     2024-01-20 10:30:15
   ```

### Q: What happens during file processing?

1. **Validation Phase**:
   - Check file format (JSON/YAML)
   - Verify OpenAPI spec structure
   - Extract basic metadata

2. **Chunking Phase**:
   - Parse specification
   - Identify chunk boundaries
   - Generate chunk metadata
   - Prepare for vector storage

3. **Storage Phase**:
   - Save original file
   - Store chunks with metadata
   - Generate response data

### Q: How are errors handled?

The system handles various error cases:

1. **File Errors**:
   - Invalid format
   - Corrupted content
   - Size limits
   - Permission issues

2. **Spec Errors**:
   - Invalid OpenAPI format
   - Missing required fields
   - Version mismatches
   - Reference errors

3. **Chunking Errors**:
   - Processing failures
   - Memory limitations
   - Invalid content
   - Metadata errors

### Q: What about performance?

Performance considerations:

1. **File Size**:
   - Recommended: < 10MB
   - Maximum: Configurable
   - Chunking overhead: ~100ms per MB

2. **Chunking**:
   - Async processing
   - Memory-efficient
   - Configurable chunk sizes
   - Batch processing support

3. **Storage**:
   - Efficient metadata indexing
   - Quick retrieval
   - Optimized chunk storage
   - Caching support

### Q: How do I monitor the process?

Monitoring options:

1. **Logs**:
   ```json
   {
     "event": "file_processed",
     "spec_id": "550e8400-e29b-41d4-a716-446655440000",
     "num_chunks": 15,
     "processing_time_ms": 234
   }
   ```

2. **CLI Output**:
   - Progress indicators
   - Error messages
   - Success confirmations
   - Performance stats

3. **API Response**:
   - Processing status
   - Chunk counts
   - Timing information
   - Error details

### Q: What's next after upload?

After successful upload:

1. **Immediate**:
   - File is chunked
   - Metadata extracted
   - Chunks prepared for storage

2. **Next Steps**:
   - Vector embeddings (Phase 2.3)
   - Semantic search
   - Chat interface
   - Advanced querying

3. **Available Operations**:
   - View file details
   - Export chunks
   - Delete file
   - Update metadata

### Q: How do I configure the system?

Configuration options:

```env
# File Upload Settings
UPLOAD_MAX_SIZE=10MB
ALLOWED_EXTENSIONS=.json,.yaml,.yml
CHUNK_MAX_SIZE=1000
CLEANUP_INTERVAL=24h

# Processing Settings
ASYNC_PROCESSING=true
BATCH_SIZE=100
PRESERVE_ORIGINAL=true
CHUNK_OVERLAP=0

# Storage Settings
STORAGE_PATH=uploads
CHUNK_STORAGE=chunks
BACKUP_ENABLED=true
```

### Q: What about security?

Security measures:

1. **File Security**:
   - Format validation
   - Size limits
   - Content scanning
   - Secure storage

2. **Processing Security**:
   - Resource limits
   - Timeout controls
   - Error isolation
   - Sanitized output

3. **Access Control**:
   - API authentication
   - Rate limiting
   - Audit logging
   - Permission checks
