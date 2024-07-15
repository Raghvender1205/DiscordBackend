from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import User, Channel, Message
from app.core.database import get_db
from datetime import datetime


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel_id: int):
        await websocket.accept()
        if channel_id not in self.active_connections:
            self.active_connections[channel_id] = []
        self.active_connections[channel_id].append(websocket)

    def disconnect(self, websocket: WebSocket, channel_id: int):
        self.active_connections[channel_id].remove(websocket)
        if not self.active_connections[channel_id]:
            del self.active_connections[channel_id]

    async def broadcast(self, message: str, channel_id: int):
        for connection in self.active_connections.get(channel_id, []):
            await connection.send_text(message)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, channel_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket, channel_id)
    try:
        while True:
            data = await websocket.receive_text()
            user_email = websocket.headers.get("user-email")
            user = db.query(User).filter(User.email == user_email).first()
            if not user:
                raise HTTPException(status_code=404, detail="Invalid User")
            # Save to db
            message = Message(content=data, user_id=user.id, channel_id=channel_id, timestamp=datetime.utcnow())
            db.add(message)
            db.commit()
            db.refresh(message)

            await manager.broadcast(data, channel_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id)
