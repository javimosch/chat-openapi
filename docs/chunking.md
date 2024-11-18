# OpenAPI Specification Chunking

This document describes the chunking strategy used to break down OpenAPI specifications into meaningful pieces for vector storage and retrieval.

## Overview

The chunking system divides OpenAPI specifications into logical segments that preserve the semantic meaning and relationships between different parts of the API. This approach enables more accurate retrieval and better context preservation when searching through specifications.

## Chunk Types

### 1. Info Chunks
- Contains basic API information
- Includes title, description, version
- Single chunk per specification
- Metadata: `component_type="info"`

### 2. Path Chunks
- One chunk per path+method combination
- Includes operation details, parameters, responses
- Preserves HTTP method context
- Metadata includes:
  - `path`: The endpoint path
  - `method`: HTTP method (GET, POST, etc.)

### 3. Component Chunks
- Separate chunks for each component
- Types include schemas, responses, parameters
- Preserves component relationships
- Metadata includes:
  - `component_type`: Type of component
  - `component_name`: Name of the component

## Metadata Structure

Each chunk includes metadata for context preservation:

```python
{
    "spec_id": str,      # Unique identifier for the specification
    "chunk_id": str,     # Unique identifier for the chunk
    "path": str,         # For path chunks
    "method": str,       # For path chunks
    "component_type": str,  # For component chunks
    "component_name": str,  # For component chunks
    "parent_type": str,  # For nested components
    "parent_name": str   # For nested components
}
```

## Example Chunks

### Info Chunk
```json
{
    "text": {
        "title": "Petstore API",
        "version": "1.0.0",
        "description": "A sample API for pets"
    },
    "metadata": {
        "spec_id": "petstore",
        "chunk_id": "petstore_info",
        "component_type": "info"
    }
}
```

### Path Chunk
```json
{
    "text": {
        "summary": "Get pet by ID",
        "parameters": [...],
        "responses": {...}
    },
    "metadata": {
        "spec_id": "petstore",
        "chunk_id": "petstore_path_/pets/{id}_get",
        "path": "/pets/{id}",
        "method": "get"
    }
}
```

### Component Chunk
```json
{
    "text": {
        "type": "object",
        "properties": {...}
    },
    "metadata": {
        "spec_id": "petstore",
        "chunk_id": "petstore_component_schema_Pet",
        "component_type": "schema",
        "component_name": "Pet"
    }
}
```

## Implementation Details

### Chunking Process
1. Parse OpenAPI specification
2. Extract info section
3. Process paths and operations
4. Process components
5. Generate metadata for each chunk
6. Prepare chunks for vector storage

### Code Example
```python
# Create chunks from a specification
chunker = OpenAPIChunker()
chunks = chunker.process_specification(spec_path)

# Each chunk contains:
for text, metadata in chunks:
    print(f"Chunk ID: {metadata['chunk_id']}")
    print(f"Content: {text[:100]}...")
```

## Best Practices

1. **Chunk Size**
   - Keep chunks focused on single concepts
   - Avoid splitting related information
   - Preserve context in metadata

2. **Metadata**
   - Include all relevant relationships
   - Use consistent naming
   - Preserve hierarchy information

3. **Processing**
   - Validate chunks before storage
   - Log chunk creation for debugging
   - Handle errors gracefully

## Vector Storage Integration

Chunks are prepared for vector storage by:
1. Converting text to embeddings
2. Storing metadata alongside vectors
3. Creating efficient indexes for retrieval

## Error Handling

The chunking system handles various error cases:
- Invalid OpenAPI specs
- Missing required fields
- Malformed components
- File access issues

## Logging

Comprehensive logging is implemented:
- Chunk creation events
- Processing errors
- Performance metrics
- Validation issues

## Future Improvements

1. **Enhanced Chunking**
   - Smart size optimization
   - Better handling of references
   - Support for OpenAPI extensions

2. **Performance**
   - Parallel processing
   - Batch operations
   - Caching strategies

3. **Quality**
   - Chunk validation
   - Duplicate detection
   - Relationship verification
