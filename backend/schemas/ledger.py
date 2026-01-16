"""账本相关模型"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LedgerBase(BaseModel):
    """账本基础信息"""

    name: str = Field(..., min_length=1, max_length=50, description="账本名称")
    description: Optional[str] = Field(None, max_length=200, description="账本描述")
    icon: Optional[str] = Field("book", description="账本图标")
    color: Optional[str] = Field("#1890ff", description="账本颜色")


class LedgerCreate(LedgerBase):
    """创建账本请求"""


class LedgerUpdate(BaseModel):
    """更新账本请求"""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = None
    color: Optional[str] = None


class LedgerResponse(LedgerBase):
    """账本响应"""

    id: int
    is_default: bool = False
    account_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
