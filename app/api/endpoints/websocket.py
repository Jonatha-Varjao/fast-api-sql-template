from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.api.endpoints.websocket_manager import manager
from app.infrastructure.cache.redis_client import redis_client
from app.application.auth.factory import get_oauth2_provider

router = APIRouter()

@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str, token: str = Query(...)):
    try:
        provider = get_oauth2_provider()
        user_info = await provider.validate_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(channel, {"sender": user_info.sub, "data": data})
            await redis_client.publish(f"ws:{channel}", {"sender": user_info.sub, "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)