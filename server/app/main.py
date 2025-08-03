"""FastAPI application that

1. Serves the Web UI (optional – you can host it anywhere).
2. Accepts microphone data from browser producers over `/ws/producer`.
3. Broadcasts each chunk to every connected consumer on `/ws/consumer`.
"""

import asyncio
from pathlib import Path
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app = FastAPI()

# Static files (Web UI)   /srv/app/client/index.html
BASE_DIR = Path(__file__).resolve().parents[1]  # → /srv/app
STATIC_DIR = BASE_DIR / "client"  # → /srv/app/client


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/app.js")
async def app_js():
    return FileResponse(STATIC_DIR / "app.js", media_type="application/javascript")


# ───────── WebSocket fan-out ─────────
_consumers: Set[WebSocket] = set()


@app.websocket("/ws/producer")
async def ws_producer(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            chunk = await ws.receive_bytes()
            for c in _consumers:
                try:
                    await c.send_bytes(chunk)
                except Exception:
                    _consumers.discard(c)
    except WebSocketDisconnect:
        pass


@app.websocket("/ws/consumer")
async def ws_consumer(ws: WebSocket):
    await ws.accept()
    _consumers.add(ws)
    try:
        while True:
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        _consumers.discard(ws)
