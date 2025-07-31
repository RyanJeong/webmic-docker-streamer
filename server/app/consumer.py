#!/usr/bin/env python3
"""
Example downstream programme that connects as a consumer,
stores 1 second chunks into "stream.raw", and prints VU-meter-ish stats.
"""
import asyncio
import websockets
import struct

SINK = open("stream.raw", "wb")  # 16-bit little-endian PCM, 48 kHz by default


def mean_amplitude(buf: bytes) -> float:
    """Rough quick-and-dirty level meter."""
    samples = struct.iter_unpack("<h", buf)  # int16_t little-endian
    return sum(abs(s[0]) for s in samples) / (len(buf) // 2)


async def main():
    uri = "ws://127.0.0.1:33333/ws/consumer"
    async with websockets.connect(uri) as ws:
        print("Connected – recording ... Ctrl-C to stop")
        async for msg in ws:
            SINK.write(msg)
            amp = mean_amplitude(msg)
            print(f"chunk {len(msg):>5} B | amp≈{amp:6.1f}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        SINK.close()
