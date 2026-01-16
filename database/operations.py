"""数据库操作封装"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from .models import Account


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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    is_deleted BOOLEAN DEFAULT 0
                )
            """)

            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transaction_date ON accounts(transaction_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON accounts(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transaction_type ON accounts(transaction_type)")

    def add_account(self, account: Account) -> int:
        """添加账目记录"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO accounts (
                    transaction_date, amount, item_name, category,
                    merchant_name, payment_method, transaction_type,
                    notes, image_path, receipt_type, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Account]:
        """查询账目列表（支持筛选）"""
        query = "SELECT * FROM accounts WHERE is_deleted = 0"
        params = []

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

    def get_statistics(self, start_date: str, end_date: str) -> dict:
        """获取统计信息"""
        with self._get_connection() as conn:
            # 总支出
            cursor = conn.execute("""
                SELECT SUM(amount) FROM accounts
                WHERE transaction_type = '支出'
                AND transaction_date BETWEEN ? AND ?
                AND is_deleted = 0
            """, (start_date, end_date))
            total_expense = cursor.fetchone()[0] or 0

            # 总收入
            cursor = conn.execute("""
                SELECT SUM(amount) FROM accounts
                WHERE transaction_type = '收入'
                AND transaction_date BETWEEN ? AND ?
                AND is_deleted = 0
            """, (start_date, end_date))
            total_income = cursor.fetchone()[0] or 0

            # 分类统计
            cursor = conn.execute("""
                SELECT category, SUM(amount) as total
                FROM accounts
                WHERE transaction_date BETWEEN ? AND ?
                AND is_deleted = 0
                GROUP BY category
                ORDER BY total DESC
            """, (start_date, end_date))
            category_stats = {row[0]: row[1] for row in cursor.fetchall()}

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
