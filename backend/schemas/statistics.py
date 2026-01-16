"""统计分析相关模型"""
from pydantic import BaseModel
from typing import Optional


class CategoryStat(BaseModel):
    """分类统计"""

    category: str
    amount: float
    percentage: float


class TrendData(BaseModel):
    """趋势数据"""

    date: str
    income: float = 0
    expense: float = 0


class OverviewStats(BaseModel):
    """概览统计"""

    total_income: float
    total_expense: float
    balance: float
    account_count: int
    month_expense: float
    month_income: float


class CategoryStatsResponse(BaseModel):
    """分类统计响应"""

    expense_by_category: list[CategoryStat]
    income_by_category: list[CategoryStat]


class TrendStatsResponse(BaseModel):
    """趋势统计响应"""

    trend: list[TrendData]
