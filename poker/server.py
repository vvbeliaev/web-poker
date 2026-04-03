# poker/server.py
from __future__ import annotations
import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
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

# Mount static files if built frontend exists
_static_dir = os.path.join(os.path.dirname(__file__), "..", "build")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
