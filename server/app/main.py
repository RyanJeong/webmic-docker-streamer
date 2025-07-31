"""FastAPI application that

1. Serves the Web UI (optional – you can host it anywhere).
2. Accepts microphone data from browser producers over `/ws/producer`.
3. Broadcasts each chunk to every connected consumer on `/ws/consumer`.
"""

import asyncio
from pathlib import Path
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI()

# In-memory fan-out: one writer (browser), many readers (Python apps)
consumers: Set[WebSocket] = set()


@app.get("/")
async def index() -> HTMLResponse:
    """Serve the static Web UI (handy for local testing)."""
    html_file = Path(__file__).parent.parent.parent / "client" / "index.html"
    return FileResponse(html_file)


# ───────── WebSocket end-points ─────────
@app.websocket("/ws/producer")
async def websocket_producer(ws: WebSocket):
    """Browser connects here and PUSHES binary audio frames."""
    await ws.accept()
    try:
        while True:
            data = await ws.receive_bytes()  # raw PCM / webm chunk
            # broadcast
            for c in consumers:
                try:
                    await c.send_bytes(data)
                except Exception:
                    consumers.discard(c)
    except WebSocketDisconnect:
        pass


@app.websocket("/ws/consumer")
async def websocket_consumer(ws: WebSocket):
    """Backend Python app connects here and RECEIVES the stream."""
    await ws.accept()
    consumers.add(ws)
    try:
        while True:
            await asyncio.sleep(60)  # keep connection open
    except WebSocketDisconnect:
        consumers.discard(ws)
