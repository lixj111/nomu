"""数据库操作封装"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from .models import Account, ChatMessage, ChatSession, Ledger, Memory, MemoryEvent, MemoryPhoto, User


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "accounting.db"):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """初始化数据库表"""
        with self._get_connection() as conn:
            # 创建用户表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100),
                    hashed_password VARCHAR(200) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建账本表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ledgers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name VARCHAR(50) NOT NULL,
                    description VARCHAR(200),
                    icon VARCHAR(20),
                    color VARCHAR(20),
                    is_default BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建账目表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ledger_id INTEGER,
                    transaction_date DATE NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    item_name VARCHAR(200) NOT NULL,
                    category VARCHAR(50),
                    merchant_name VARCHAR(100),
                    payment_method VARCHAR(20),
                    transaction_type VARCHAR(20) DEFAULT '支出',
                    notes TEXT,
                    image_path VARCHAR(500),
                    receipt_type VARCHAR(20),
                    confidence DECIMAL(3, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (ledger_id) REFERENCES ledgers(id)
                )
            """)

            # 创建索引：加速用户名查询（登录验证）
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            # 创建索引：加速按用户ID查询账本列表
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ledgers_user_id ON ledgers(user_id)")
            # 创建索引：加速查询默认账本
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ledgers_default ON ledgers(is_default)")
            # 创建索引：加速按账本查询账单（最常用）
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_ledger_id ON accounts(ledger_id)")
            # 创建索引：加速按日期范围查询和统计
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_transaction_date ON accounts(transaction_date)")
            # 创建索引：加速按分类查询和统计
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_category ON accounts(category)")
            # 创建索引：加速按收支类型查询和统计
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_transaction_type ON accounts(transaction_type)")

            # 创建 AI 会话表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建 AI 消息表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    role VARCHAR(20) NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                )
            """)

            # 创建索引：加速按用户查询会话、按会话查询消息
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)")

            # 创建回忆空间表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    partner_name VARCHAR(50) NOT NULL,
                    partner_avatar VARCHAR(500),
                    story VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # 创建回忆事件表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER,
                    title VARCHAR(200) NOT NULL,
                    event_date DATE NOT NULL,
                    description TEXT,
                    location VARCHAR(200),
                    cover_path VARCHAR(500),
                    author VARCHAR(20) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (memory_id) REFERENCES memories(id)
                )
            """)

            # 创建回忆照片表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER,
                    image_path VARCHAR(500) NOT NULL,
                    caption VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (event_id) REFERENCES memory_events(id)
                )
            """)

            # 创建索引：加速按用户查询回忆、按回忆查询事件、按事件查询照片
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_events_memory_id ON memory_events(memory_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_photos_event_id ON memory_photos(event_id)")

            # 为现有数据添加默认账本（如果表存在但 ledger_id 列不存在）
            self._migrate_existing_data(conn)

    def _migrate_existing_data(self, conn):
        """迁移现有数据：添加ledger_id列和默认账本"""
        try:
            # 检查accounts表是否有ledger_id列
            cursor = conn.execute("PRAGMA table_info(accounts)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'ledger_id' not in columns:
                # 添加ledger_id列
                conn.execute("ALTER TABLE accounts ADD COLUMN ledger_id INTEGER")

                # 创建默认账本
                conn.execute("""
                    INSERT INTO ledgers (user_id, name, description, icon, color, is_default)
                    VALUES (1, '默认账本', '系统默认账本', 'book', '#1890ff', 1)
                """)

                # 更新现有账单的ledger_id
                conn.execute("UPDATE accounts SET ledger_id = 1 WHERE ledger_id IS NULL")

            # chat_sessions 表增加 ledger_id 列（会话绑定的账本，旧会话为 NULL）
            cursor = conn.execute("PRAGMA table_info(chat_sessions)")
            session_columns = [row[1] for row in cursor.fetchall()]
            if 'ledger_id' not in session_columns:
                conn.execute("ALTER TABLE chat_sessions ADD COLUMN ledger_id INTEGER")

            # memory_events 表增加 author 列（事件主体: user/partner）
            cursor = conn.execute("PRAGMA table_info(memory_events)")
            event_columns = [row[1] for row in cursor.fetchall()]
            if 'author' not in event_columns:
                conn.execute("ALTER TABLE memory_events ADD COLUMN author VARCHAR(20) DEFAULT 'user'")
        except Exception:
            # 如果迁移失败，忽略（表可能已经是新结构）
            pass

    def add_account(self, account: Account) -> Account:
        """添加账目记录并返回完整的Account对象"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO accounts (
                    ledger_id, transaction_date, amount, item_name, category,
                    merchant_name, payment_method, transaction_type,
                    notes, image_path, receipt_type, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.ledger_id,
                account.transaction_date,
                float(account.amount),
                account.item_name,
                account.category,
                account.merchant_name,
                account.payment_method,
                account.transaction_type,
                account.notes,
                account.image_path,
                account.receipt_type,
                account.confidence
            ))
            account_id = cursor.lastrowid

        # 查询并返回完整的Account对象（包含created_at和updated_at）
        if account_id is None:
            raise ValueError("Failed to create account")
        result = self.get_account_by_id(account_id)
        if result is None:
            raise ValueError(f"Failed to retrieve created account with id {account_id}")
        return result

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """根据ID查询账目"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM accounts WHERE id = ? AND is_deleted = 0",
                (account_id,)
            )
            row = cursor.fetchone()
            return self._row_to_account(row) if row else None

    def get_all_accounts(
        self,
        ledger_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Account]:
        """查询账目列表（支持筛选）"""
        query = "SELECT * FROM accounts WHERE is_deleted = 0"
        params = []

        if ledger_id:
            query += " AND ledger_id = ?"
            params.append(ledger_id)
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_account(row) for row in cursor.fetchall()]

    def get_account_count(
        self,
        ledger_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None
    ) -> int:
        """获取账目总数"""
        query = "SELECT COUNT(*) FROM accounts WHERE is_deleted = 0"
        params = []

        if ledger_id:
            query += " AND ledger_id = ?"
            params.append(ledger_id)
        if start_date:
            query += " AND transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]

    def get_accounts_paginated(
        self,
        ledger_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """分页查询账目列表"""
        # 防御性兜底：page_size 必须 ≥1，否则下方计算总页数会除零
        if not page_size or page_size < 1:
            page_size = 20
        query = "SELECT * FROM accounts WHERE is_deleted = 0"
        count_query = "SELECT COUNT(*) FROM accounts WHERE is_deleted = 0"
        params = []

        if ledger_id:
            query += " AND ledger_id = ?"
            count_query += " AND ledger_id = ?"
            params.append(ledger_id)
        if start_date:
            query += " AND transaction_date >= ?"
            count_query += " AND transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= ?"
            count_query += " AND transaction_date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            count_query += " AND category = ?"
            params.append(category)
        if transaction_type:
            query += " AND transaction_type = ?"
            count_query += " AND transaction_type = ?"
            params.append(transaction_type)

        # 获取总数
        with self._get_connection() as conn:
            cursor = conn.execute(count_query, params)
            total = cursor.fetchone()[0]

        # 分页查询
        offset = (page - 1) * page_size
        query += " ORDER BY transaction_date DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            items = [self._row_to_account(row) for row in cursor.fetchall()]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
            "items": items
        }

    def update_account(self, account_id: int, account: Account) -> bool:
        """更新账目记录"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE accounts SET
                    transaction_date = ?, amount = ?, item_name = ?,
                    category = ?, merchant_name = ?, payment_method = ?,
                    transaction_type = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND is_deleted = 0
            """, (
                account.transaction_date, float(account.amount), account.item_name,
                account.category, account.merchant_name, account.payment_method,
                account.transaction_type, account.notes, account_id
            ))
            return cursor.rowcount > 0

    def delete_account(self, account_id: int) -> bool:
        """软删除账目记录"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE accounts SET is_deleted = 1 WHERE id = ?",
                (account_id,)
            )
            return cursor.rowcount > 0

    def get_statistics(self, start_date: str, end_date: str, ledger_id: Optional[int] = None) -> dict:
        """获取统计信息"""
        with self._get_connection() as conn:
            # 基础条件
            base_condition = "is_deleted = 0 AND transaction_date BETWEEN ? AND ?"
            params = [start_date, end_date]

            # 添加账本过滤
            if ledger_id:
                base_condition += " AND ledger_id = ?"
                params.append(ledger_id)

            # 总支出
            cursor = conn.execute(f"""
                SELECT SUM(amount) FROM accounts
                WHERE transaction_type = '支出' AND {base_condition}
            """, params)
            total_expense = cursor.fetchone()[0] or 0

            # 总收入
            cursor = conn.execute(f"""
                SELECT SUM(amount) FROM accounts
                WHERE transaction_type = '收入' AND {base_condition}
            """, params)
            total_income = cursor.fetchone()[0] or 0

            # 分类统计
            cursor = conn.execute(f"""
                SELECT category, transaction_type, SUM(amount) as total
                FROM accounts
                WHERE {base_condition}
                GROUP BY category, transaction_type
                ORDER BY total DESC
            """, params)
            category_stats = {}
            for row in cursor.fetchall():
                category, trans_type, total = row
                if category not in category_stats:
                    category_stats[category] = {"收入": 0, "支出": 0}
                category_stats[category][trans_type] = total

            return {
                "total_expense": float(total_expense),
                "total_income": float(total_income),
                "balance": float(total_income - total_expense),
                "category_stats": category_stats
            }

    @staticmethod
    def _parse_beijing_time(dt_str):
        """解析时间字符串并转换为北京时间"""
        if not dt_str:
            return None
        # 定义北京时区（UTC+8）
        BEIJING_TZ = timezone(timedelta(hours=8))
        # SQLite返回的时间不带时区，解析为UTC时间
        dt = datetime.fromisoformat(dt_str)
        # 如果时间没有时区信息，假设是UTC时间，转换为北京时间
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(BEIJING_TZ)

    @staticmethod
    def _row_to_account(row) -> Account:
        """将数据库行转换为Account对象"""
        return Account(
            id=row["id"],
            ledger_id=row["ledger_id"],
            transaction_date=row["transaction_date"],
            amount=Decimal(str(row["amount"])),
            item_name=row["item_name"],
            category=row["category"],
            merchant_name=row["merchant_name"],
            payment_method=row["payment_method"],
            transaction_type=row["transaction_type"],
            notes=row["notes"],
            image_path=row["image_path"],
            receipt_type=row["receipt_type"],
            confidence=row["confidence"],
            created_at=DatabaseManager._parse_beijing_time(row["created_at"]),
            updated_at=DatabaseManager._parse_beijing_time(row["updated_at"]),
            is_deleted=bool(row["is_deleted"])
        )

    # ========== 用户相关方法 ==========

    def create_user(self, user: User) -> int:
        """创建用户"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO users (username, email, hashed_password, is_active)
                VALUES (?, ?, ?, ?)
            """, (user.username, user.email, user.hashed_password, user.is_active))
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    @staticmethod
    def _row_to_user(row) -> User:
        """将数据库行转换为User对象"""
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            is_active=bool(row["is_active"]),
            created_at=DatabaseManager._parse_beijing_time(row["created_at"]),
            updated_at=DatabaseManager._parse_beijing_time(row["updated_at"])
        )

    # ========== 账本相关方法 ==========

    def create_ledger(self, ledger: Ledger) -> int:
        """创建账本"""
        # 检查同名账本
        if self.check_ledger_name_exists(ledger.user_id, ledger.name):
            raise ValueError("账本名称已存在")

        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO ledgers (user_id, name, description, icon, color, is_default)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ledger.user_id, ledger.name, ledger.description, ledger.icon, ledger.color, ledger.is_default))
            return cursor.lastrowid

    def check_ledger_name_exists(self, user_id: Optional[int], name: str, exclude_id: Optional[int] = None) -> bool:
        """检查账本名称是否已存在"""
        if user_id is None:
            return False

        with self._get_connection() as conn:
            if exclude_id is not None:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM ledgers WHERE user_id = ? AND name = ? AND id != ? AND is_deleted = 0",
                    (user_id, name, exclude_id)
                )
            else:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM ledgers WHERE user_id = ? AND name = ? AND is_deleted = 0",
                    (user_id, name)
                )
            return cursor.fetchone()[0] > 0

    def get_ledger_by_id(self, ledger_id: int) -> Optional[Ledger]:
        """根据ID查询账本"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM ledgers WHERE id = ? AND is_deleted = 0",
                (ledger_id,)
            )
            row = cursor.fetchone()
            return self._row_to_ledger(row) if row else None

    def get_ledgers_by_user(self, user_id: int) -> List[Ledger]:
        """查询用户的所有账本"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM ledgers WHERE user_id = ? AND is_deleted = 0 ORDER BY is_default DESC, created_at DESC",
                (user_id,)
            )
            return [self._row_to_ledger(row) for row in cursor.fetchall()]

    def get_default_ledger(self, user_id: int) -> Optional[Ledger]:
        """获取用户的默认账本"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM ledgers WHERE user_id = ? AND is_default = 1 AND is_deleted = 0",
                (user_id,)
            )
            row = cursor.fetchone()
            return self._row_to_ledger(row) if row else None

    def update_ledger(self, ledger_id: int, ledger: Ledger) -> bool:
        """更新账本"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE ledgers SET
                    name = ?, description = ?, icon = ?, color = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND is_deleted = 0
            """, (ledger.name, ledger.description, ledger.icon, ledger.color, ledger_id))
            return cursor.rowcount > 0

    def delete_ledger(self, ledger_id: int) -> bool:
        """软删除账本"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE ledgers SET is_deleted = 1 WHERE id = ?",
                (ledger_id,)
            )
            return cursor.rowcount > 0

    def set_default_ledger(self, user_id: int, ledger_id: int) -> bool:
        """设置默认账本"""
        with self._get_connection() as conn:
            # 取消其他账本的默认状态
            conn.execute(
                "UPDATE ledgers SET is_default = 0 WHERE user_id = ?",
                (user_id,)
            )
            # 设置新的默认账本
            cursor = conn.execute(
                "UPDATE ledgers SET is_default = 1 WHERE id = ? AND user_id = ?",
                (ledger_id, user_id)
            )
            return cursor.rowcount > 0

    def get_trend(
        self,
        start_date: str,
        end_date: str,
        ledger_id: int,
        group_by: str = "month"
    ) -> List[Dict]:
        """按天/月分组统计收支趋势（含端点日期）"""
        date_expr = "strftime('%Y-%m', transaction_date)" if group_by == "month" else "transaction_date"

        with self._get_connection() as conn:
            cursor = conn.execute(f"""
                SELECT {date_expr} as date, transaction_type, SUM(amount) as total
                FROM accounts
                WHERE ledger_id = ? AND transaction_date >= ? AND transaction_date <= ?
                AND is_deleted = 0
                GROUP BY date, transaction_type
                ORDER BY date
            """, (ledger_id, start_date, end_date))
            rows = cursor.fetchall()

        trend = {}
        for date, trans_type, total in rows:
            bucket = trend.setdefault(date, {"date": date, "income": 0.0, "expense": 0.0})
            if trans_type == "收入":
                bucket["income"] = float(total)
            else:
                bucket["expense"] = float(total)

        return list(trend.values())

    def get_ledger_account_count(self, ledger_id: int) -> int:
        """获取账本下的账单数量"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM accounts WHERE ledger_id = ? AND is_deleted = 0",
                (ledger_id,)
            )
            return cursor.fetchone()[0]

    def get_ledger_accounts(self, ledger_id: int) -> List[Dict]:
        """获取账本的所有账单（用于导出）"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    transaction_date,
                    transaction_type,
                    category,
                    item_name,
                    amount,
                    merchant_name,
                    notes,
                    image_path
                FROM accounts
                WHERE ledger_id = ? AND is_deleted = 0
                ORDER BY transaction_date DESC, created_at DESC
            """, (ledger_id,))

            columns = ['transaction_date', 'transaction_type', 'category', 'item_name',
                      'amount', 'merchant_name', 'notes', 'image_path']
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_ledger(row) -> Ledger:
        """将数据库行转换为Ledger对象"""
        return Ledger(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row["description"],
            icon=row["icon"],
            color=row["color"],
            is_default=bool(row["is_default"]),
            created_at=DatabaseManager._parse_beijing_time(row["created_at"]),
            updated_at=DatabaseManager._parse_beijing_time(row["updated_at"]),
            is_deleted=bool(row["is_deleted"])
        )

    def get_accounts_by_date(
        self,
        ledger_id: int,
        year: int,
        month: int
    ) -> Dict[str, List[Account]]:
        """按日期获取账单（用于日程视图）"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM accounts
                WHERE ledger_id = ? AND transaction_date >= ? AND transaction_date < ?
                AND is_deleted = 0
                ORDER BY transaction_date DESC, created_at DESC
            """, (ledger_id, start_date, end_date))
            rows = cursor.fetchall()

        # 按日期分组
        result = {}
        for row in rows:
            account = self._row_to_account(row)
            date = account.transaction_date
            if date not in result:
                result[date] = []
            result[date].append(account)

        return result

    # ---------- AI 会话与消息 ----------

    def create_chat_session(
        self, user_id: int, title: Optional[str] = None, ledger_id: Optional[int] = None
    ) -> int:
        """创建会话，返回会话ID；ledger_id 绑定该会话的分析账本"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO chat_sessions (user_id, title, ledger_id) VALUES (?, ?, ?)",
                (user_id, title or "新会话", ledger_id),
            )
            return cursor.lastrowid

    def get_chat_session(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        """获取会话（校验归属）"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM chat_sessions WHERE id = ? AND user_id = ?",
                (session_id, user_id),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return ChatSession(
                id=row["id"],
                user_id=row["user_id"],
                title=row["title"],
                ledger_id=row["ledger_id"],
                created_at=self._parse_beijing_time(row["created_at"]),
                updated_at=self._parse_beijing_time(row["updated_at"]),
            )

    def list_chat_sessions(self, user_id: int) -> List[Dict]:
        """列出用户会话（含消息数，按更新时间倒序）"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT s.id, s.title, s.ledger_id, s.created_at, s.updated_at,
                       (SELECT COUNT(*) FROM chat_messages m WHERE m.session_id = s.id) AS message_count
                FROM chat_sessions s
                WHERE s.user_id = ?
                ORDER BY s.updated_at DESC, s.id DESC
            """, (user_id,))
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "ledger_id": row["ledger_id"],
                    "message_count": row["message_count"],
                    "created_at": self._parse_beijing_time(row["created_at"]),
                    "updated_at": self._parse_beijing_time(row["updated_at"]),
                }
                for row in cursor.fetchall()
            ]

    def update_chat_session_title(self, session_id: int, title: str) -> bool:
        """更新会话标题"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE chat_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, session_id),
            )
            return cursor.rowcount > 0

    def touch_chat_session(self, session_id: int) -> bool:
        """更新会话的最近活动时间"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,),
            )
            return cursor.rowcount > 0

    def delete_chat_session(self, session_id: int, user_id: int) -> bool:
        """删除会话及其消息（校验归属）"""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            cursor = conn.execute(
                "DELETE FROM chat_sessions WHERE id = ? AND user_id = ?",
                (session_id, user_id),
            )
            return cursor.rowcount > 0

    def add_chat_message(self, session_id: int, role: str, content: str) -> int:
        """添加一条会话消息"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )
            return cursor.lastrowid

    def list_chat_messages(self, session_id: int) -> List[ChatMessage]:
        """获取会话的全部消息（按时间正序）"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            )
            return [
                ChatMessage(
                    id=row["id"],
                    session_id=row["session_id"],
                    role=row["role"],
                    content=row["content"],
                    created_at=self._parse_beijing_time(row["created_at"]),
                )
                for row in cursor.fetchall()
            ]

    # ==================== 回忆空间 ====================

    def create_memory(self, memory: Memory) -> int:
        """创建回忆空间"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO memories (user_id, partner_name, partner_avatar, story)
                VALUES (?, ?, ?, ?)
            """, (memory.user_id, memory.partner_name, memory.partner_avatar, memory.story))
            return cursor.lastrowid

    def get_memory_by_user(self, user_id: int) -> Optional[Memory]:
        """获取用户的回忆空间（一人一回忆）"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memories WHERE user_id = ? AND is_deleted = 0",
                (user_id,)
            )
            row = cursor.fetchone()
            return self._row_to_memory(row) if row else None

    def get_memory_by_id(self, memory_id: int) -> Optional[Memory]:
        """根据ID查询回忆空间"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ? AND is_deleted = 0",
                (memory_id,)
            )
            row = cursor.fetchone()
            return self._row_to_memory(row) if row else None

    def update_memory(self, memory_id: int, memory: Memory) -> bool:
        """更新回忆空间"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE memories SET
                    partner_name = ?, partner_avatar = ?, story = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND is_deleted = 0
            """, (memory.partner_name, memory.partner_avatar, memory.story, memory_id))
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_memory(row) -> Memory:
        """将数据库行转换为Memory对象"""
        return Memory(
            id=row["id"],
            user_id=row["user_id"],
            partner_name=row["partner_name"],
            partner_avatar=row["partner_avatar"],
            story=row["story"],
            created_at=DatabaseManager._parse_beijing_time(row["created_at"]),
            updated_at=DatabaseManager._parse_beijing_time(row["updated_at"]),
            is_deleted=bool(row["is_deleted"])
        )

    # ==================== 回忆事件 ====================

    def create_memory_event(self, event: MemoryEvent) -> int:
        """创建回忆事件"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO memory_events (memory_id, title, event_date, description, location, cover_path, author)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event.memory_id, event.title, event.event_date, event.description, event.location, event.cover_path, event.author))
            return cursor.lastrowid

    def get_memory_event_by_id(self, event_id: int) -> Optional[MemoryEvent]:
        """根据ID查询回忆事件"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memory_events WHERE id = ? AND is_deleted = 0",
                (event_id,)
            )
            row = cursor.fetchone()
            return self._row_to_memory_event(row) if row else None

    def get_memory_events(self, memory_id: int) -> List[MemoryEvent]:
        """获取回忆下的所有事件（按事件日期倒序）"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memory_events WHERE memory_id = ? AND is_deleted = 0 ORDER BY event_date DESC, created_at DESC",
                (memory_id,)
            )
            return [self._row_to_memory_event(row) for row in cursor.fetchall()]

    def update_memory_event(self, event_id: int, event: MemoryEvent) -> bool:
        """更新回忆事件"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE memory_events SET
                    title = ?, event_date = ?, description = ?, location = ?, cover_path = ?, author = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND is_deleted = 0
            """, (event.title, event.event_date, event.description, event.location, event.cover_path, event.author, event_id))
            return cursor.rowcount > 0

    def delete_memory_event(self, event_id: int) -> bool:
        """软删除回忆事件（级联软删其照片）"""
        with self._get_connection() as conn:
            # 级联软删该事件下的所有照片
            conn.execute(
                "UPDATE memory_photos SET is_deleted = 1 WHERE event_id = ?",
                (event_id,)
            )
            cursor = conn.execute(
                "UPDATE memory_events SET is_deleted = 1 WHERE id = ?",
                (event_id,)
            )
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_memory_event(row) -> MemoryEvent:
        """将数据库行转换为MemoryEvent对象"""
        return MemoryEvent(
            id=row["id"],
            memory_id=row["memory_id"],
            title=row["title"],
            event_date=row["event_date"],
            description=row["description"],
            location=row["location"],
            cover_path=row["cover_path"],
            author=row["author"],
            created_at=DatabaseManager._parse_beijing_time(row["created_at"]),
            updated_at=DatabaseManager._parse_beijing_time(row["updated_at"]),
            is_deleted=bool(row["is_deleted"])
        )

    # ==================== 回忆照片 ====================

    def create_memory_photo(self, photo: MemoryPhoto) -> int:
        """创建回忆照片记录"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO memory_photos (event_id, image_path, caption)
                VALUES (?, ?, ?)
            """, (photo.event_id, photo.image_path, photo.caption))
            return cursor.lastrowid

    def get_memory_photo_by_id(self, photo_id: int) -> Optional[MemoryPhoto]:
        """根据ID查询回忆照片"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memory_photos WHERE id = ? AND is_deleted = 0",
                (photo_id,)
            )
            row = cursor.fetchone()
            return self._row_to_memory_photo(row) if row else None

    def get_photos_by_event(self, event_id: int) -> List[MemoryPhoto]:
        """获取事件下的所有照片（按创建时间正序）"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memory_photos WHERE event_id = ? AND is_deleted = 0 ORDER BY id ASC",
                (event_id,)
            )
            return [self._row_to_memory_photo(row) for row in cursor.fetchall()]

    def delete_memory_photo(self, photo_id: int) -> bool:
        """软删除回忆照片"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE memory_photos SET is_deleted = 1 WHERE id = ?",
                (photo_id,)
            )
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_memory_photo(row) -> MemoryPhoto:
        """将数据库行转换为MemoryPhoto对象"""
        return MemoryPhoto(
            id=row["id"],
            event_id=row["event_id"],
            image_path=row["image_path"],
            caption=row["caption"],
            created_at=DatabaseManager._parse_beijing_time(row["created_at"]),
            is_deleted=bool(row["is_deleted"])
        )
