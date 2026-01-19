# 自动记账系统

基于AI视觉识别的智能记账系统，支持命令行和Web界面两种使用方式。

## 版本说明

本项目包含两个版本：
- **命令行版本**：原始的CLI界面版本（见下方使用说明）
- **Web版本**：前后端分离的移动端Web应用（新增）

## Web版本功能特性

- **智能识别**：利用智谱AI视觉模型（glm-4.6v）自动提取账单关键信息
- **多账本管理**：支持创建多个账本，账本间数据隔离
- **移动端适配**：响应式设计，手机浏览器友好
- **数据统计**：分类图表、趋势分析
- **日程视图**：按日期查看收支情况

## 快速启动（Web版本）

### 1. 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端
cd backend
python main.py
```

后端运行在 http://localhost:8000，API文档：http://localhost:8000/docs

### 2. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

---

## 命令行版本功能特性

- **智能识别**：利用智谱AI视觉模型（glm-4.6v）自动提取账单关键信息
- **多种票据支持**：支持发票、收据、手写记录、电子账单截图等多种格式
- **结构化存储**：使用SQLite数据库持久化存储账目记录
- **批量处理**：支持一次性处理多张账单图片
- **数据查询**：按日期、分类等条件筛选记录
- **统计分析**：自动计算收支统计和分类汇总

## 提取信息

系统会自动提取以下账单信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| 交易日期 | 账单日期 | 2024-01-15 |
| 金额 | 总金额/实付金额 | 58.50 |
| 商品/服务名称 | 主要消费项目 | 午餐 |
| 分类 | 自动分类（餐饮/交通/购物等） | 餐饮 |
| 商户名称 | 商家名称 | XX餐厅 |
| 支付方式 | 微信/支付宝/现金等 | 微信支付 |
| 票据类型 | 发票/收据/手写记录等 | 发票 |

## 项目结构

```
omu/
├── backend/               # Web版本 - 后端服务
│   └── ...
├── frontend/              # Web版本 - 前端应用
│   └── ...
├── cli/                   # 命令行版本
│   ├── agent/             # Agent核心模块
│   │   ├── __init__.py
│   │   ├── schemas.py     # JSON Schema和Prompt定义
│   │   ├── receipt_analyzer.py # 账单分析器
│   │   └── accounting_agent.py # Agent主流程
│   ├── database/          # 数据库模块
│   │   ├── __init__.py
│   │   ├── models.py      # Account数据模型
│   │   └── operations.py  # 数据库CRUD操作
│   ├── config/            # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py    # 配置管理
│   ├── utils/             # 工具模块
│   │   ├── __init__.py
│   │   └── validators.py  # 数据验证
│   ├── __init__.py
│   ├── cli.py             # 主入口
│   └── README.md          # CLI版本文档
├── requirements.txt       # 项目依赖
├── .env.example           # 环境变量模板
├── .gitignore             # Git忽略配置
├── CLAUDE.md              # 项目配置说明
└── README.md              # 项目文档
```

## 安装部署

### 环境要求

- Python 3.8+
- 智谱AI API密钥

### 安装步骤

1. **克隆项目**
   ```bash
   cd /path/to/omu
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 文件，填入你的配置：
   ```bash
   ZHIPU_API_KEY=your-api-key-here
   VISION_MODEL=glm-4.6v
   DB_PATH=accounting.db
   CONFIDENCE_THRESHOLD=0.7
   ```

4. **运行程序**
   ```bash
   cd cli
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

## 代码示例

### Python API调用

除了交互式界面，你也可以直接在代码中使用（需先进入cli目录）：

```bash
cd cli
```

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

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPU_API_KEY` | 智谱AI API密钥（必填） | - |
| `VISION_MODEL` | 视觉模型名称 | glm-4.6v |
| `DB_PATH` | 数据库文件路径 | accounting.db |
| `CONFIDENCE_THRESHOLD` | 自动保存置信度阈值 | 0.7 |
| `AUTO_SAVE` | 是否自动保存到数据库 | true |

## 数据库结构

### accounts 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键（自增） |
| transaction_date | DATE | 交易日期 |
| amount | DECIMAL(10,2) | 金额 |
| item_name | VARCHAR(200) | 商品/服务名称 |
| category | VARCHAR(50) | 分类 |
| merchant_name | VARCHAR(100) | 商户名称 |
| payment_method | VARCHAR(20) | 支付方式 |
| transaction_type | VARCHAR(20) | 交易类型 |
| notes | TEXT | 备注 |
| image_path | VARCHAR(500) | 图片路径 |
| receipt_type | VARCHAR(20) | 票据类型 |
| confidence | DECIMAL(3,2) | AI识别置信度 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| is_deleted | BOOLEAN | 软删除标记 |

## 后续扩展

- [ ] 多账本支持
- [ ] 标签系统
- [ ] 预算管理和提醒
- [ ] 图表可视化
- [ ] 导出Excel/CSV
- [ ] Web界面
- [ ] 移动端支持
- [ ] 收入类型识别

## 常见问题

**Q: 识别准确率如何？**
A: 识别准确率取决于图片清晰度和票据格式。建议使用清晰、完整的票据图片，系统会输出置信度供参考。

**Q: 识别失败怎么办？**
A: 可以手动编辑数据库记录，或调整识别阈值后重新处理。

**Q: 数据库文件在哪里？**
A: 默认在项目根目录下的 `accounting.db`，可以在 `.env` 中自定义路径。

**Q: 支持哪些图片格式？**
A: 支持 PNG、JPG、JPEG 等常见图片格式。

## 许可证

MIT License
