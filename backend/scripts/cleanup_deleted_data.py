"""清理已软删除的账本和账单数据

此脚本会硬删除：
1. ledgers表中所有is_deleted=1的记录
2. accounts表中所有is_deleted=1的记录
3. accounts表中关联到已删除账本的记录

警告：此操作不可逆，请在运行前备份数据库！
"""
import sqlite3
import sys
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def cleanup_deleted_data(db_path: str = "accounting.db", dry_run: bool = True):
    """清理已删除的数据

    Args:
        db_path: 数据库文件路径
        dry_run: 是否为试运行模式（True=只显示，不执行；False=实际删除）
    """
    if not Path(db_path).exists():
        print(f"[错误] 数据库文件不存在: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        # 查询将要删除的数据
        print("=" * 60)
        print("[扫描] 待删除数据...")
        print("=" * 60)

        # 1. 查询已删除的账本
        cursor.execute("""
            SELECT id, name, user_id, created_at
            FROM ledgers
            WHERE is_deleted = 1
            ORDER BY id
        """)
        deleted_ledgers = cursor.fetchall()

        print(f"\n[已删除账本] 数量: {len(deleted_ledgers)}")
        for ledger in deleted_ledgers:
            print(f"   - ID: {ledger['id']}, 名称: {ledger['name']}, 用户ID: {ledger['user_id']}")

        # 2. 查询已删除账本关联的账单
        if deleted_ledgers:
            ledger_ids = ",".join(str(l['id']) for l in deleted_ledgers)
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM accounts
                WHERE ledger_id IN ({ledger_ids})
            """)
            related_accounts = cursor.fetchone()['count']
            print(f"\n[关联账单] 数量: {related_accounts}")
        else:
            related_accounts = 0
            print(f"\n[关联账单] 数量: 0")

        # 3. 查询已标记删除的账单（软删除）
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM accounts
            WHERE is_deleted = 1
        """)
        soft_deleted_accounts = cursor.fetchone()['count']
        print(f"[软删除账单] 数量: {soft_deleted_accounts}")

        print("\n" + "=" * 60)

        # 统计将要删除的总数
        total_accounts = related_accounts + soft_deleted_accounts
        total_ledgers = len(deleted_ledgers)

        if dry_run:
            print("[试运行模式] 以下数据将被删除：")
            print(f"   - 账本: {total_ledgers} 条")
            print(f"   - 账单: {total_accounts} 条")
            print("\n[提示] 如需实际执行，请运行: python cleanup_deleted_data.py --execute")
            print("   或者先备份数据库！")
        else:
            # 确认删除
            print("[警告] 即将执行硬删除操作！")
            print(f"   - 账本: {total_ledgers} 条")
            print(f"   - 账单: {total_accounts} 条")
            confirm = input("\n[确认] 确认要删除这些数据吗？(输入 'yes' 确认): ")

            if confirm.lower() != 'yes':
                print("[取消] 操作已取消")
                return

            print("\n[删除] 开始删除...")

            # 先删除账单（因为有关联约束）
            if deleted_ledgers:
                # 删除关联到已删除账本的账单
                cursor.execute(f"""
                    DELETE FROM accounts
                    WHERE ledger_id IN ({ledger_ids})
                """)
                print(f"   [完成] 删除关联账单: {cursor.rowcount} 条")

            # 删除软删除的账单
            cursor.execute("""
                DELETE FROM accounts
                WHERE is_deleted = 1
            """)
            print(f"   [完成] 删除软删除账单: {cursor.rowcount} 条")

            # 删除已删除的账本
            cursor.execute("""
                DELETE FROM ledgers
                WHERE is_deleted = 1
            """)
            print(f"   [完成] 删除已删除账本: {cursor.rowcount} 条")

            conn.commit()
            print("\n[完成] 清理完成！")

            # 显示清理后的统计
            cursor.execute("SELECT COUNT(*) as count FROM ledgers")
            print(f"[统计] 剩余账本: {cursor.fetchone()['count']} 条")

            cursor.execute("SELECT COUNT(*) as count FROM accounts")
            print(f"[统计] 剩余账单: {cursor.fetchone()['count']} 条")

    except Exception as e:
        conn.rollback()
        print(f"\n[错误] 发生错误: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="清理已软删除的账本和账单数据")
    parser.add_argument(
        "--db",
        default="accounting.db",
        help="数据库文件路径 (默认: accounting.db)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实际执行删除操作（默认为试运行模式）"
    )

    args = parser.parse_args()

    # 如果使用相对路径，从脚本所在目录查找
    db_path = args.db
    if not Path(db_path).is_absolute():
        script_dir = Path(__file__).parent
        db_path = script_dir / db_path

    cleanup_deleted_data(str(db_path), dry_run=not args.execute)
