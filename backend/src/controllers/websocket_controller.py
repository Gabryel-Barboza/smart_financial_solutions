from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from src.schemas import StatusOutput

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        # Garante que a chave existe antes de tentar deletar
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_status_update(self, session_id: str, data: StatusOutput):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)


manager = ConnectionManager()


@router.websocket('/websocket/{session_id}')
async def websocket_endpoint(ws: WebSocket, session_id: str):
    await manager.connect(session_id, ws)
    try:
        while ws.client_state != WebSocketState.DISCONNECTED:
            # Mantém a conexão viva aguardando mensagens.
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    finally:
        manager.disconnect(session_id)
