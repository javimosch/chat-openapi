# Chat-OpenAPI CLI Documentation

The Chat-OpenAPI CLI tool provides a command-line interface for managing OpenAPI specifications in the system.

## Installation

The CLI tool is included in the backend directory. Make sure you have all dependencies installed:

```bash
cd backend
pip install -r requirements.txt
```

## Usage

The CLI can be accessed using the `chatapi` command in the backend directory:

```bash
./chatapi [COMMAND] [ARGUMENTS]
```

## Available Commands

### Upload a Specification

Upload an OpenAPI specification file to the system:

```bash
./chatapi upload PATH_TO_FILE
```

Example:
```bash
./chatapi upload ~/specs/petstore.yaml
```

### List Specifications

List all uploaded OpenAPI specifications:

```bash
./chatapi list
```

This command shows:
- File name
- File size
- Last modified date

### Get Specification Info

View detailed information about a specific OpenAPI specification:

```bash
./chatapi info SPEC_ID
```

Example:
```bash
./chatapi info 550e8400-e29b-41d4-a716-446655440000
```

### Delete a Specification

Remove a specification from the system:

```bash
./chatapi delete SPEC_ID
```

Example:
```bash
./chatapi delete 550e8400-e29b-41d4-a716-446655440000
```

### Export a Specification

Export a specification to a file:

```bash
./chatapi export SPEC_ID [OUTPUT_PATH]
```

Example:
```bash
# Export with default name (SPEC_ID_export.yaml)
./chatapi export 550e8400-e29b-41d4-a716-446655440000

# Export with custom name
./chatapi export 550e8400-e29b-41d4-a716-446655440000 ~/exported_spec.yaml
```

### WebSocket Chat Functionality

The Chat-OpenAPI WebSocket service allows real-time interaction with the chat functionality. Users can send messages and receive responses that utilize context retrieved from the RAG service.

#### How It Works:
1. **Send a Message**: Users send a message to the WebSocket endpoint.
2. **Context Retrieval**: The service retrieves relevant context based on the user's message.
3. **Response Generation**: The context is combined with the user's message to generate a response using the OpenRouter service.
4. **Receive Response**: The response is sent back to the user in real-time.

#### Example Usage:
To interact with the WebSocket service, connect to the WebSocket endpoint and send a message. The service will respond with a context-aware reply.

### Error Handling

The CLI provides clear error messages for common issues:
- File not found
- Invalid file format
- Processing errors
- Missing specifications

All errors are logged and displayed with appropriate color coding for better visibility.

## Examples

1. Upload and view info:
```bash
./chatapi upload ~/specs/petstore.yaml
./chatapi info 550e8400-e29b-41d4-a716-446655440000
```

2. List and export:
```bash
./chatapi list
./chatapi export 550e8400-e29b-41d4-a716-446655440000 ~/exported_spec.yaml
```

3. Delete after listing:
```bash
./chatapi list
./chatapi delete 550e8400-e29b-41d4-a716-446655440000
```

## Notes

- All commands use color-coded output for better readability
- File operations are performed in the `uploads` directory
- Supported file formats: JSON (.json), YAML (.yaml, .yml)
- All operations are logged for debugging purposes
