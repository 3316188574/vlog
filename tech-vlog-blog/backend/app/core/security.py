import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from ..database import get_db
from ..models import User

security = HTTPBearer()

# ========== 密码哈希函数 ==========
def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = secrets.token_hex(16)
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() + ":" + salt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    if not hashed_password:
        return False
    if ":" not in hashed_password:
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    hash_value, salt = hashed_password.split(":")
    return hash_value == hashlib.sha256(f"{salt}{plain_password}".encode()).hexdigest()


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """解码 JWT token"""
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户（需要 is_admin=True）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user