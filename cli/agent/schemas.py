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
    "required": ["success", "confidence", "transaction_date", "amount", "item_name", "category"]
}

# 账单分析Prompt
RECEIPT_ANALYSIS_PROMPT = """你是一个专业的账单信息提取助手。请仔细分析这张账单图片，提取关键信息。

**必填字段要求（禁止返回null）：**
1. **transaction_date（交易日期）**：必须填写，格式为 YYYY-MM-DD
   - 优先寻找：发票日期、交易时间、账单日期
   - 如果找不到日期，使用图片中的时间（HH:MM）推断今天的日期
   - 完全没有时间信息时，使用当前日期

2. **amount（金额）**：必须填写数字
   - 识别总金额、实付金额或应付金额
   - 单位统一为元，不包含货币符号

3. **item_name（商品/服务名称）**：必须填写
   - 如果没有具体商品名，使用商户名称作为商品名
   - 如果也没有商户名，使用"日常消费"作为默认值

4. **category（分类）**：必须从以下选项中选择一个
   - 食品餐饮、出行交通、购物消费、休闲娱乐、居家生活、文化教育、健康医疗、其他
   - 根据支付内容智能判断：如餐厅→食品餐饮，加油→出行交通

**可选字段（允许null）：**
- merchant_name：商户名称
- payment_method：支付方式（现金/微信支付/支付宝/银行卡/信用卡/其他）
- receipt_type：票据类型（发票/收据/手写记录/电子账单/其他）

**识别规则：**
- 置信度低于0.5时，应在errors数组中说明原因
- 严格按JSON Schema格式返回，不添加额外文字
- 对于模糊图片，尽力推断而非返回null
- items数组列出所有识别到的明细项（如有）

请开始分析并返回JSON格式的结果。"""
