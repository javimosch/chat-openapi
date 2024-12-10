# FastAPI WebSocket Example

This is a simple example demonstrating WebSocket functionality using FastAPI. It includes a WebSocket server that echoes messages back to the client and a web interface for testing the connection.

## Requirements

```bash
pip install fastapi uvicorn
```

## Running the Example

1. Start the FastAPI server:
```bash
python app.py
```
Or alternatively:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

2. Open your web browser and navigate to:
```
http://localhost:8000/static/index.html
```

## Features

- WebSocket server that echoes messages back to the client
- Simple web interface for testing WebSocket connections
- Real-time message display
- Clean and responsive design

## How it Works

1. The server (`app.py`) creates a WebSocket endpoint at `/ws`
2. The web interface (`index.html`) connects to this endpoint and provides a UI for sending/receiving messages
3. Messages sent from the web interface are echoed back by the server with a prefix

## Testing

1. Open the web interface in your browser
2. Type a message in the input field
3. Click "Send" or press Enter
4. You should see your message being echoed back from the server
