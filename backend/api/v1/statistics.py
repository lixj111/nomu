"""统计分析相关API"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timedelta
from database.models import User
from database.operations import DatabaseManager
from schemas.statistics import (
    OverviewStats,
    CategoryStatsResponse,
    TrendStatsResponse,
    CategoryStat,
    TrendData
)
from schemas.response import ResponseModel
from api.deps import get_db, get_current_user

router = APIRouter(prefix="/statistics", tags=["统计"])


@router.get("/overview/{ledger_id}", response_model=ResponseModel[OverviewStats])
async def get_overview_stats(
    ledger_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """获取账本概览统计"""
    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

    # 获取当前月份的开始和结束日期
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d")
    if now.month == 12:
        month_end = now.replace(year=now.year + 1, month=1, day=1).strftime("%Y-%m-%d")
    else:
        month_end = now.replace(month=now.month + 1, day=1).strftime("%Y-%m-%d")

    # 总统计（所有时间）
    all_stats = db.get_statistics("2020-01-01", "2099-12-31", ledger_id)

    # 本月统计
    month_stats = db.get_statistics(month_start, month_end, ledger_id)

    # 账单总数
    account_count = db.get_ledger_account_count(ledger_id)

    return ResponseModel(
        code=200,
        message="success",
        data=OverviewStats(
            total_income=all_stats["total_income"],
            total_expense=all_stats["total_expense"],
            balance=all_stats["balance"],
            account_count=account_count,
            month_expense=month_stats["total_expense"],
            month_income=month_stats["total_income"]
        )
    )


@router.get("/category/{ledger_id}", response_model=ResponseModel[CategoryStatsResponse])
async def get_category_stats(
    ledger_id: int,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """获取分类统计"""
    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

    # 默认查询本月
    if not start_date or not end_date:
        now = datetime.now()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d")
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1).strftime("%Y-%m-%d")
        else:
            end_date = now.replace(month=now.month + 1, day=1).strftime("%Y-%m-%d")

    # 获取统计数据
    stats = db.get_statistics(start_date, end_date, ledger_id)
    category_stats = stats["category_stats"]

    # 计算总收入和总支出
    total_expense = stats["total_expense"]
    total_income = stats["total_income"]

    # 构建分类统计
    expense_by_category = []
    income_by_category = []

    for category, amounts in category_stats.items():
        expense_amount = amounts.get("支出", 0)
        income_amount = amounts.get("收入", 0)

        if expense_amount > 0:
            expense_by_category.append(
                CategoryStat(
                    category=category or "未分类",
                    amount=expense_amount,
                    percentage=round(expense_amount / total_expense * 100, 2) if total_expense > 0 else 0
                )
            )

        if income_amount > 0:
            income_by_category.append(
                CategoryStat(
                    category=category or "未分类",
                    amount=income_amount,
                    percentage=round(income_amount / total_income * 100, 2) if total_income > 0 else 0
                )
            )

    # 按金额排序
    expense_by_category.sort(key=lambda x: x.amount, reverse=True)
    income_by_category.sort(key=lambda x: x.amount, reverse=True)

    return ResponseModel(
        code=200,
        message="success",
        data=CategoryStatsResponse(
            expense_by_category=expense_by_category,
            income_by_category=income_by_category
        )
    )


@router.get("/trend/{ledger_id}", response_model=ResponseModel[TrendStatsResponse])
async def get_trend_stats(
    ledger_id: int,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    group_by: str = Query("day", description="分组方式：day/month"),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """获取趋势统计"""
    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

    # 默认查询本月
    if not start_date or not end_date:
        now = datetime.now()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d")
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1).strftime("%Y-%m-%d")
        else:
            end_date = now.replace(month=now.month + 1, day=1).strftime("%Y-%m-%d")

    # 查询账单数据
    with db._get_connection() as conn:
        if group_by == "month":
            # 按月分组
            cursor = conn.execute("""
                SELECT
                    strftime('%Y-%m', transaction_date) as date,
                    transaction_type,
                    SUM(amount) as total
                FROM accounts
                WHERE ledger_id = ? AND transaction_date >= ? AND transaction_date < ?
                AND is_deleted = 0
                GROUP BY date, transaction_type
                ORDER BY date
            """, (ledger_id, start_date, end_date))
        else:
            # 按天分组
            cursor = conn.execute("""
                SELECT
                    transaction_date as date,
                    transaction_type,
                    SUM(amount) as total
                FROM accounts
                WHERE ledger_id = ? AND transaction_date >= ? AND transaction_date < ?
                AND is_deleted = 0
                GROUP BY date, transaction_type
                ORDER BY date
            """, (ledger_id, start_date, end_date))

        rows = cursor.fetchall()

    # 构建趋势数据
    trend_dict = {}
    for row in rows:
        date, trans_type, total = row
        if date not in trend_dict:
            trend_dict[date] = {"date": date, "income": 0, "expense": 0}

        if trans_type == "收入":
            trend_dict[date]["income"] = float(total)
        else:
            trend_dict[date]["expense"] = float(total)

    # 转换为列表并排序
    trend = [TrendData(**v) for v in trend_dict.values()]
    trend.sort(key=lambda x: x.date)

    return ResponseModel(
        code=200,
        message="success",
        data=TrendStatsResponse(trend=trend)
    )
