"""导入相关API"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from database.models import User, Account
from database.operations import DatabaseManager
from api.deps import get_db, get_current_user
import pandas as pd
from datetime import datetime
import logging
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import", tags=["导入"])


def parse_internal_format(df: pd.DataFrame) -> list:
    """解析本程序导出的Excel格式"""
    accounts = []
    for _, row in df.iterrows():
        # 跳过空行
        if pd.isna(row.get('日期', pd.NA)):
            continue

        account = {
            'transaction_date': str(row.get('日期', ''))[:10],  # 确保日期格式正确
            'transaction_type': row.get('类型', '支出'),
            'category': row.get('分类', '未分类'),
            'item_name': row.get('商品名称', ''),
            'amount': float(row.get('金额', '0').replace('¥', '').replace(',', '') if isinstance(row.get('金额'), str) else row.get('金额', 0)),
            'merchant_name': row.get('地点', ''),
            'notes': row.get('备注', ''),
            'image_path': row.get('附件', '')
        }
        accounts.append(account)
    return accounts


def parse_yimu_format(df: pd.DataFrame) -> list:
    """解析一木记账导出的Excel格式"""
    logger.info(f"[一木记账] 开始解析，DataFrame shape: {df.shape}")
    accounts = []

    # 一木记账的列名映射（可能需要根据实际导出文件调整）
    column_mapping = {
        '交易时间': 'transaction_date',
        '日期': 'transaction_date',
        '类别': 'transaction_type',
        '二级分类': 'category',
        '金额': 'amount',
        '备注': 'notes',
        '商品名称': 'item_name',
        '项目': 'item_name',
        '商家': 'merchant_name',
        '地点': 'merchant_name'
    }

    # 先找到实际使用的列名
    actual_columns = df.columns.tolist()
    logger.info(f"[一木记账] Excel列名: {actual_columns}")
    print(f"[一木记账] Excel列名: {actual_columns}")

    for idx, row in df.iterrows():
        try:
            # 跳过空行
            date_value = row.get('交易时间') or row.get('日期')
            if pd.isna(date_value):
                logger.debug(f"[一木记账] 跳过空行，行号: {idx}")
                continue

            # 解析交易类型（类别）
            transaction_type = row.get('类别', '支出')
            if pd.isna(transaction_type):
                transaction_type = '支出'

            # 解析分类（二级分类）
            category = row.get('二级分类', '未分类')
            if pd.isna(category):
                category = '未分类'

            # 解析金额
            amount_value = row.get('金额')
            if pd.isna(amount_value):
                amount_value = 0
            else:
                amount_value = float(amount_value)

            # 解析商品名称，优先使用商品名称、项目、备注，最后使用分类
            item_name = row.get('商品名称') or row.get('项目') or row.get('备注')
            if pd.isna(item_name):
                item_name = category

            account = {
                'transaction_date': str(date_value)[:10],
                'transaction_type': str(transaction_type),
                'category': str(category),
                'item_name': str(item_name),
                'amount': abs(amount_value),  # 确保金额为正数
                'merchant_name': str(row.get('商家') or row.get('地点') or ''),
                'notes': str(row.get('备注') or ''),
                'image_path': ''
            }
            logger.debug(f"[一木记账] 解析行 {idx}: {account}")
            accounts.append(account)

        except Exception as e:
            logger.error(f"[一木记账] 解析行 {idx} 失败: {e}", exc_info=True)
            print(f"[一木记账] 解析行 {idx} 失败: {e}")
            continue

    logger.info(f"[一木记账] 解析完成，共解析 {len(accounts)} 条记录")
    return accounts


@router.post("/accounts")
async def import_accounts(
    file: UploadFile = File(...),
    source: str = Form(...),
    ledger_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """导入账单数据到指定账本"""
    logger.info(f"[导入] 开始导入 - 文件名: {file.filename}, 来源: {source}, 账本ID: {ledger_id}, 用户: {current_user.username}")

    # 验证账本所有权
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != current_user.id:
        logger.warning(f"[导入] 账本不存在或无权限，账本ID: {ledger_id}, 用户ID: {current_user.id}")
        raise HTTPException(status_code=404, detail="账本不存在")

    # 验证导入来源
    if source not in ['internal', 'yimu']:
        logger.warning(f"[导入] 无效的导入来源: {source}")
        raise HTTPException(status_code=400, detail="无效的导入来源")

    try:
        # 读取Excel文件
        logger.info(f"[导入] 开始读取文件: {file.filename}")
        contents = await file.read()
        logger.info(f"[导入] 文件读取完成，大小: {len(contents)} bytes")

        logger.info(f"[导入] 开始解析Excel")
        df = pd.read_excel(io.BytesIO(contents))
        logger.info(f"[导入] Excel解析完成，shape: {df.shape}, 列名: {df.columns.tolist()}")

        # 根据来源解析数据
        logger.info(f"[导入] 使用解析器: {source}")
        if source == 'internal':
            accounts = parse_internal_format(df)
        else:  # yimu
            accounts = parse_yimu_format(df)

        logger.info(f"[导入] 解析完成，共 {len(accounts)} 条记录")

        if not accounts:
            logger.warning(f"[导入] 未找到有效的账单数据")
            raise HTTPException(status_code=400, detail="未找到有效的账单数据")

        # 批量导入账单
        success_count = 0
        error_count = 0

        for idx, account in enumerate(accounts):
            try:
                logger.debug(f"[导入] 处理第 {idx + 1}/{len(accounts)} 条记录: {account.get('item_name', '')}")

                # 验证必填字段
                if not account.get('transaction_date') or not account.get('item_name'):
                    logger.warning(f"[导入] 跳过无效记录 {idx}: 缺少必填字段")
                    error_count += 1
                    continue

                # 确保金额有效
                try:
                    account['amount'] = float(account['amount'])
                except (ValueError, TypeError):
                    logger.warning(f"[导入] 金额无效，设置为0: {account.get('amount')}")
                    account['amount'] = 0.0

                # 创建账单
                logger.debug(f"[导入] 创建账单: date={account['transaction_date']}, type={account.get('transaction_type')}, item={account['item_name']}, amount={account['amount']}")
                new_account = Account(
                    ledger_id=ledger_id,
                    transaction_date=account['transaction_date'],
                    transaction_type=account.get('transaction_type', '支出'),
                    category=account.get('category', '未分类'),
                    item_name=account['item_name'],
                    amount=account['amount'],
                    merchant_name=account.get('merchant_name', ''),
                    notes=account.get('notes', ''),
                    image_path=account.get('image_path', '')
                )
                db.add_account(new_account)
                success_count += 1
                logger.debug(f"[导入] 成功创建第 {success_count} 条账单")

            except Exception as e:
                logger.error(f"[导入] 导入第 {idx} 条记录失败: {e}", exc_info=True)
                print(f"[导入] 导入第 {idx} 条记录失败: {e}")
                error_count += 1

        logger.info(f"[导入] 导入完成 - 成功: {success_count}, 失败: {error_count}")

        return {
            "code": 200,
            "message": "导入成功",
            "data": {
                "count": success_count,
                "errors": error_count
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[导入] 导入失败: {e}", exc_info=True)
        print(f"[导入] 导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
