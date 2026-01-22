"""账本相关API"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database.models import User, Ledger
from database.operations import DatabaseManager
from schemas.ledger import LedgerCreate, LedgerUpdate, LedgerResponse
from schemas.response import ResponseModel
from api.deps import get_db, get_current_user

router = APIRouter(prefix="/ledgers", tags=["账本"])


@router.get("", response_model=ResponseModel[List[LedgerResponse]])
async def get_ledgers(
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """获取当前用户的所有账本"""
    ledgers = db.get_ledgers_by_user(current_user.id)

    # 添加账单数量
    result = []
    for ledger in ledgers:
        account_count = db.get_ledger_account_count(ledger.id)
        result.append(LedgerResponse(
            id=ledger.id,
            name=ledger.name,
            description=ledger.description,
            icon=ledger.icon,
            color=ledger.color,
            is_default=ledger.is_default,
            account_count=account_count,
            created_at=ledger.created_at,
            updated_at=ledger.updated_at
        ))

    return ResponseModel(
        code=200,
        message="success",
        data=result
    )


@router.post("", response_model=ResponseModel[LedgerResponse])
async def create_ledger(
    ledger_data: LedgerCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """创建账本"""
    ledger = Ledger(
        user_id=current_user.id,
        name=ledger_data.name,
        description=ledger_data.description,
        icon=ledger_data.icon,
        color=ledger_data.color,
        is_default=False
    )

    try:
        ledger_id = db.create_ledger(ledger)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 重新从数据库获取创建后的账本（包含时间戳）
    created_ledger = db.get_ledger_by_id(ledger_id)
    if not created_ledger:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建账本失败"
        )

    account_count = db.get_ledger_account_count(ledger_id)

    return ResponseModel(
        code=201,
        message="创建成功",
        data=LedgerResponse(
            id=created_ledger.id,
            name=created_ledger.name,
            description=created_ledger.description,
            icon=created_ledger.icon,
            color=created_ledger.color,
            is_default=created_ledger.is_default,
            account_count=account_count,
            created_at=created_ledger.created_at,
            updated_at=created_ledger.updated_at
        )
    )


@router.put("/{ledger_id}", response_model=ResponseModel[LedgerResponse])
async def update_ledger(
    ledger_id: int,
    ledger_data: LedgerUpdate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """更新账本"""
    # 检查账本是否存在且属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账本不存在"
        )

    # 检查名称是否重复
    if ledger_data.name and ledger_data.name != ledger.name:
        if db.check_ledger_name_exists(current_user.id, ledger_data.name, exclude_id=ledger_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账本名称已存在"
            )

    # 更新字段
    if ledger_data.name:
        ledger.name = ledger_data.name
    if ledger_data.description is not None:
        ledger.description = ledger_data.description
    if ledger_data.icon:
        ledger.icon = ledger_data.icon
    if ledger_data.color:
        ledger.color = ledger_data.color

    db.update_ledger(ledger_id, ledger)

    # 获取更新后的账本
    updated_ledger = db.get_ledger_by_id(ledger_id)
    account_count = db.get_ledger_account_count(ledger_id)

    return ResponseModel(
        code=200,
        message="更新成功",
        data=LedgerResponse(
            id=updated_ledger.id,
            name=updated_ledger.name,
            description=updated_ledger.description,
            icon=updated_ledger.icon,
            color=updated_ledger.color,
            is_default=updated_ledger.is_default,
            account_count=account_count,
            created_at=updated_ledger.created_at,
            updated_at=updated_ledger.updated_at
        )
    )


@router.delete("/{ledger_id}", response_model=ResponseModel[dict])
async def delete_ledger(
    ledger_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """删除账本"""
    # 检查账本是否存在且属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账本不存在"
        )

    # 不允许删除默认账本
    if ledger.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除默认账本"
        )

    db.delete_ledger(ledger_id)

    return ResponseModel(
        code=200,
        message="删除成功",
        data=None
    )


@router.patch("/{ledger_id}/default", response_model=ResponseModel[dict])
async def set_default_ledger(
    ledger_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """设置默认账本"""
    # 检查账本是否存在且属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账本不存在"
        )

    db.set_default_ledger(current_user.id, ledger_id)

    return ResponseModel(
        code=200,
        message="设置成功",
        data=None
    )
