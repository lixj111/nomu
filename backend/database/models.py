"""数据库模型定义"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class User:
    """用户数据模型"""
    id: Optional[int] = None
    username: str = None
    email: Optional[str] = None
    hashed_password: str = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Ledger:
    """账本数据模型"""
    id: Optional[int] = None
    user_id: Optional[int] = None  # 关联用户ID
    name: str = None  # 账本名称
    description: Optional[str] = None  # 账本描述
    icon: Optional[str] = None  # 账本图标
    color: Optional[str] = None  # 账本颜色
    is_default: bool = False  # 是否默认账本
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }


@dataclass
class Account:
    """账目数据模型"""
    id: Optional[int] = None
    ledger_id: Optional[int] = None  # 关联账本ID
    transaction_date: str = None  # 格式: YYYY-MM-DD
    amount: Decimal = None
    item_name: str = None
    category: Optional[str] = None
    merchant_name: Optional[str] = None
    payment_method: Optional[str] = None
    transaction_type: str = '支出'
    notes: Optional[str] = None
    image_path: Optional[str] = None
    receipt_type: Optional[str] = None
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'ledger_id': self.ledger_id,
            'transaction_date': self.transaction_date,
            'amount': float(self.amount) if self.amount else None,
            'item_name': self.item_name,
            'category': self.category,
            'merchant_name': self.merchant_name,
            'payment_method': self.payment_method,
            'transaction_type': self.transaction_type,
            'notes': self.notes,
            'image_path': self.image_path,
            'receipt_type': self.receipt_type,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }
