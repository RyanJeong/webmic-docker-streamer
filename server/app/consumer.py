#!/usr/bin/env python3
"""
WebSocket consumer

• Connects to ws://127.0.0.1:33333/ws/consumer
• Each 1-second frame is 22,050 x 4B = 88,200 B (Float32, little-endian)
• Prints "frame N  |  mean approx ..." when data arrives
• Sits idle (no error) while producer is stopped
"""

import asyncio
import struct
import websockets

WS_URL = "ws://127.0.0.1:33333/ws/consumer"
FRAME_BYTES = 22_050 * 4  # 88 200 B
BYTES_PER_F = 4  # Float32


def mean_abs_float32(buf: bytes) -> float:
    """Rough average"""
    total = 0.0
    count = len(buf) // BYTES_PER_F
    for (sample,) in struct.iter_unpack("<f", buf):
        total += abs(sample)
    return total / count if count else 0.0


async def main() -> None:
    frame_no = 0
    async with websockets.connect(WS_URL) as ws:
        async for msg in ws:  # silently waits when no data
            if len(msg) != FRAME_BYTES:
                print(f"[WARN] unexpected size {len(msg)} B")
                continue
            frame_no += 1
            level = mean_abs_float32(msg)
            print(f"frame {frame_no:5d} | mean approx {level:7.5f}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
