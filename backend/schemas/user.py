"""用户相关模型"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    """用户基础信息"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserCreate(UserBase):
    """用户创建请求"""

    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    """用户登录请求"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应"""

    id: int
    is_active: bool = True

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
