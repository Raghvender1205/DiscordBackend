from fastapi import FastAPI
from app.api.endpoints import router
from app.core.database import engine, Base
from app.services.websockets import websocket_endpoint, WebSocket

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(router, prefix="/auth", tags=["auth"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Discord API"}


@app.websocket("/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: int):
    await websocket_endpoint(websocket, channel_id)

