# 命令行版本记账系统

基于AI视觉识别的智能记账系统CLI版本。

## 功能特性

- **智能识别**：利用智谱AI视觉模型（glm-4.6v）自动提取账单关键信息
- **多种票据支持**：支持发票、收据、手写记录、电子账单截图等多种格式
- **结构化存储**：使用SQLite数据库持久化存储账目记录
- **批量处理**：支持一次性处理多张账单图片
- **数据查询**：按日期、分类等条件筛选记录
- **统计分析**：自动计算收支统计和分类汇总

## 快速启动

```bash
# 进入cli目录
cd cli

# 运行程序
python cli.py
```

## 使用说明

### 交互式菜单

启动程序后，会显示以下菜单：

```
==================================================
欢迎使用自动记账Agent
==================================================

请选择操作:
1. 处理单张账单
2. 批量处理账单
3. 查询记账记录
4. 统计分析
5. 退出
```

### 功能详解

#### 1. 处理单张账单

选择选项 `1`，输入图片路径，系统会自动识别账单信息：

```
请输入选项 (1-5): 1
请输入图片路径: /path/to/receipt.jpg

正在处理账单: /path/to/receipt.jpg
✅ 账单识别成功 (置信度: 0.92)
💾 已保存到数据库 (ID: 1)
```

#### 2. 批量处理账单

选择选项 `2`，输入包含账单图片的文件夹路径：

```
请输入选项 (1-5): 2
请输入图片文件夹路径: /path/to/receipts/

[1/5] 处理: /path/to/receipts/img1.jpg
正在处理账单: /path/to/receipts/img1.jpg
...
```

支持的图片格式：`.png`, `.jpg`, `.jpeg`

#### 3. 查询记账记录

选择选项 `3`，查看最近的账目记录：

```
请输入选项 (1-5): 3

找到 10 条记录:
  2024-01-15 | 午餐 | ¥58.50 | 餐饮
  2024-01-14 | 地铁充值 | ¥100.00 | 交通
  2024-01-13 | 超市购物 | ¥235.80 | 购物
  ...
```

#### 4. 统计分析

选择选项 `4`，查看指定时间段的收支统计：

```
请输入选项 (1-5): 4
开始日期 (YYYY-MM-DD): 2024-01-01
结束日期 (YYYY-MM-DD): 2024-01-31

统计信息 (2024-01-01 至 2024-01-31):
  总收入: ¥5000.00
  总支出: ¥1850.30
  结余: ¥3149.70

分类统计:
  餐饮: ¥850.50
  交通: ¥320.00
  购物: ¥580.80
  其他: ¥99.00
```

## Python API调用

除了交互式界面，你也可以直接在代码中使用：

```python
from agent.accounting_agent import AccountingAgent

# 初始化Agent
agent = AccountingAgent(
    api_key="your-api-key",
    db_path="accounting.db"
)

# 处理单张账单
account = agent.process_receipt("receipt.jpg")
print(f"识别结果: {account.to_dict()}")

# 批量处理
images = ["receipt1.jpg", "receipt2.jpg", "receipt3.jpg"]
results = agent.batch_process_receipts(images)

# 查询记录
records = agent.query_records(
    start_date="2024-01-01",
    end_date="2024-01-31",
    category="餐饮"
)

# 统计分析
stats = agent.get_statistics("2024-01-01", "2024-01-31")
print(f"本月支出: ¥{stats['total_expense']}")
```

## 目录结构

```
cli/
├── agent/                 # Agent核心模块
│   ├── __init__.py
│   ├── schemas.py         # JSON Schema和Prompt定义
│   ├── receipt_analyzer.py # 账单分析器
│   └── accounting_agent.py # Agent主流程
├── database/              # 数据库模块
│   ├── __init__.py
│   ├── models.py          # Account数据模型
│   └── operations.py      # 数据库CRUD操作
├── config/                # 配置模块
│   ├── __init__.py
│   └── settings.py        # 配置管理
├── utils/                 # 工具模块
│   ├── __init__.py
│   └── validators.py      # 数据验证
├── __init__.py
├── cli.py                 # 主入口
└── README.md              # 本文档
```

## 配置说明

需要确保项目根目录的 `.env` 文件中包含以下配置：

```bash
ZHIPU_API_KEY=your-api-key-here
VISION_MODEL=glm-4.6v
DB_PATH=accounting.db
CONFIDENCE_THRESHOLD=0.7
AUTO_SAVE=true
```
