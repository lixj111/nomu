"""数据验证工具"""
from datetime import datetime
from decimal import Decimal, InvalidOperation


def validate_date(date_str: str) -> bool:
    """验证日期格式 (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def validate_amount(amount) -> bool:
    """验证金额"""
    try:
        return Decimal(str(amount)) > 0
    except (InvalidOperation, TypeError):
        return False


def validate_account_data(account_data: dict) -> tuple[bool, list[str]]:
    """
    验证账目数据

    Returns:
        (是否有效, 错误信息列表)
    """
    errors = []

    if not account_data.get("transaction_date"):
        errors.append("缺少交易日期")
    elif not validate_date(account_data["transaction_date"]):
        errors.append("日期格式错误，应为YYYY-MM-DD")

    if not account_data.get("amount"):
        errors.append("缺少金额")
    elif not validate_amount(account_data["amount"]):
        errors.append("金额格式错误")

    if not account_data.get("item_name"):
        errors.append("缺少商品/服务名称")

    return len(errors) == 0, errors
