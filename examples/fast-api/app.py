from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def get():
    return {"message": "Hello World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo the received message back with a prefix
            await websocket.send_text(f"Server received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
