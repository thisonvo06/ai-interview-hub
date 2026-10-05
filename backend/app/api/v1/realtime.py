from datetime import timedelta
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.core.deps import require_auth, oauth2_scheme, authenticate_token
from app.core.security import create_access_token, decode_token
from app.models.interview import Interview
from app.models.user import User
from app.schemas.common import ResponseModel

router = APIRouter(tags=["实时通道认证"])


class TicketRequest(BaseModel):
    channel: Literal["interview", "notifications"]
    resource_id: int


@router.post("/realtime/ticket", response_model=ResponseModel[dict])
def issue_ticket(req: TicketRequest, user: User = Depends(require_auth), token: str = Depends(oauth2_scheme),
                 db: Session = Depends(get_db)):
    if req.channel == "notifications":
        allowed = req.resource_id == user.id
    else:
        allowed = db.query(Interview).filter_by(id=req.resource_id, user_id=user.id).first() is not None
    if not allowed:
        raise HTTPException(403, "无权连接此实时通道")
    claims = decode_token(token)
    ticket = create_access_token(user.id, timedelta(seconds=90), {
        "type": "ws", "jti": claims["jti"], "channel": req.channel,
        "resource_id": req.resource_id, "access_exp": claims["exp"],
    })
    return ResponseModel(data={"ticket": ticket, "expires_in": 90})


async def authenticate_websocket(ws: WebSocket, channel: str, resource_id: int):
    """先鉴权再 accept；仅接受短期且绑定目标资源的凭证。"""
    with SessionLocal() as db:
        try:
            token = ws.query_params.get("ticket") or ""
            user = authenticate_token(db, token, "ws")
            claims = decode_token(token)
            if claims.get("channel") != channel or claims.get("resource_id") != resource_id:
                raise HTTPException(403, "通道不匹配")
            if channel == "notifications" and user.id != resource_id:
                raise HTTPException(403, "无权连接")
            if channel == "interview" and not db.query(Interview).filter_by(id=resource_id, user_id=user.id).first():
                raise HTTPException(403, "无权连接")
            ws.state.auth_claims = claims
            return user.id
        except HTTPException:
            await ws.close(code=1008)
            return None


def websocket_session_active(ws: WebSocket):
    import time
    from app.models.system import UserSession
    claims = ws.state.auth_claims
    if claims.get("access_exp", 0) <= time.time():
        return False
    with SessionLocal() as db:
        return db.query(UserSession).join(User, UserSession.user_id == User.id).filter(
            UserSession.jti == claims["jti"], UserSession.user_id == int(claims["sub"]),
            UserSession.revoked_at.is_(None), User.status == "ACTIVE").first() is not None
