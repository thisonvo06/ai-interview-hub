import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.api.v1.realtime import authenticate_websocket, websocket_session_active

logger = logging.getLogger("notification_ws")


class ConnectionManager:
    """按 user_id 维护通知 WebSocket 连接，支持线程安全广播。"""

    def __init__(self):
        self.active: Dict[int, Set[WebSocket]] = {}
        self._loop = None

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(user_id, set()).add(websocket)
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

    def disconnect(self, user_id: int, websocket: WebSocket):
        conns = self.active.get(user_id)
        if conns:
            conns.discard(websocket)
            if not conns:
                self.active.pop(user_id, None)

    async def _send(self, user_id: int, payload: dict):
        for ws in list(self.active.get(user_id, set())):
            try:
                if not websocket_session_active(ws):
                    await ws.close(code=1008)
                    self.disconnect(user_id, ws)
                    continue
                await ws.send_text(json.dumps(payload, ensure_ascii=False))
            except Exception:
                self.disconnect(user_id, ws)

    def publish(self, user_id: int, payload: dict):
        """线程安全广播：供同步路由在线程池中调用。无活跃连接时静默返回。"""
        if self._loop is None or not self.active.get(user_id):
            return
        try:
            asyncio.run_coroutine_threadsafe(self._send(user_id, payload), self._loop)
        except Exception as e:  # pragma: no cover - 广播失败不影响主流程
            logger.warning(f"通知推送失败: {e}")


manager = ConnectionManager()


async def handle_notification_websocket(websocket: WebSocket, user_id: int):
    if await authenticate_websocket(websocket, "notifications", user_id) is None:
        return
    await manager.connect(user_id, websocket)
    try:
        # 连接建立后回推一次，让前端同步最新未读状态
        await websocket.send_text(json.dumps({"type": "connected"}, ensure_ascii=False))
        while True:
            if not websocket_session_active(websocket):
                await websocket.close(code=1008)
                break
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:  # pragma: no cover
        logger.error(f"通知 WebSocket 异常: {e}")
        manager.disconnect(user_id, websocket)
    finally:
        manager.disconnect(user_id, websocket)
