"""回忆相关模型"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MemoryCreate(BaseModel):
    """创建回忆空间请求"""
    partner_name: str = Field(..., min_length=1, max_length=50, description="对象名称")
    partner_avatar: Optional[str] = Field(None, max_length=500, description="对象头像相对路径")
    story: Optional[str] = Field(None, max_length=500, description="寄语/简介")


class MemoryUpdate(BaseModel):
    """更新回忆空间请求"""
    partner_name: Optional[str] = Field(None, min_length=1, max_length=50)
    partner_avatar: Optional[str] = Field(None, max_length=500)
    story: Optional[str] = Field(None, max_length=500)


class MemoryResponse(BaseModel):
    """回忆空间响应"""
    id: int
    user_id: Optional[int] = None
    partner_name: str
    partner_avatar: Optional[str] = None
    story: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MemoryPhotoResponse(BaseModel):
    """回忆照片响应"""
    id: int
    event_id: Optional[int] = None
    image_path: str
    caption: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MemoryEventCreate(BaseModel):
    """创建回忆事件请求"""
    title: str = Field(..., min_length=1, max_length=200, description="事件标题")
    event_date: str = Field(..., description="事件日期 YYYY-MM-DD")
    description: Optional[str] = Field(None, description="事件描述")
    location: Optional[str] = Field(None, max_length=200, description="地点")
    cover_path: Optional[str] = Field(None, max_length=500, description="封面图相对路径")
    author: str = Field("user", description="事件主体: user(当前用户)/partner(对象)")


class MemoryEventUpdate(BaseModel):
    """更新回忆事件请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    event_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    cover_path: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = None


class MemoryEventResponse(BaseModel):
    """回忆事件响应（含照片列表）"""
    id: int
    memory_id: Optional[int] = None
    title: str
    event_date: str
    description: Optional[str] = None
    location: Optional[str] = None
    cover_path: Optional[str] = None
    author: str = "user"
    photos: List[MemoryPhotoResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
