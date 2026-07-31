"""账单识别服务"""
from typing import Optional, Dict
from database.models import Account, Ledger
from database.operations import DatabaseManager
from agent.receipt_analyzer import ReceiptAnalyzer
from decimal import Decimal, InvalidOperation
from datetime import datetime

# 有效的分类列表
VALID_CATEGORIES = [
    "食品餐饮", "出行交通", "购物消费", "休闲娱乐",
    "居家生活", "文化教育", "健康医疗", "其他"
]

# 有效的支付方式
VALID_PAYMENT_METHODS = [
    "现金", "微信支付", "支付宝", "银行卡", "信用卡", "其他"
]

# 有效的票据类型
VALID_RECEIPT_TYPES = [
    "发票", "收据", "手写记录", "电子账单", "其他"
]


class ReceiptService:
    """账单识别服务"""

    def __init__(self, db: DatabaseManager, api_key: Optional[str]):
        if not api_key:
            raise ValueError("ZHIPU_API_KEY 未配置，请在 .env 文件中设置")
        self.db = db
        self.analyzer = ReceiptAnalyzer(api_key=api_key)

    def _validate_and_fix_date(self, date_str: Optional[str]) -> str:
        """验证并修复日期"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # 尝试解析日期
        try:
            # 如果是 YYYY-MM-DD 格式
            if "-" in date_str:
                parts = date_str.split("-")
                if len(parts) == 3:
                    year, month, day = parts
                    # 确保是4位年份
                    if len(year) == 4 and year.isdigit() and month.isdigit() and day.isdigit():
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            # 如果是其他格式，尝试使用当前日期
            return datetime.now().strftime("%Y-%m-%d")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d")

    def _validate_and_fix_amount(self, amount) -> float:
        """验证并修复金额"""
        try:
            amount_value = float(amount)
            if amount_value <= 0:
                return 0.0
            return amount_value
        except (ValueError, TypeError, InvalidOperation):
            return 0.0

    def _validate_and_fix_category(self, category: Optional[str]) -> str:
        """验证并修复分类"""
        if not category:
            return "其他"
        # 如果分类不在有效列表中，返回"其他"
        if category not in VALID_CATEGORIES:
            # 尝试模糊匹配
            for valid_cat in VALID_CATEGORIES:
                if valid_cat in category or category in valid_cat:
                    return valid_cat
            return "其他"
        return category

    def _validate_and_fix_item_name(self, item_name: Optional[str], merchant_name: Optional[str]) -> str:
        """验证并修复商品名称"""
        if item_name and item_name.strip():
            return item_name.strip()
        # 如果商品名为空，尝试使用商户名称
        if merchant_name and merchant_name.strip():
            return merchant_name.strip()
        return "日常消费"

    def _validate_payment_method(self, payment_method: Optional[str]) -> Optional[str]:
        """验证支付方式"""
        if not payment_method:
            return None
        if payment_method in VALID_PAYMENT_METHODS:
            return payment_method
        # 模糊匹配
        if "微信" in payment_method:
            return "微信支付"
        if "支付宝" in payment_method:
            return "支付宝"
        if "现金" in payment_method:
            return "现金"
        if "银行卡" in payment_method or "储蓄卡" in payment_method:
            return "银行卡"
        if "信用卡" in payment_method:
            return "信用卡"
        return None

    def _validate_receipt_type(self, receipt_type: Optional[str]) -> Optional[str]:
        """验证票据类型"""
        if not receipt_type:
            return None
        if receipt_type in VALID_RECEIPT_TYPES:
            return receipt_type
        # 模糊匹配
        if "电子" in receipt_type or "账单" in receipt_type:
            return "电子账单"
        if "发票" in receipt_type:
            return "发票"
        if "收据" in receipt_type:
            return "收据"
        if "手写" in receipt_type:
            return "手写记录"
        return "其他"

    async def recognize_receipt(
        self,
        full_path: str,
        relative_path: str,
        ledger_id: int
    ) -> Account:
        """识别账单图片并保存到数据库"""
        # 验证账本存在
        ledger = self.db.get_ledger_by_id(ledger_id)
        if not ledger:
            raise ValueError("账本不存在")

        # 调用AI识别
        result = self.analyzer.analyze_receipt(full_path)

        if not result or not result.get("success"):
            raise ValueError("账单识别失败")

        # 验证并修复所有字段
        transaction_date = self._validate_and_fix_date(result.get("transaction_date"))
        amount = self._validate_and_fix_amount(result.get("amount", 0))
        category = self._validate_and_fix_category(result.get("category"))
        item_name = self._validate_and_fix_item_name(
            result.get("item_name"),
            result.get("merchant_name")
        )
        merchant_name = result.get("merchant_name")
        payment_method = self._validate_payment_method(result.get("payment_method"))
        receipt_type = self._validate_receipt_type(result.get("receipt_type"))
        confidence = result.get("confidence", 0.0)

        # 如果金额为0，给出警告
        if amount == 0:
            print(f"警告：未能识别到有效金额，使用默认值0")

        # 转换为Account对象
        account = Account(
            ledger_id=ledger_id,
            transaction_date=transaction_date,
            amount=Decimal(str(amount)),
            item_name=item_name,
            category=category,
            merchant_name=merchant_name,
            payment_method=payment_method,
            transaction_type="支出",  # 默认为支出
            notes=result.get("notes"),
            image_path=relative_path,  # 存储相对路径
            receipt_type=receipt_type,
            confidence=confidence
        )

        # 保存到数据库并返回完整的Account对象（包含created_at和updated_at）
        return self.db.add_account(account)

    async def batch_recognize(
        self,
        full_paths: list,
        relative_paths: list,
        ledger_id: int
    ) -> list[Account]:
        """批量识别账单"""
        results = []
        for full_path, relative_path in zip(full_paths, relative_paths):
            try:
                account = await self.recognize_receipt(full_path, relative_path, ledger_id)
                results.append(account)
            except Exception as e:
                # 记录错误但继续处理其他图片
                print(f"识别失败: {full_path}, 错误: {str(e)}")

        return results
