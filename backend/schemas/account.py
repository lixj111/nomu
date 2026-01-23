"""账单相关模型"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AccountBase(BaseModel):
    """账单基础信息"""

    transaction_date: str = Field(..., description="交易日期 YYYY-MM-DD")
    amount: Decimal = Field(..., ge=0, description="金额")
    item_name: str = Field(..., max_length=200, description="商品/服务名称")
    category: Optional[str] = Field(None, max_length=50, description="消费分类")
    merchant_name: Optional[str] = Field(None, max_length=100, description="商户名称")
    payment_method: Optional[str] = Field(None, max_length=20, description="支付方式")
    transaction_type: str = Field("支出", description="交易类型：收入/支出")
    notes: Optional[str] = Field(None, description="备注")


class AccountCreate(AccountBase):
    """创建账单请求"""
    ledger_id: int = Field(..., description="账本ID")


class AccountUpdate(BaseModel):
    """更新账单请求"""

    transaction_date: Optional[str] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    item_name: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    merchant_name: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[str] = Field(None, max_length=20)
    transaction_type: Optional[str] = None
    notes: Optional[str] = None


class AccountResponse(AccountBase):
    """账单响应"""

    id: int
    ledger_id: int
    image_url: Optional[str] = None
    receipt_type: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


class AccountListResponse(BaseModel):
    """账单列表响应"""

    total: int
    page: int
    page_size: int
    items: list[AccountResponse]
