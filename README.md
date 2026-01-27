# 智账 - AI自动记账系统

基于AI视觉识别的智能记账系统，支持命令行和Web界面两种使用方式。

## 版本说明

本项目包含两个版本：
- **命令行版本**：原始的CLI界面版本（见下方使用说明）
- **Web版本**：前后端分离的移动端Web应用，提供更丰富的功能和更好的用户体验

## Web版本功能特性

### 核心功能
- **智能识别**：利用智谱AI视觉模型（glm-4.6v）自动提取账单关键信息
- **多账本管理**：支持创建多个账本，账本间数据隔离
- **移动端适配**：响应式设计，手机浏览器友好
- **悬浮快捷按钮**：快速添加账单，支持拍照和相册选择

### 数据管理
- **账单列表**：按时间顺序展示账单，支持分页加载
- **账单详情**：查看完整的账单信息，支持编辑和删除
- **搜索功能**：按关键词、分类、日期范围搜索账单
- **数据导出**：支持导出为CSV格式
- **数据导入**：支持批量导入账单数据
- **数据清除**：支持清除账本所有数据

### 统计分析
- **数据统计**：收支总额、分类占比、趋势分析
- **分类图表**：饼图展示各类别支出占比
- **趋势图表**：折线图展示收支趋势
- **日程视图**：按日期查看收支情况，热力图展示消费密度

### 设置功能
- **账本管理**：创建、切换、删除账本
- **自定义分类**：支持添加自定义消费分类
- **数据备份**：本地数据存储和管理

## 快速启动（Web版本）

### 技术栈
- **后端**：FastAPI + SQLite + 智谱AI
- **前端**：Vue 3 + Ant Design Vue + ECharts + Pinia

### 1. 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的智谱AI API密钥

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

### 3. 访问应用

打开浏览器访问 http://localhost:5173，即可开始使用智账系统。

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
│   ├── agent/             # AI识别模块
│   │   ├── schemas.py     # JSON Schema定义
│   │   └── receipt_analyzer.py # 账单分析器
│   ├── api/               # API路由
│   │   ├── v1/            # API v1版本
│   │   │   ├── auth.py    # 认证接口
│   │   │   ├── ledgers.py # 账本接口
│   │   │   ├── accounts.py # 账单接口
│   │   │   ├── upload.py  # 上传接口
│   │   │   ├── statistics.py # 统计接口
│   │   │   ├── export.py  # 导出接口
│   │   │   └── import_data.py # 导入接口
│   │   └── deps.py        # 依赖注入
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   └── security.py    # 安全相关
│   ├── database/          # 数据库模块
│   │   ├── models.py      # 数据模型
│   │   └── operations.py  # 数据库操作
│   ├── schemas/           # Pydantic模型
│   │   ├── user.py        # 用户模型
│   │   ├── ledger.py      # 账本模型
│   │   └── statistics.py  # 统计模型
│   ├── services/          # 业务逻辑
│   │   └── auth_service.py
│   └── main.py            # 应用入口
├── frontend/              # Web版本 - 前端应用
│   ├── src/
│   │   ├── api/           # API接口封装
│   │   ├── components/    # 组件
│   │   │   ├── AccountCard.vue # 账单卡片
│   │   │   ├── AccountForm.vue # 账单表单
│   │   │   ├── CategoryChart.vue # 分类图表
│   │   │   ├── TrendChart.vue # 趋势图表
│   │   │   ├── ImageUploader.vue # 图片上传
│   │   │   ├── LedgerSelector.vue # 账本选择器
│   │   │   └── DraggableFloatButton.vue # 悬浮按钮
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # Pinia状态管理
│   │   └── views/         # 页面视图
│   │       ├── Ledger.vue # 账本页面
│   │       ├── Search.vue # 搜索页面
│   │       ├── BillDetail.vue # 账单详情
│   │       ├── Schedule.vue # 日程页面
│   │       ├── Statistics.vue # 统计页面
│   │       └── Settings.vue # 设置页面
│   └── package.json
├── cli/                   # 命令行版本
│   ├── agent/             # Agent核心模块
│   │   ├── schemas.py     # JSON Schema和Prompt定义
│   │   ├── receipt_analyzer.py # 账单分析器
│   │   └── accounting_agent.py # Agent主流程
│   ├── database/          # 数据库模块
│   │   ├── models.py      # Account数据模型
│   │   └── operations.py  # 数据库CRUD操作
│   ├── config/            # 配置模块
│   │   └── settings.py    # 配置管理
│   ├── utils/             # 工具模块
│   │   └── validators.py  # 数据验证
│   └── cli.py             # 主入口
├── requirements.txt       # Python依赖
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

## Web版本界面展示

### 主要页面

1. **账本页面**：展示所有账单列表，支持分页加载和无限滚动
2. **搜索页面**：支持按关键词、分类、日期范围搜索，滚动位置记忆
3. **账单详情**：查看完整账单信息，支持编辑和删除操作
4. **日程页面**：日历视图展示每日收支，热力图显示消费密度
5. **统计页面**：分类饼图、趋势折线图、收支统计汇总
6. **设置页面**：账本管理、分类管理、数据导入导出、数据清除

### 交互特性

- 响应式设计，完美适配移动端
- 悬浮快捷按钮，快速添加账单
- 下拉刷新和上拉加载更多
- 流畅的页面切换动画
- 友好的错误提示和加载状态

## 常见问题

**Q: 识别准确率如何？**
A: 识别准确率取决于图片清晰度和票据格式。建议使用清晰、完整的票据图片，系统会输出置信度供参考。

**Q: 识别失败怎么办？**
A: 可以手动编辑账单信息，或重新上传图片进行识别。Web版本提供了完整的编辑功能。

**Q: 数据存储在哪里？**
A: 默认使用SQLite数据库，数据库文件位于 `backend/accounting.db`，可以在 `.env` 中自定义路径。

**Q: 支持哪些图片格式？**
A: 支持 PNG、JPG、JPEG 等常见图片格式。

**Q: 如何备份数据？**
A: Web版本提供了数据导出功能，可以导出为CSV格式进行备份。也可以直接复制 `accounting.db` 数据库文件。

**Q: 可以在手机上使用吗？**
A: 可以。Web版本采用了响应式设计，在手机浏览器上可以完美使用。

**Q: API密钥如何获取？**
A: 需要在智谱AI官网（https://open.bigmodel.cn/）注册账号并申请API密钥。

## 更新日志

### v1.0.0 (最新版本)
- ✨ 新增Web版本完整功能
- ✨ 支持多账本管理
- ✨ 添加账单搜索功能
- ✨ 实现数据导入导出
- ✨ 日程视图和统计图表
- ✨ 悬浮快捷按钮
- 🐛 修复滚动位置记忆问题
- 🎨 优化UI/UX体验

## 项目特色

1. **AI驱动**：利用最新的智谱AI视觉模型，识别准确率高
2. **双版本支持**：提供命令行和Web两个版本，满足不同使用场景
3. **移动优先**：Web版本专为移动端设计，随时随地记账
4. **完整功能**：从识别、管理到统计分析，提供完整记账流程
5. **数据安全**：本地存储，数据完全掌控
6. **开源免费**：MIT许可证，可自由使用和修改

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

MIT License

Copyright (c) 2025 智账

## 联系方式

如有问题或建议，欢迎提交Issue。
