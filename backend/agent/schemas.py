"""JSON Schema定义和Prompt模板"""

# 账单识别的JSON Schema
RECEIPT_SCHEMA = {
    "type": "object",
    "description": "账单信息结构",
    "properties": {
        "success": {
            "type": "boolean",
            "description": "是否成功识别到账单信息"
        },
        "confidence": {
            "type": "number",
            "description": "整体识别置信度 (0-1)",
            "minimum": 0,
            "maximum": 1
        },
        "receipt_type": {
            "type": "string",
            "description": "票据类型",
            "enum": ["发票", "收据", "手写记录", "电子账单", "其他"]
        },
        "transaction_date": {
            "type": "string",
            "description": "交易日期，格式：YYYY-MM-DD"
        },
        "amount": {
            "type": "number",
            "description": "金额（元）"
        },
        "item_name": {
            "type": "string",
            "description": "商品或服务名称"
        },
        "category": {
            "type": "string",
            "description": "消费分类",
            "enum": ["食品餐饮", "出行交通", "购物消费", "休闲娱乐", "居家生活", "文化教育", "健康医疗", "其他"]
        },
        "merchant_name": {
            "type": "string",
            "description": "商户名称"
        },
        "payment_method": {
            "type": "string",
            "description": "支付方式",
            "enum": ["现金", "微信支付", "支付宝", "银行卡", "信用卡", "其他"]
        },
        "items": {
            "type": "array",
            "description": "详细项目列表（如果有多个项目）",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "项目名称"
                    },
                    "quantity": {
                        "type": "number",
                        "description": "数量"
                    },
                    "price": {
                        "type": "number",
                        "description": "单价"
                    },
                    "subtotal": {
                        "type": "number",
                        "description": "小计"
                    }
                }
            }
        },
        "notes": {
            "type": "string",
            "description": "其他备注信息"
        },
        "raw_text": {
            "type": "string",
            "description": "识别到的原始文本内容"
        },
        "errors": {
            "type": "array",
            "description": "识别过程中遇到的问题",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["success", "confidence"]
}

# 账单分析Prompt
RECEIPT_ANALYSIS_PROMPT = """请仔细分析这张账单图片，提取关键信息。

**识别要求：**
1. **交易日期**：优先识别发票日期/交易时间，格式统一为 YYYY-MM-DD
2. **金额**：识别总金额或实付金额，以元为单位
3. **商品/服务名称**：提取主要商品或服务名称
4. **分类**：根据消费内容自动归类（食品餐饮/出行交通/购物消费/休闲娱乐/居家生活/文化教育/健康医疗/其他）
5. **商户名称**：识别商家名称
6. **支付方式**：判断支付类型（现金/微信/支付宝/银行卡等）
7. **票据类型**：判断是发票、收据、手写记录还是电子账单截图

**注意事项：**
- 如果图片模糊或信息不全，请在confidence字段中降低置信度
- 如果无法识别某项信息，该字段可以返回null
- amount字段必须是数字类型，不要包含货币符号
- 日期格式必须严格遵循 YYYY-MM-DD
- 如果有多个消费项目，请全部列出在items数组中
- 识别的置信度综合考虑图片清晰度和信息完整度

请严格按照提供的JSON Schema格式返回结果，不要添加任何额外说明文字。"""
