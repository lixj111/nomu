"""AI 工具定义与执行器（OpenAI 格式 function calling）"""
import json

from database.operations import DatabaseManager


# OpenAI 标准格式工具定义
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_ledgers",
            "description": "列出当前用户的所有账本（含名称、是否默认）。用户未指定账本、需要确定分析数据范围时调用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_default_ledger",
            "description": "获取当前用户的默认账本。用户未指定账本时，用其确定分析数据范围。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_statistics",
            "description": "查询指定账本在日期范围内的收支概览：总收入、总支出、结余、账单笔数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ledger_id": {"type": "integer", "description": "账本ID"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                },
                "required": ["ledger_id", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_category_stats",
            "description": "查询指定账本在日期范围内按分类统计的收支金额与占比（金额降序）。用于分析消费结构、主要花销。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ledger_id": {"type": "integer", "description": "账本ID"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                    "transaction_type": {"type": "string", "enum": ["支出", "收入"], "description": "可选，仅统计该类型"},
                },
                "required": ["ledger_id", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_trend",
            "description": "查询指定账本在日期范围内按天/月分组的收入与支出趋势，用于分析消费随时间的变化。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ledger_id": {"type": "integer", "description": "账本ID"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                    "group_by": {"type": "string", "enum": ["day", "month"], "description": "分组粒度，默认 month"},
                },
                "required": ["ledger_id", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_accounts",
            "description": "查询指定账本在日期范围内的账单明细，可按分类/收支类型筛选，返回最近的若干条。用于回答“最近买了什么”“某分类的明细”。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ledger_id": {"type": "integer", "description": "账本ID"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD，可选"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD，可选"},
                    "category": {"type": "string", "description": "分类，可选"},
                    "transaction_type": {"type": "string", "enum": ["支出", "收入"], "description": "可选"},
                    "limit": {"type": "integer", "description": "返回条数，默认10，最大50"},
                },
                "required": ["ledger_id"],
            },
        },
    },
]


def _require_ledger(db: DatabaseManager, ledger_id: int, user_id: int):
    """校验账本归属，越权抛 PermissionError"""
    ledger = db.get_ledger_by_id(ledger_id)
    if not ledger or ledger.user_id != user_id:
        raise PermissionError("账本不存在或无权访问")
    return ledger


def _list_ledgers(db: DatabaseManager, user_id: int, args: dict) -> list:
    return [
        {
            "id": l.id,
            "name": l.name,
            "description": l.description or "",
            "is_default": bool(l.is_default),
        }
        for l in db.get_ledgers_by_user(user_id)
    ]


def _get_default_ledger(db: DatabaseManager, user_id: int, args: dict) -> dict:
    ledger = db.get_default_ledger(user_id)
    if not ledger:
        ledgers = db.get_ledgers_by_user(user_id)
        ledger = ledgers[0] if ledgers else None
    if not ledger:
        return {"error": "当前用户没有任何账本"}
    return {"id": ledger.id, "name": ledger.name, "is_default": bool(ledger.is_default)}


def _get_statistics(db: DatabaseManager, user_id: int, args: dict) -> dict:
    ledger = _require_ledger(db, args["ledger_id"], user_id)
    s = db.get_statistics(args["start_date"], args["end_date"], ledger.id)
    count = db.get_account_count(
        ledger_id=ledger.id, start_date=args["start_date"], end_date=args["end_date"]
    )
    return {
        "ledger": ledger.name,
        "total_income": round(s["total_income"], 2),
        "total_expense": round(s["total_expense"], 2),
        "balance": round(s["balance"], 2),
        "account_count": count,
    }


def _get_category_stats(db: DatabaseManager, user_id: int, args: dict) -> dict:
    ledger = _require_ledger(db, args["ledger_id"], user_id)
    s = db.get_statistics(args["start_date"], args["end_date"], ledger.id)
    ttype = args.get("transaction_type")
    items = []
    total = 0.0
    for category, amounts in s["category_stats"].items():
        for tt, amt in amounts.items():
            if ttype and tt != ttype:
                continue
            if amt <= 0:
                continue
            items.append({"category": category or "未分类", "type": tt, "amount": round(float(amt), 2)})
            total += float(amt)
    for c in items:
        c["percentage"] = round(c["amount"] / total * 100, 2) if total else 0.0
    items.sort(key=lambda x: x["amount"], reverse=True)
    return {"ledger": ledger.name, "total": round(total, 2), "items": items}


def _get_trend(db: DatabaseManager, user_id: int, args: dict) -> dict:
    ledger = _require_ledger(db, args["ledger_id"], user_id)
    group_by = args.get("group_by") or "month"
    if group_by not in ("day", "month"):
        group_by = "month"
    items = db.get_trend(args["start_date"], args["end_date"], ledger.id, group_by)
    return {"ledger": ledger.name, "group_by": group_by, "items": items}


def _get_accounts(db: DatabaseManager, user_id: int, args: dict) -> dict:
    ledger = _require_ledger(db, args["ledger_id"], user_id)
    limit = min(int(args.get("limit") or 10), 50)
    res = db.get_accounts_paginated(
        ledger_id=ledger.id,
        start_date=args.get("start_date"),
        end_date=args.get("end_date"),
        category=args.get("category"),
        transaction_type=args.get("transaction_type"),
        page=1,
        page_size=limit,
    )
    items = [
        {
            "date": a.transaction_date,
            "type": a.transaction_type,
            "category": a.category or "未分类",
            "item": a.item_name,
            "amount": round(float(a.amount), 2),
            "merchant": a.merchant_name or "",
        }
        for a in res["items"]
    ]
    return {"ledger": ledger.name, "total": res["total"], "returned": len(items), "items": items}


TOOL_EXECUTORS = {
    "list_ledgers": _list_ledgers,
    "get_default_ledger": _get_default_ledger,
    "get_statistics": _get_statistics,
    "get_category_stats": _get_category_stats,
    "get_trend": _get_trend,
    "get_accounts": _get_accounts,
}


def execute_tool(name: str, args_json: str, db: DatabaseManager, user_id: int) -> dict:
    """执行工具的统一入口，返回可 JSON 序列化的结果"""
    fn = TOOL_EXECUTORS[name]
    args = json.loads(args_json) if args_json else {}
    return fn(db, user_id, args)


def summarize_tool_result(name: str, result: dict) -> str:
    """生成工具结果的一句话摘要（前端 ToolCallCard 展示）"""
    try:
        if name == "get_statistics":
            return (
                f"账本[{result.get('ledger')}] 支出 {result.get('total_expense', 0)} 元，"
                f"收入 {result.get('total_income', 0)} 元，结余 {result.get('balance', 0)} 元，"
                f"共 {result.get('account_count', 0)} 笔"
            )
        if name == "get_category_stats":
            return f"共 {len(result.get('items', []))} 个分类，合计 {result.get('total', 0)} 元"
        if name == "get_trend":
            return f"共 {len(result.get('items', []))} 个周期"
        if name == "get_accounts":
            return f"返回 {result.get('returned', 0)} 条，共 {result.get('total', 0)} 条匹配"
        if name == "list_ledgers":
            names = "、".join(l["name"] for l in result)
            return f"找到 {len(result)} 个账本：{names}"
        if name == "get_default_ledger":
            return f"默认账本：{result.get('name')}"
    except Exception:
        pass
    return str(result)[:80]
