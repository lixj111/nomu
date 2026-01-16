"""账单相关API"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from decimal import Decimal
from database.models import User, Account
from database.operations import DatabaseManager
from schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountListResponse
from schemas.response import ResponseModel
from api.deps import get_db, get_current_user

router = APIRouter(prefix="/accounts", tags=["账单"])


@router.get("", response_model=ResponseModel[AccountListResponse])
async def get_accounts(
    ledger_id: Optional[int] = Query(None, description="账本ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
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
        default_ledger = db.get_default_ledger(current_user.id)
        if default_ledger:
            ledger_id = default_ledger.id
        else:
            return ResponseModel(
                code=200,
                message="success",
                data=AccountListResponse(total=0, page=page, page_size=page_size, pages=0, items=[])
            )

    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

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
    items = [
        AccountResponse(
            id=account.id,
            ledger_id=account.ledger_id,
            transaction_date=account.transaction_date,
            amount=float(account.amount),
            item_name=account.item_name,
            category=account.category,
            merchant_name=account.merchant_name,
            payment_method=account.payment_method,
            transaction_type=account.transaction_type,
            notes=account.notes,
            image_url=account.image_path,
            receipt_type=account.receipt_type,
            confidence=account.confidence,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
        for account in result["items"]
    ]

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
    ledger = db.get_ledger_by_id(account.ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账单"
        )

    return ResponseModel(
        code=200,
        message="success",
        data=AccountResponse(
            id=account.id,
            ledger_id=account.ledger_id,
            transaction_date=account.transaction_date,
            amount=float(account.amount),
            item_name=account.item_name,
            category=account.category,
            merchant_name=account.merchant_name,
            payment_method=account.payment_method,
            transaction_type=account.transaction_type,
            notes=account.notes,
            image_url=account.image_path,
            receipt_type=account.receipt_type,
            confidence=account.confidence,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
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

    account_id = db.add_account(account)
    account.id = account_id

    return ResponseModel(
        code=201,
        message="创建成功",
        data=AccountResponse(
            id=account.id,
            ledger_id=account.ledger_id,
            transaction_date=account.transaction_date,
            amount=float(account.amount),
            item_name=account.item_name,
            category=account.category,
            merchant_name=account.merchant_name,
            payment_method=account.payment_method,
            transaction_type=account.transaction_type,
            notes=account.notes,
            image_url=account.image_path,
            receipt_type=account.receipt_type,
            confidence=account.confidence,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
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
    ledger = db.get_ledger_by_id(account.ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该账单"
        )

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

    return ResponseModel(
        code=200,
        message="更新成功",
        data=AccountResponse(
            id=updated_account.id,
            ledger_id=updated_account.ledger_id,
            transaction_date=updated_account.transaction_date,
            amount=float(updated_account.amount),
            item_name=updated_account.item_name,
            category=updated_account.category,
            merchant_name=updated_account.merchant_name,
            payment_method=updated_account.payment_method,
            transaction_type=updated_account.transaction_type,
            notes=updated_account.notes,
            image_url=updated_account.image_path,
            receipt_type=updated_account.receipt_type,
            confidence=updated_account.confidence,
            created_at=updated_account.created_at,
            updated_at=updated_account.updated_at
        )
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
    ledger = db.get_ledger_by_id(account.ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该账单"
        )

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
        default_ledger = db.get_default_ledger(current_user.id)
        if default_ledger:
            ledger_id = default_ledger.id
        else:
            return ResponseModel(code=200, message="success", data={})

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
        result[date] = [
            AccountResponse(
                id=account.id,
                ledger_id=account.ledger_id,
                transaction_date=account.transaction_date,
                amount=float(account.amount),
                item_name=account.item_name,
                category=account.category,
                merchant_name=account.merchant_name,
                payment_method=account.payment_method,
                transaction_type=account.transaction_type,
                notes=account.notes,
                image_url=account.image_path,
                receipt_type=account.receipt_type,
                confidence=account.confidence,
                created_at=account.created_at,
                updated_at=account.updated_at
            )
            for account in accounts
        ]

    return ResponseModel(
        code=200,
        message="success",
        data=result
    )
