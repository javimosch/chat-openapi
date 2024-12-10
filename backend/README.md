# Chat OpenAPI Backend

FastAPI-based backend service for the Chat OpenAPI application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory:
```bash
# .env example
LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000  # Comma-separated list of allowed origins
# Add other environment variables as needed
```

## Running the Application

### Development Mode (with hot reload)

From the project root directory:
```bash
PYTHONPATH=backend uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

This command:
- Sets the `PYTHONPATH` to include the `backend` directory
- Uses `uvicorn` as the ASGI server
- Enables hot reload with `--reload` flag
- Binds to all network interfaces with `--host 0.0.0.0`
- Runs on port 8000

### Production Mode

```bash
PYTHONPATH=backend uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): http://localhost:8000/docs
- Alternative API documentation (ReDoc): http://localhost:8000/redoc

## Features

- FastAPI-based REST API
- WebSocket support for real-time communication
- Environment variable configuration
- CORS middleware
- Automatic API documentation
- Hot reload for development
- Structured logging

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/          # API version 1 routes
│   │   └── routes/      # Additional routes
│   ├── core/            # Core functionality
│   └── main.py         # Application entry point
└── README.md
```

## Health Checks

- `GET /`: Basic health check
- `GET /health`: Detailed health status
