"""账单相关API"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from decimal import Decimal
from database.models import User, Account
from database.operations import DatabaseManager
from schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountListResponse
from schemas.response import ResponseModel
from api.deps import get_db, get_current_user

router = APIRouter(prefix="/accounts", tags=["账单"])


def _verify_account_owner(account: Account, current_user: User, db: DatabaseManager, action: str = "访问") -> None:
    """验证账单归属，未通过则抛 403；同时收窄 account.ledger_id 类型"""
    if account.ledger_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="账单数据异常：缺少 ledger_id"
        )
    ledger = db.get_ledger_by_id(account.ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"无权{action}该账单"
        )


@router.get("", response_model=ResponseModel[AccountListResponse])
async def get_accounts(
    ledger_id: Optional[int] = Query(None, description="账本ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: Optional[int] = Query(None, description="每页大小（不指定则根据数据量自动调整）"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    category: Optional[str] = Query(None, description="分类"),
    transaction_type: Optional[str] = Query(None, description="交易类型：收入/支出"),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """获取账单列表（分页）"""
    # 如果没有指定账本ID，使用默认账本
    if ledger_id is None:
        assert current_user.id is not None  # 已认证用户必有 id
        default_ledger = db.get_default_ledger(current_user.id)
        if default_ledger:
            ledger_id = default_ledger.id
        else:
            return ResponseModel(
                code=200,
                message="success",
                data=AccountListResponse(total=0, page=page, page_size=page_size or 20, pages=0, items=[])
            )
    assert ledger_id is not None  # 已通过默认账本解析

    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

    # 如果未指定 page_size，先获取总数来决定合适的分页大小
    if page_size is None:
        total = db.get_account_count(
            ledger_id=ledger_id,
            start_date=start_date,
            end_date=end_date,
            category=category,
            transaction_type=transaction_type
        )

        # 根据数据量动态调整 page_size
        if total <= 20:
            page_size = total
        elif total <= 100:
            page_size = 50
        elif total <= 500:
            page_size = 100
        elif total <= 1000:
            page_size = 200
        else:
            page_size = 500

        # 第一页时返回所有数据（无上限）
        if page == 1:
            page_size = total
    else:
        # 限制 page_size 最大值为 10000
        page_size = min(page_size, 10000)

    # 查询账单
    result = db.get_accounts_paginated(
        ledger_id=ledger_id,
        start_date=start_date,
        end_date=end_date,
        category=category,
        transaction_type=transaction_type,
        page=page,
        page_size=page_size
    )

    # 转换为响应格式
    items = [AccountResponse.from_account(account) for account in result["items"]]

    return ResponseModel(
        code=200,
        message="success",
        data=AccountListResponse(
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            pages=result["pages"],
            items=items
        )
    )


@router.get("/{account_id}", response_model=ResponseModel[AccountResponse])
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """获取账单详情"""
    account = db.get_account_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账单不存在"
        )

    # 验证账本属于当前用户
    _verify_account_owner(account, current_user, db, "访问")

    return ResponseModel(
        code=200,
        message="success",
        data=AccountResponse.from_account(account)
    )


@router.post("", response_model=ResponseModel[AccountResponse])
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """创建账单"""
    # 确保ledger_id有效
    ledger = db.get_ledger_by_id(account_data.ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的账本ID"
        )

    # 创建账单
    account = Account(
        ledger_id=account_data.ledger_id,
        transaction_date=account_data.transaction_date,
        amount=Decimal(str(account_data.amount)),
        item_name=account_data.item_name,
        category=account_data.category,
        merchant_name=account_data.merchant_name,
        payment_method=account_data.payment_method,
        transaction_type=account_data.transaction_type,
        notes=account_data.notes
    )

    # add_account 现在返回完整的 Account 对象（包含 id, created_at, updated_at）
    created_account = db.add_account(account)

    return ResponseModel(
        code=201,
        message="创建成功",
        data=AccountResponse.from_account(created_account)
    )


@router.put("/{account_id}", response_model=ResponseModel[AccountResponse])
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """更新账单"""
    account = db.get_account_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账单不存在"
        )

    # 验证账本属于当前用户
    _verify_account_owner(account, current_user, db, "修改")

    # 更新字段
    if account_data.transaction_date:
        account.transaction_date = account_data.transaction_date
    if account_data.amount:
        account.amount = Decimal(str(account_data.amount))
    if account_data.item_name:
        account.item_name = account_data.item_name
    if account_data.category is not None:
        account.category = account_data.category
    if account_data.merchant_name is not None:
        account.merchant_name = account_data.merchant_name
    if account_data.payment_method is not None:
        account.payment_method = account_data.payment_method
    if account_data.transaction_type:
        account.transaction_type = account_data.transaction_type
    if account_data.notes is not None:
        account.notes = account_data.notes

    db.update_account(account_id, account)

    # 获取更新后的账单
    updated_account = db.get_account_by_id(account_id)
    if updated_account is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新后查询失败"
        )

    return ResponseModel(
        code=200,
        message="更新成功",
        data=AccountResponse.from_account(updated_account)
    )


@router.delete("/{account_id}", response_model=ResponseModel[dict])
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """删除账单"""
    account = db.get_account_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账单不存在"
        )

    # 验证账本属于当前用户
    _verify_account_owner(account, current_user, db, "删除")

    db.delete_account(account_id)

    return ResponseModel(
        code=200,
        message="删除成功",
        data=None
    )


@router.get("/by-date/{year}/{month}", response_model=ResponseModel[dict])
async def get_accounts_by_date(
    year: int,
    month: int,
    ledger_id: Optional[int] = Query(None, description="账本ID"),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """按日期获取账单（用于日程视图）"""
    # 如果没有指定账本ID，使用默认账本
    if ledger_id is None:
        assert current_user.id is not None  # 已认证用户必有 id
        default_ledger = db.get_default_ledger(current_user.id)
        if default_ledger:
            ledger_id = default_ledger.id
        else:
            return ResponseModel(code=200, message="success", data={})
    assert ledger_id is not None  # 已通过默认账本解析

    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

    # 查询账单
    accounts_by_date = db.get_accounts_by_date(ledger_id, year, month)

    # 转换为响应格式
    result = {}
    for date, accounts in accounts_by_date.items():
        result[date] = [AccountResponse.from_account(account) for account in accounts]

    return ResponseModel(
        code=200,
        message="success",
        data=result
    )
