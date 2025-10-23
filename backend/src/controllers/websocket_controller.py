from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.schemas import StatusOutput

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        del self.active_connections[session_id]

    async def send_status_update(self, session_id: str, data: StatusOutput):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)
        else:
            print(
                f'Tried to send status update for session ID with no active connection. Called within service: {data.name}'
            )


manager = ConnectionManager()


@router.websocket('/websocket/{session_id}')
async def websocket_endpoint(ws: WebSocket, session_id: str):
    await manager.connect(session_id, ws)

    try:
        while True:
            await ws.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(session_id)
