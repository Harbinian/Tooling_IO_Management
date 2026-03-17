# -*- coding: utf-8 -*-
"""
简化迁移：删除旧中文表，让schema_manager自动重建
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
    print("=" * 60)
    print("SIMPLE MIGRATION - Drop old Chinese tables")
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
        print(f"[OK] Connected to {settings.db.database}\n")

        # Tables to drop (KEEP 工装身份卡_主表!)
        tables_to_drop = [
            '工装出入库单_主表',
            '工装出入库单_明细',
            '工装出入库单_操作日志',
            '工装出入库单_通知记录',
            '工装出入库单_位置',
            '工装运输异常记录',
        ]

        # Also drop any new English tables if they exist (clean slate)
        english_tables = [
            'tool_io_order',
            'tool_io_order_item',
            'tool_io_operation_log',
            'tool_io_notification',
            'tool_io_location',
            'tool_io_transport_issue',
            'table_english_mappings',
        ]

        # Drop old Chinese tables
        print("[1] Dropping old Chinese tables...")
        for t in tables_to_drop:
            cursor.execute(f"""
                IF OBJECT_ID(N'{t}', N'U') IS NOT NULL
                    DROP TABLE [{t}]
            """)
            print(f"  Dropped: {t}")

        # Drop any partial English tables
        print("\n[2] Dropping any existing English tables (clean slate)...")
        for t in english_tables:
            cursor.execute(f"""
                IF OBJECT_ID(N'{t}', N'U') IS NOT NULL
                    DROP TABLE [{t}]
            """)
            print(f"  Dropped: {t}")

        # Drop views
        print("\n[3] Dropping backward-compat views...")
        views = [
            '工装出入库单_主表',
            '工装出入库单_明细',
            '工装出入库单_操作日志',
            '工装出入库单_通知记录',
            '工装出入库单_位置',
            '工装运输异常记录',
        ]
        for v in views:
            cursor.execute(f"""
                IF OBJECT_ID(N'{v}', N'U') IS NOT NULL
                    DROP VIEW [{v}]
            """)
            print(f"  Dropped view: {v}")

        conn.commit()

        print("\n[OK] All old tables and views dropped")
        print("\nNext step: Restart the application")
        print("  schema_manager.py will automatically create new English tables")

        conn.close()

    except pyodbc.Error as e:
        print(f"[ERROR] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
