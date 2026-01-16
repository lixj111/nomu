"""自动记账Agent主入口"""
import os
from pathlib import Path

from agent.accounting_agent import AccountingAgent


def main():
    """主函数"""
    # 配置API密钥（建议使用环境变量）
    API_KEY = os.getenv("ZHIPU_API_KEY", "your-api-key-here")

    # 初始化Agent
    agent = AccountingAgent(
        api_key=API_KEY,
        db_path="accounting.db",
        model="glm-4.6v"
    )

    print("=" * 50)
    print("欢迎使用自动记账Agent")
    print("=" * 50)

    while True:
        print("\n请选择操作:")
        print("1. 处理单张账单")
        print("2. 批量处理账单")
        print("3. 查询记账记录")
        print("4. 统计分析")
        print("5. 退出")

        choice = input("\n请输入选项 (1-5): ").strip()

        if choice == "1":
            image_path = input("请输入图片路径: ").strip()
            if os.path.exists(image_path):
                agent.process_receipt(image_path)
            else:
                print("文件不存在")

        elif choice == "2":
            folder = input("请输入图片文件夹路径: ").strip()
            if os.path.isdir(folder):
                images = [
                    str(Path(folder) / f)
                    for f in os.listdir(folder)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]
                if images:
                    agent.batch_process_receipts(images)
                else:
                    print("文件夹中没有图片文件")
            else:
                print("文件夹不存在")

        elif choice == "3":
            records = agent.query_records(limit=20)
            print(f"\n找到 {len(records)} 条记录:")
            for r in records:
                print(f"  {r.transaction_date} | {r.item_name} | ¥{r.amount} | {r.category}")

        elif choice == "4":
            start_date = input("开始日期 (YYYY-MM-DD): ").strip()
            end_date = input("结束日期 (YYYY-MM-DD): ").strip()
            stats = agent.get_statistics(start_date, end_date)
            print(f"\n统计信息 ({start_date} 至 {end_date}):")
            print(f"  总收入: ¥{stats['total_income']:.2f}")
            print(f"  总支出: ¥{stats['total_expense']:.2f}")
            print(f"  结余: ¥{stats['balance']:.2f}")
            print(f"\n分类统计:")
            for cat, amount in stats['category_stats'].items():
                print(f"  {cat}: ¥{amount:.2f}")

        elif choice == "5":
            print("再见！")
            break

        else:
            print("无效选项")


if __name__ == "__main__":
    main()
