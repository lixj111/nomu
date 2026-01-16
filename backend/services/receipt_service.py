"""账单识别服务"""
import os
from typing import Optional, Dict
from database.models import Account, Ledger
from database.operations import DatabaseManager
from agent.receipt_analyzer import ReceiptAnalyzer
from decimal import Decimal
from datetime import datetime


class ReceiptService:
    """账单识别服务"""

    def __init__(self, db: DatabaseManager, api_key: str):
        self.db = db
        self.analyzer = ReceiptAnalyzer(api_key=api_key)

    async def recognize_receipt(
        self,
        image_path: str,
        ledger_id: int
    ) -> Account:
        """识别账单图片并保存到数据库"""
        # 验证账本存在
        ledger = self.db.get_ledger_by_id(ledger_id)
        if not ledger:
            raise ValueError("账本不存在")

        # 调用AI识别
        result = self.analyzer.analyze_receipt(image_path)

        if not result or not result.get("success"):
            raise ValueError("账单识别失败")

        # 转换为Account对象
        account = Account(
            ledger_id=ledger_id,
            transaction_date=result.get("transaction_date", datetime.now().strftime("%Y-%m-%d")),
            amount=Decimal(str(result.get("amount", 0))),
            item_name=result.get("item_name", "未知"),
            category=result.get("category"),
            merchant_name=result.get("merchant_name"),
            payment_method=result.get("payment_method"),
            transaction_type="支出",  # 默认为支出
            notes=result.get("notes"),
            image_path=image_path,
            receipt_type=result.get("receipt_type"),
            confidence=result.get("confidence", 0.0)
        )

        # 保存到数据库
        account_id = self.db.add_account(account)
        account.id = account_id

        return account

    async def batch_recognize(
        self,
        image_paths: list,
        ledger_id: int
    ) -> list[Account]:
        """批量识别账单"""
        results = []
        for image_path in image_paths:
            try:
                account = await self.recognize_receipt(image_path, ledger_id)
                results.append(account)
            except Exception as e:
                # 记录错误但继续处理其他图片
                print(f"识别失败: {image_path}, 错误: {str(e)}")

        return results
