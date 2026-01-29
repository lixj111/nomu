"""文件上传相关API"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional
from database.models import User
from database.operations import DatabaseManager
from schemas.account import AccountResponse
from schemas.response import ResponseModel
from services.image_service import ImageService
from services.receipt_service import ReceiptService
from api.deps import get_db, get_current_user
from core.config import settings

router = APIRouter(prefix="/upload", tags=["上传"])

logger = logging.getLogger(__name__)

@router.post("/receipt", response_model=ResponseModel[AccountResponse])
async def upload_receipt(
    file: UploadFile = File(...),
    ledger_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """上传并识别账单图片"""
    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

    try:
        # 保存图片
        image_service = ImageService()
        relative_path = await image_service.save_upload_file(file)  # 相对路径，用于数据库存储和前端访问
        full_path = image_service.get_full_path(relative_path)  # 绝对路径，用于AI识别

        # 识别账单
        receipt_service = ReceiptService(db, api_key=settings.ZHIPU_API_KEY)
        account = await receipt_service.recognize_receipt(full_path, relative_path, ledger_id)

        result = ResponseModel(
            code=200,
            message="识别成功",
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
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理失败: {str(e)}"
        )


@router.post("/receipts/batch", response_model=ResponseModel[list[AccountResponse]])
async def batch_upload_receipts(
    files: list[UploadFile] = File(...),
    ledger_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """批量上传并识别账单图片"""
    # 验证账本属于当前用户
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该账本"
        )

    # 限制批量上传数量
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="批量上传最多支持10张图片"
        )

    try:
        image_service = ImageService()
        relative_paths = []
        full_paths = []

        # 保存所有图片
        for file in files:
            relative_path = await image_service.save_upload_file(file)
            full_path = image_service.get_full_path(relative_path)
            relative_paths.append(relative_path)
            full_paths.append(full_path)

        # 批量识别
        receipt_service = ReceiptService(db, api_key=settings.ZHIPU_API_KEY)
        accounts = await receipt_service.batch_recognize(full_paths, relative_paths, ledger_id)

        # 转换为响应格式
        result = [
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
            message=f"成功识别 {len(result)} 张图片",
            data=result
        )
    except Exception as e:
        logger.error(f"批量处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量处理失败: {str(e)}"
        )
