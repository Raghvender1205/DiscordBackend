from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.endpoints import router
from app.core.database import engine, Base
from app.services.websockets import websocket_endpoint, WebSocket

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Discord Backend API",
    description="FastAPI based implementation of Discord backend",
    version="1.0.0",
)

app.include_router(router, prefix="/auth", tags=["auth"])


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to Discord API"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Discord API",
        version="1.0.0",
        description="API for Discord",
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    
    return app.openapi_schema


@app.websocket("/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: int):
    await websocket_endpoint(websocket, channel_id)


app.openapi = custom_openapi
