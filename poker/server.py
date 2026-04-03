# poker/server.py
from __future__ import annotations
import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import HTTPException
import os

from poker.game.tournament import Room

# In-memory room registry: room_id → Room
rooms: dict[str, Room] = {}

# Socket.IO async server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)

# FastAPI app
app = FastAPI()


@app.post("/api/rooms")
async def create_room() -> JSONResponse:
    room = Room()
    rooms[room.id] = room
    return JSONResponse({"room_id": room.id})


# Mount Socket.IO as ASGI middleware wrapping FastAPI
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Serve static frontend with SPA fallback
_static_dir = os.path.join(os.path.dirname(__file__), "..", "build")
if os.path.isdir(_static_dir):
    app.mount("/_app", StaticFiles(directory=os.path.join(_static_dir, "_app")), name="app_assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        file_path = os.path.join(_static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        index = os.path.join(_static_dir, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)
        raise HTTPException(status_code=404)
