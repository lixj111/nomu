"""AI 对话相关 Schema"""
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """单条对话消息"""

    role: str = Field(..., description="user / assistant / system")
    content: str = Field("", description="消息内容")
    name: Optional[str] = Field(None, description="消息作者名（可选）")


class AIChatRequest(BaseModel):
    """AI 对话请求"""

    messages: List[ChatMessage] = Field(..., description="完整对话历史（含本次用户输入）")
    ledger_id: Optional[int] = Field(None, description="前端当前账本ID，仅作提示")
    session_id: Optional[int] = Field(None, description="会话ID（持久化时传入）")
    user_message: Optional[str] = Field(None, description="本次用户提问原文（用于落库）")


class ChatSessionCreate(BaseModel):
    """新建会话请求"""

    title: Optional[str] = Field(None, description="会话标题，默认取首条提问")
    ledger_id: Optional[int] = Field(None, description="会话绑定的账本ID，开启对话后锁定")


class ChatSessionOut(BaseModel):
    """会话信息"""

    id: int = Field(..., description="会话ID")
    title: Optional[str] = Field(None, description="会话标题")
    ledger_id: Optional[int] = Field(None, description="会话绑定的账本ID")
    message_count: int = Field(0, description="消息数量")
    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)


class ChatMessageOut(BaseModel):
    """会话消息"""

    id: int = Field(..., description="消息ID")
    role: str = Field(..., description="user / assistant")
    content: str = Field("", description="消息内容")
    created_at: Optional[datetime] = Field(None)
