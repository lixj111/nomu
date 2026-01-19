"""数据库操作封装"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal

from .models import Account, Ledger, User


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

            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ledgers_user_id ON ledgers(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ledgers_default ON ledgers(is_default)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_ledger_id ON accounts(ledger_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_transaction_date ON accounts(transaction_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_category ON accounts(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_transaction_type ON accounts(transaction_type)")

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
        except Exception:
            # 如果迁移失败，忽略（表可能已经是新结构）
            pass

    def add_account(self, account: Account) -> int:
        """添加账目记录"""
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
            return cursor.lastrowid

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
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
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
    def _row_to_account(row) -> Account:
        """将数据库行转换为Account对象"""
        return Account(
            id=row["id"],
            ledger_id=row.get("ledger_id"),
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
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
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
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None
        )

    # ========== 账本相关方法 ==========

    def create_ledger(self, ledger: Ledger) -> int:
        """创建账本"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO ledgers (user_id, name, description, icon, color, is_default)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ledger.user_id, ledger.name, ledger.description, ledger.icon, ledger.color, ledger.is_default))
            return cursor.lastrowid

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

    def get_ledger_account_count(self, ledger_id: int) -> int:
        """获取账本下的账单数量"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM accounts WHERE ledger_id = ? AND is_deleted = 0",
                (ledger_id,)
            )
            return cursor.fetchone()[0]

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
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
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
