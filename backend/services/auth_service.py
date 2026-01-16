"""认证服务"""
from typing import Optional
from database.models import User
from database.operations import DatabaseManager
from core.security import verify_password, get_password_hash, create_access_token
from core.config import settings


class AuthService:
    """认证服务"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def register(self, username: str, password: str, email: Optional[str] = None) -> User:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            raise ValueError("用户名已存在")

        # 创建用户
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True
        )
        user_id = self.db.create_user(user)
        user.id = user_id

        # 创建默认账本
        from database.models import Ledger
        default_ledger = Ledger(
            user_id=user_id,
            name="默认账本",
            description="系统默认账本",
            icon="book",
            color="#1890ff",
            is_default=True
        )
        self.db.create_ledger(default_ledger)

        return user

    def login(self, username: str, password: str) -> dict:
        """用户登录"""
        # 查询用户
        user = self.db.get_user_by_username(username)
        if not user:
            raise ValueError("用户名或密码错误")

        # 验证密码
        if not verify_password(password, user.hashed_password):
            raise ValueError("用户名或密码错误")

        if not user.is_active:
            raise ValueError("用户已被禁用")

        # 生成访问令牌
        access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    def get_current_user(self, user_id: int) -> Optional[User]:
        """获取当前用户"""
        return self.db.get_user_by_id(user_id)
