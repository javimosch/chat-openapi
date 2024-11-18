# Vector Storage Documentation (Phase 2.3)

## Overview

The vector storage system is responsible for storing and retrieving OpenAPI specification chunks using semantic search capabilities. It uses Qdrant as the vector database and sentence-transformers for generating embeddings.

## Architecture

### Components

1. **VectorStorageService**
   - Core service for managing vector operations
   - Handles chunk storage and retrieval
   - Manages Qdrant collection lifecycle
   - Generates embeddings using sentence-transformers

2. **Integration Points**
   - FileService: For processing uploaded files
   - CLI: For displaying chunk information
   - API: For handling upload responses

## Features

### 1. Vector Storage

- **Collection Management**
  ```python
  collection_name = "openapi_chunks"
  vector_dimension = 384  # all-MiniLM-L6-v2 dimensions
  ```

- **Chunk Storage**
  ```python
  await vector_service.store_chunks(chunks, spec_id)
  ```

- **Chunk Retrieval**
  ```python
  results = await vector_service.search_chunks(query, spec_id, limit=5)
  ```

### 2. CLI Integration

- **File Information**
  ```bash
  $ chatapi info <spec_id>
  File Information
  ID: 550e8400-e29b-41d4-a716-446655440000
  Name: petstore.yaml
  Size: 45.2 KB
  Chunks: 15
  ...
  ```

- **List Command**
  ```bash
  $ chatapi list
  ID                                       Name           Size     Chunks  Modified
  550e8400-e29b-41d4-a716-446655440000    petstore.yaml  45.2 KB  15     2024-01-20 10:30:15
  ```

### 3. API Integration

- **Upload Response**
  ```json
  {
    "spec_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "petstore.yaml",
    "size": 46284,
    "content_type": "yaml",
    "num_chunks": 15
  }
  ```

## Configuration

### Environment Variables

```env
# Qdrant Settings
QDRANT_HOST=localhost
QDRANT_PORT=6333
VECTOR_DIMENSION=384
```

### Docker Setup

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
```

## Implementation Details

### 1. Embedding Generation

- Using sentence-transformers model: 'all-MiniLM-L6-v2'
- Vector dimension: 384
- Distance metric: Cosine similarity

### 2. Chunk Storage Format

```python
PointStruct(
    id=hash(f"{spec_id}_{chunk.metadata.chunk_id}"),
    vector=embedding_vector,
    payload={
        "text": chunk.text,
        "metadata": chunk.metadata.dict(),
        "spec_id": spec_id
    }
)
```

### 3. Search Capabilities

- Semantic search using vector similarity
- Optional filtering by spec_id
- Configurable result limit
- Score-based ranking

## Error Handling

1. **Collection Errors**
   - Automatic collection creation
   - Graceful handling of existing collections

2. **Storage Errors**
   - Batch processing with error handling
   - Detailed error logging
   - Transaction-like behavior

3. **Search Errors**
   - Query validation
   - Fallback strategies
   - Error propagation

## Performance Considerations

1. **Batch Processing**
   - Chunks processed in batches of 100
   - Optimized for memory usage
   - Efficient vector operations

2. **Caching**
   - Model caching for embeddings
   - Collection metadata caching
   - Query result caching (planned)

3. **Resource Usage**
   - Memory-efficient embedding generation
   - Optimized vector storage
   - Scalable architecture

## Best Practices

1. **Vector Storage**
   - Regular collection maintenance
   - Periodic backups
   - Performance monitoring

2. **Embedding Generation**
   - Text preprocessing
   - Batch size optimization
   - Model versioning

3. **Query Optimization**
   - Use appropriate limits
   - Include relevant filters
   - Monitor query performance

## Future Improvements

1. **Features**
   - Advanced filtering options
   - Bulk operations
   - Real-time updates

2. **Performance**
   - Query caching
   - Index optimization
   - Parallel processing

3. **Integration**
   - Additional vector databases
   - More embedding models
   - Enhanced CLI tools
