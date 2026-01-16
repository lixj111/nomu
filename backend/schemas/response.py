"""通用响应模型"""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """通用API响应"""

    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")


class PaginationResponse(BaseModel):
    """分页响应"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")
