# File Upload System Documentation

## Overview

The file upload system is responsible for handling OpenAPI specification files in both JSON and YAML formats. It provides validation, metadata extraction, and secure file storage, forming the foundation for subsequent text processing and vector storage operations.

## Current Implementation

### API Endpoint

```
POST /api/v1/upload
Content-Type: multipart/form-data
```

#### Request Parameters
- `file`: OpenAPI specification file (JSON/YAML)

#### Response Format
```json
{
    "spec_id": "uuid",
    "filename": "original_filename",
    "size_bytes": 1234,
    "message": "Success message"
}
```

### Components

1. **Models** (`app/models/openapi.py`)
   - `OpenAPISpec`: Core data model for OpenAPI specifications
   - `UploadResponse`: API response model

2. **File Service** (`app/services/file_service.py`)
   - File saving with chunked upload
   - OpenAPI validation
   - Metadata extraction
   - Error handling

### Processing Flow

1. **File Upload**
   - Validate file extension (.json, .yaml, .yml)
   - Generate unique filename
   - Save file with chunked reading
   - Track file size

2. **OpenAPI Processing**
   - Parse JSON/YAML content
   - Validate OpenAPI structure
   - Extract metadata (title, version, description)
   - Generate unique spec ID

3. **Response Generation**
   - Return file metadata
   - Include success/error messages
   - Provide spec ID for future reference

### Security Measures

1. **File Validation**
   - Extension checking
   - Content type validation
   - OpenAPI structure verification

2. **Storage Safety**
   - Unique filename generation
   - Secure file paths
   - Cleanup on errors

3. **Error Handling**
   - Detailed error messages
   - Safe error responses
   - Logging of issues

## Planned Integration with Text Chunking (Phase 2.2)

### Processing Pipeline

1. **Initial Processing**
   - Extract all text content from OpenAPI spec
   - Preserve structural relationships
   - Maintain metadata context

2. **Chunking Strategy**
   ```
   OpenAPI Spec
   ├── Info Section
   │   ├── Title & Description
   │   └── Version & Terms
   ├── Paths
   │   ├── Endpoint 1
   │   │   ├── Operations
   │   │   └── Parameters
   │   └── Endpoint 2
   ├── Components
   │   ├── Schemas
   │   └── Security
   └── Tags & External Docs
   ```

3. **Chunk Types**
   - Path-level chunks (endpoint + operations)
   - Schema-level chunks (data models)
   - Component-level chunks (reusable elements)
   - Documentation chunks (descriptions)

4. **Metadata Preservation**
   - Parent-child relationships
   - Cross-references
   - Original locations
   - Context markers

## Planned Integration with Vector Storage (Phase 2.3)

### Storage Architecture

1. **Vector Collection**
   - Collection per OpenAPI spec
   - Chunk vectors with metadata
   - Cross-reference capabilities

2. **Index Structure**
   ```
   Qdrant Collection
   ├── Vectors (embeddings)
   ├── Payload
   │   ├── chunk_type
   │   ├── spec_id
   │   ├── path
   │   └── metadata
   └── Indexes
       ├── spec_id
       └── chunk_type
   ```

3. **Search Capabilities**
   - Semantic similarity search
   - Filtered queries by spec/chunk type
   - Context-aware retrieval

### Integration Points

1. **Upload to Storage Pipeline**
   ```mermaid
   graph LR
   A[File Upload] --> B[Text Chunking]
   B --> C[Embedding Generation]
   C --> D[Vector Storage]
   ```

2. **Metadata Management**
   - Track relationships between chunks
   - Maintain spec versions
   - Enable efficient updates

3. **Performance Considerations**
   - Batch processing for large specs
   - Incremental updates
   - Efficient retrieval patterns

## Future Enhancements

1. **Upload Features**
   - Batch upload support
   - Version control
   - Diff detection
   - Format conversion

2. **Processing Improvements**
   - Parallel processing
   - Custom chunking rules
   - Advanced validation

3. **Storage Optimizations**
   - Caching layer
   - Compression
   - Incremental updates
   - Search optimization

## Usage Examples

### Basic Upload
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@petstore.yaml"
```

### Response Example
```json
{
  "spec_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "petstore.yaml",
  "size_bytes": 12345,
  "message": "OpenAPI specification uploaded successfully"
}
```

## Error Handling

1. **Common Errors**
   - Invalid file format
   - Malformed OpenAPI spec
   - Storage failures
   - Processing timeouts

2. **Error Responses**
   ```json
   {
     "detail": "Error message",
     "status_code": 400,
     "error_type": "ValidationError"
   }
   ```

## Monitoring and Logging

1. **Key Metrics**
   - Upload success rate
   - Processing time
   - File sizes
   - Error frequency

2. **Log Events**
   - Upload attempts
   - Processing stages
   - Validation results
   - Error details

## Best Practices

1. **File Management**
   - Regular cleanup of temporary files
   - Size limits enforcement
   - Format standardization

2. **Error Handling**
   - Graceful degradation
   - Clear error messages
   - Proper logging

3. **Performance**
   - Chunked file handling
   - Async processing
   - Resource management
