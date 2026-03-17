# -*- coding: utf-8 -*-
"""
简化迁移 V2 - 处理外键约束
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
    print("=" * 60)
    print("SIMPLE MIGRATION V2 - With FK handling")
    print("=" * 60)

    conn_str = (
        f"DRIVER={settings.db.driver};"
        f"SERVER={settings.db.server};"
        f"DATABASE={settings.db.database};"
        f"UID={settings.db.username};"
        f"PWD={settings.db.password};"
        f"Connection Timeout=30;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print(f"[OK] Connected\n")

        # Drop child tables first (order matters!)
        child_tables = [
            '工装出入库单_明细',       # child of 主表
            '工装出入库单_操作日志',   # child of 主表
            '工装出入库单_通知记录',   # child of 主表
            '工装出入库单_位置',
            '工装运输异常记录',
        ]

        parent_table = '工装出入库单_主表'

        print("[1] Dropping child tables first...")
        for t in child_tables:
            try:
                cursor.execute(f"""
                    IF OBJECT_ID(N'{t}', N'U') IS NOT NULL
                        DROP TABLE [{t}]
                """)
                print(f"  Dropped: {t}")
            except Exception as e:
                print(f"  {t}: {e}")

        print(f"\n[2] Dropping parent table: {parent_table}")
        cursor.execute(f"""
            IF OBJECT_ID(N'{parent_table}', N'U') IS NOT NULL
                DROP TABLE [{parent_table}]
        """)
        print(f"  Dropped: {parent_table}")

        # Drop any English tables
        print("\n[3] Dropping English tables if exist...")
        english_tables = [
            'tool_io_order', 'tool_io_order_item',
            'tool_io_operation_log', 'tool_io_notification',
            'tool_io_location', 'tool_io_transport_issue',
            'table_english_mappings',
        ]
        for t in english_tables:
            cursor.execute(f"""
                IF OBJECT_ID(N'{t}', N'U') IS NOT NULL
                    DROP TABLE [{t}]
            """)
            print(f"  Dropped: {t}")

        # Drop views
        print("\n[4] Dropping views...")
        views = ['工装出入库单_主表', '工装出入库单_明细',
                 '工装出入库单_操作日志', '工装出入库单_通知记录',
                 '工装出入库单_位置', '工装运输异常记录']
        for v in views:
            cursor.execute(f"""
                IF OBJECT_ID(N'{v}', N'U') IS NOT NULL
                    DROP VIEW [{v}]
            """)
            print(f"  Dropped view: {v}")

        conn.commit()

        print("\n[OK] All old tables dropped successfully!")
        print("\nRestart the application - schema_manager will create new English tables")

        conn.close()

    except pyodbc.Error as e:
        print(f"[ERROR] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
