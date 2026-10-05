from typing import Generator, Optional, List
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.models.company import CompanyMember
from app.models.system import OperationLog, UserSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def authenticate_token(db: Session, token: str, token_type: str = "access") -> User:
    payload = decode_token(token)
    if not payload or payload.get("type", "access") != token_type:
        raise HTTPException(401, "登录凭证无效或已过期，请重新登录")
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(401, "登录凭证异常")
    session = db.query(UserSession).filter_by(jti=payload.get("jti"), user_id=user_id).first()
    if not session or session.revoked_at is not None:
        raise HTTPException(401, "会话已失效，请重新登录")
    user = db.query(User).filter_by(id=user_id).first()
    if not user or user.status != "ACTIVE":
        raise HTTPException(403, "账号已被禁用或不存在")
    return user


def get_current_user(db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    return authenticate_token(db, token) if token else None

def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录后操作"
        )
    return current_user

def require_roles(allowed_roles: List[str]):
    def role_checker(
        current_user: User = Depends(require_auth),
        db: Session = Depends(get_db)
    ) -> User:
        user_roles = [r.role_code for r in current_user.roles]
        # Super admin always has bypass
        if "SUPER_ADMIN" in user_roles:
            return current_user
        # Check if any allowed role matches
        if any(role in allowed_roles for role in user_roles):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，您无权访问该资源或执行此操作"
        )
    return role_checker

def get_enterprise_member(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
) -> CompanyMember:
    member = db.query(CompanyMember).filter(
        CompanyMember.user_id == current_user.id,
        CompanyMember.status == "ACTIVE"
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您未加入任何企业或企业账号已被停用"
        )
    if member.company.status == "SUSPENDED":
        raise HTTPException(403, "该企业已被停用")
    return member

def log_operation(
    db: Session,
    actor_id: Optional[int],
    actor_name: str,
    role: str,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    detail: Optional[str] = None
):
    log = OperationLog(
        actor_id=actor_id,
        actor_name=actor_name,
        role=role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail
    )
    db.add(log)
    try:
        db.commit()
    except Exception:
        db.rollback()
