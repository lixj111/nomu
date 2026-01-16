"""API依赖注入"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.operations import DatabaseManager
from core.config import settings
from core.security import decode_access_token
from database.models import User

# HTTP Bearer认证
security = HTTPBearer()


def get_db() -> Generator[DatabaseManager, None, None]:
    """获取数据库连接"""
    db = DatabaseManager(db_path=settings.DB_PATH)
    try:
        yield db
    finally:
        pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: DatabaseManager = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码令牌
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 查询用户
    user = db.get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: DatabaseManager = Depends(get_db)
) -> Optional[User]:
    """获取可选的当前用户（允许未登录）"""
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload is None:
            return None

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        return db.get_user_by_id(int(user_id))
    except Exception:
        return None
