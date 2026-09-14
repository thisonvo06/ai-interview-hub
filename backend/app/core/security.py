import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    # Check if hashed with fallback sha256
    if hashed_password.startswith("sha256$"):
        parts = hashed_password.split("$")
        if len(parts) == 3:
            salt, h = parts[1], parts[2]
            calc = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
            return calc == h
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback comparison if bcrypt has issue in some environment
        return False

def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception:
        salt = os.urandom(8).hex()
        calc = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return f"sha256${salt}${calc}"

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None, extra_claims: dict = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None
