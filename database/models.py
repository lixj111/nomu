"""数据库模型定义"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Account:
    """账目数据模型"""
    id: Optional[int] = None
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
