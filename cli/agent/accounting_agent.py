"""自动记账Agent主流程"""
from typing import Optional, List
import os
from decimal import Decimal

from database.operations import DatabaseManager
from database.models import Account
from .receipt_analyzer import ReceiptAnalyzer


class AccountingAgent:
    """自动记账Agent"""

    def __init__(
        self,
        api_key: str,
        db_path: str = "accounting.db",
        model: str = "glm-4.6v"
    ):
        """
        初始化记账Agent

        Args:
            api_key: 智谱AI API密钥
            db_path: 数据库文件路径
            model: 视觉模型名称
        """
        self.analyzer = ReceiptAnalyzer(api_key=api_key, model=model)
        self.db = DatabaseManager(db_path=db_path)

    def process_receipt(
        self,
        image_path: str,
        auto_save: bool = True,
        confirm_threshold: float = 0.7
    ) -> Optional[Account]:
        """
        处理账单图片的完整流程

        Args:
            image_path: 账单图片路径
            auto_save: 是否自动保存到数据库
            confirm_threshold: 自动保存的置信度阈值

        Returns:
            Account对象，如果处理失败返回None
        """
        print(f"正在处理账单: {image_path}")

        # 1. 分析账单图片
        result = self.analyzer.analyze_receipt(image_path)
        if not result:
            print("❌ 账单识别失败")
            return None

        print(f"✅ 账单识别成功 (置信度: {result.get('confidence', 0):.2f})")

        # 2. 转换为Account对象
        account = self._parse_to_account(image_path, result)

        # 3. 置信度检查
        if account.confidence < confirm_threshold:
            print(f"⚠️  识别置信度较低 ({account.confidence:.2f})，建议人工核对")
            print(f"识别结果: {account.to_dict()}")

            if auto_save:
                confirm = input("是否仍要保存到数据库？(y/n): ").strip().lower()
                if confirm != 'y':
                    print("已取消保存")
                    return account

        # 4. 保存到数据库
        if auto_save:
            account_id = self.db.add_account(account)
            account.id = account_id
            print(f"💾 已保存到数据库 (ID: {account_id})")

        return account

    def batch_process_receipts(
        self,
        image_paths: List[str],
        auto_save: bool = True
    ) -> List[Account]:
        """
        批量处理账单

        Args:
            image_paths: 图片路径列表
            auto_save: 是否自动保存

        Returns:
            成功处理的Account列表
        """
        results = []
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n[{i}/{len(image_paths)}] 处理: {image_path}")
            account = self.process_receipt(image_path, auto_save)
            if account:
                results.append(account)

        return results

    def query_records(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Account]:
        """查询记账记录"""
        return self.db.get_all_accounts(
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit
        )

    def get_statistics(self, start_date: str, end_date: str) -> dict:
        """获取统计信息"""
        return self.db.get_statistics(start_date, end_date)

    @staticmethod
    def _parse_to_account(image_path: str, result: dict) -> Account:
        """将识别结果转换为Account对象"""
        return Account(
            transaction_date=result.get("transaction_date"),
            amount=Decimal(str(result.get("amount", 0))),
            item_name=result.get("item_name", "未知"),
            category=result.get("category"),
            merchant_name=result.get("merchant_name"),
            payment_method=result.get("payment_method"),
            transaction_type="支出",  # 默认为支出，后续可扩展识别收入
            notes=result.get("notes"),
            image_path=os.path.abspath(image_path),
            receipt_type=result.get("receipt_type"),
            confidence=result.get("confidence", 0.0)
        )
