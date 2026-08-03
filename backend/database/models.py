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


@dataclass
class ChatSession:
    """AI 会话数据模型"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    title: Optional[str] = None
    ledger_id: Optional[int] = None  # 会话锁定的账本ID，开启对话后不可切换
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ChatMessage:
    """AI 聊天消息数据模型"""
    id: Optional[int] = None
    session_id: Optional[int] = None
    role: Optional[str] = None  # user / assistant
    content: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Memory:
    """回忆空间数据模型"""
    id: Optional[int] = None
    user_id: Optional[int] = None  # 关联用户ID（一人一回忆）
    partner_name: str = None  # 对象名称
    partner_avatar: Optional[str] = None  # 对象头像相对路径
    story: Optional[str] = None  # 寄语/简介
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'partner_name': self.partner_name,
            'partner_avatar': self.partner_avatar,
            'story': self.story,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }


@dataclass
class MemoryEvent:
    """回忆事件数据模型"""
    id: Optional[int] = None
    memory_id: Optional[int] = None  # 关联回忆ID
    title: str = None  # 事件标题
    event_date: str = None  # 事件日期，格式: YYYY-MM-DD
    description: Optional[str] = None  # 事件描述
    location: Optional[str] = None  # 地点
    cover_path: Optional[str] = None  # 封面图相对路径
    author: str = 'user'  # 事件主体：user(当前用户) / partner(对象)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'memory_id': self.memory_id,
            'title': self.title,
            'event_date': self.event_date,
            'description': self.description,
            'location': self.location,
            'cover_path': self.cover_path,
            'author': self.author,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }


@dataclass
class MemoryPhoto:
    """回忆照片数据模型"""
    id: Optional[int] = None
    event_id: Optional[int] = None  # 关联事件ID
    image_path: str = None  # 图片相对路径，如 uploads/20260119/1.png
    caption: Optional[str] = None  # 照片说明
    created_at: Optional[datetime] = None
    is_deleted: bool = False

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'event_id': self.event_id,
            'image_path': self.image_path,
            'caption': self.caption,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_deleted': self.is_deleted
        }
