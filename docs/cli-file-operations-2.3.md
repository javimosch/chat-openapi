# CLI File Operations Documentation (v2.3)

## Overview

Version 2.3 introduces vector storage integration into the CLI file operations, enabling efficient storage and retrieval of OpenAPI specification chunks. This document details the available commands and their functionality.

## Commands

### Upload

Upload an OpenAPI specification file to the system:

```bash
./chatapi upload <file_path>
```

Features:
- Validates JSON/YAML format
- Performs OpenAPI specification validation
- Chunks the specification for vector storage
- Generates a unique specification ID
- Displays upload summary with chunk information

Example output:
```
Successfully uploaded petstore.yaml
Specification ID: 550e8400-e29b-41d4-a716-446655440000
Title: Petstore API
Version: 1.0.0
Size: 45.2 KB
Format: YAML
Chunks: 15
```

### List

List all uploaded specifications:

```bash
./chatapi list
```

Features:
- Displays all uploaded specifications in a tabular format
- Shows specification ID, name, size, chunk count, and modification date
- Sorts by most recently modified

Example output:
```
ID                                    Name           Size    Chunks  Modified
------------------------------------ -------------- ------- ------- -------------------
550e8400-e29b-41d4-a716-446655440000 petstore.yaml  45.2 KB 15      2024-01-20 10:30:15
71f0d6a0-54c7-42c1-a53c-3a63c65e3ef4 users.json     12.8 KB 8       2024-01-19 15:45:30
```

### Info

View detailed information about a specific specification:

```bash
./chatapi info <spec_id>
```

Features:
- Shows comprehensive specification metadata
- Displays chunk statistics
- Includes creation and modification timestamps

Example output:
```
File Information
ID: 550e8400-e29b-41d4-a716-446655440000
Name: petstore.yaml
Size: 45.2 KB
Format: YAML
Chunks: 15
Created: 2024-01-20 10:30:15
Modified: 2024-01-20 10:30:15
```

### Export

Export a specification to a file:

```bash
./chatapi export <spec_id> [output_path]
```

Features:
- Exports in original format (JSON/YAML)
- Optional custom output path
- Maintains original content structure

Example:
```bash
# Export with default name (SPEC_ID_export.yaml)
./chatapi export 550e8400-e29b-41d4-a716-446655440000

# Export with custom name
./chatapi export 550e8400-e29b-41d4-a716-446655440000 ~/exported_spec.yaml
```

### Delete

Remove a specification and its associated chunks:

```bash
./chatapi delete <spec_id>
```

Features:
- Removes file from storage
- Deletes associated vector chunks
- Cleans up all related metadata

## Vector Storage Integration

### Chunk Types

1. **Info Chunks**
   - Title and version information
   - API description
   - Terms of service
   - Contact information

2. **Path Chunks**
   - Endpoint paths
   - HTTP methods
   - Parameters
   - Request/response schemas

3. **Component Chunks**
   - Schema definitions
   - Security schemes
   - Parameters
   - Response objects

### Storage Architecture

The vector storage system (Qdrant) maintains:
- Separate collections per specification
- Metadata preservation
- Cross-reference capabilities
- Efficient retrieval patterns

## Error Handling

The CLI provides clear error messages for common scenarios:
- Invalid file formats
- Missing specifications
- Processing errors
- Storage failures

All errors are color-coded for better visibility and logged for debugging purposes.

## Best Practices

1. **File Management**
   - Use meaningful filenames
   - Keep specifications under 10MB
   - Regularly clean up unused specifications
   - Export backups of important specifications

2. **Performance**
   - Large specifications are automatically chunked
   - Vector storage is optimized for quick retrieval
   - Batch operations are handled efficiently

3. **Organization**
   - Use the list command to maintain overview
   - Delete unused specifications
   - Keep track of specification IDs
   - Export specifications before major changes
