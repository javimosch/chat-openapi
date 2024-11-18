# CLI Vector Database Management Features (v2.4)

## Overview

Version 2.4 introduces new CLI commands for managing the vector database (Qdrant) directly. These commands provide essential functionality for monitoring and maintaining the vector storage system.

## Proposed Commands

### Vector Database Size

Get the current size of the vector database:

```bash
./chatapi vector size
```

Features:
- Shows total size in MB
- Breaks down size by:
  * Collection storage
  * Index storage
  * Metadata storage
- Optional detailed view with `--detailed` flag

Example output:
```
Vector Database Size
┏━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Component    ┃ Size (MB) ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Collections  │ 256.4     │
│ Indices      │ 128.2     │
│ Metadata     │ 64.8      │
├──────────────┼──────────┤
│ Total        │ 449.4     │
└──────────────┴──────────┘
```

### Remove Embeddings

Remove embeddings for a specific specification:

```bash
./chatapi vector remove <spec_id>
```

Features:
- Removes all vectors associated with the specification
- Preserves the original specification file
- Requires confirmation for safety
- Optional `--force` flag to skip confirmation

Example:
```bash
# With confirmation
./chatapi vector remove 550e8400-e29b-41d4-a716-446655440000
Are you sure you want to remove vectors for spec 550e8400-e29b-41d4-a716-446655440000? [y/N]: y
Successfully removed vectors for specification.

# Force remove
./chatapi vector remove 550e8400-e29b-41d4-a716-446655440000 --force
Successfully removed vectors for specification.
```

### Clear Vector Database

Remove all embeddings from the vector database:

```bash
./chatapi vector clear
```

Features:
- Removes all vectors from the database
- Preserves all specification files
- Requires explicit confirmation
- Optional `--force` flag to skip confirmation
- Can specify collection with `--collection` flag

Example:
```bash
# With confirmation
./chatapi vector clear
Warning: This will remove ALL vectors from the database.
Are you sure you want to proceed? [y/N]: y
Successfully cleared vector database.

# Force clear
./chatapi vector clear --force
Successfully cleared vector database.

# Clear specific collection
./chatapi vector clear --collection openapi_chunks
Successfully cleared collection 'openapi_chunks'.
```

## Implementation Details

### Vector Size Calculation
- Uses Qdrant's collection info API
- Calculates storage size from:
  * Vector data
  * Index structures
  * Payload/metadata

### Vector Removal
- Uses Qdrant's filter-based deletion
- Removes vectors by matching spec_id
- Updates collection statistics

### Database Clearing
- Uses Qdrant's collection deletion API
- Recreates empty collection with same schema
- Maintains configuration settings

## Security Considerations
- Requires confirmation for destructive operations
- Logs all vector management operations
- Maintains specification file integrity

## Error Handling
- Validates spec_id before removal
- Checks collection existence
- Provides clear error messages
- Handles connection issues gracefully

## Future Enhancements
1. Add vector database health check
2. Implement vector backup/restore
3. Add vector optimization commands
4. Support multiple vector collections
5. Add vector statistics and analytics
