# webmic-docker-streamer

Cross-platform **browser-to-Docker microphone streaming** example  

| Layer | Tech | Role |
|-------|------|------|
| **Client** | Chrome (latest) | Captures mic with `getUserMedia`, pushes 1-second chunks over **WebSocket** |
| **Server (container)** | FastAPI + uvicorn | Receives chunks on `/ws/producer`, broadcasts to any `/ws/consumer` |
| **Downstream** | Plain Python | Simple `consumer.py` shows how *another* app can tap the live stream |

## Repository Layout

```text
server/           : Docker image (Ubuntu 18.04 + Python 3.8)
  app/main.py     : FastAPI + WS broadcaster
  app/consumer.py : Example downstream client
client/           : Static files served by the API (optional)
README.md         : You are here
```

## Quick Start

```bash
# 1. clone
git clone https://github.com/ryanjeong/webmic-docker-streamer.git
cd webmic-docker-streamer

# 2. build + run the Ubuntu 18.04 image
docker build -t webmic-server -f server/Dockerfile .
docker run --rm --name webmic -p 33333:33333 webmic-server
```

Open <http://localhost:33333> in Chrome, grant mic permission, and Start.
In another terminal:

```bash
docker inspect -f '{{.Id}}' webmic
docker exec -it webmic python /srv/app/app/consumer.py
```
