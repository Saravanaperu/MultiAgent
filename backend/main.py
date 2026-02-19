from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import socketio
import asyncio
import redis.asyncio as redis
import json
from routers import user

app = FastAPI(title="Options Scalping Backend")
app.include_router(user.router)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO setup (mounting on FastAPI)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# Redis connection
redis_client = redis.Redis(host='redis', port=6379, db=0)

async def subscribe_to_market_data():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe('market:tick')
    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                await sio.emit('market:tick', data)
            except Exception as e:
                print(f"Error forwarding tick: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(subscribe_to_market_data())

@app.get("/")
async def root():
    return {"message": "Options Scalping System API is running"}

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
