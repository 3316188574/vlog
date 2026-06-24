from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.schemas.common import error

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error(message="未登录或 token 缺失", code=401),
        )
    try:
        payload = decode_token(credentials.credentials)
        # 骨架占位：此处可根据 sub 去数据库查用户
        return {"username": payload.get("sub")}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error(message="token 无效或已过期", code=401),
        )

