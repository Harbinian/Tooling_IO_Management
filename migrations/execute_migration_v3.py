# -*- coding: utf-8 -*-
"""
Execute migration with better parsing - handle IF/BEGIN/END blocks properly
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
    print("=" * 60)
    print("MIGRATION EXECUTION V3")
    print("=" * 60)

    conn_str = (
        f"DRIVER={settings.db.driver};"
        f"SERVER={settings.db.server};"
        f"DATABASE={settings.db.database};"
        f"UID={settings.db.username};"
        f"PWD={settings.db.password};"
        f"Connection Timeout=120;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        conn.autocommit = False
        cursor = conn.cursor()
        print(f"[OK] Connected\n")

        sql_file = os.path.join(
            os.path.dirname(__file__),
            '001_rename_tables_to_english.sql'
        )

        with open(sql_file, 'r', encoding='utf-8') as f:
            full_sql = f.read()

        print("Executing full SQL script...")

        # The script has its own transaction handling
        # Just execute the whole thing
        try:
            cursor.execute(full_sql)
            conn.commit()
            print("[OK] Script executed successfully")
        except Exception as e:
            print(f"[ERROR] {e}")
            conn.rollback()
            print("[ROLLBACK] Transaction rolled back")
            return 1

        print("\nVerifying created objects...")

        # Check tables
        tables = [
            'tool_io_order',
            'tool_io_order_item',
            'tool_io_operation_log',
            'tool_io_notification',
            'tool_io_location',
            'tool_io_transport_issue',
            'table_english_mappings'
        ]

        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = '{t}'")
            exists = cursor.fetchone()[0] > 0
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {t}")
                count = cursor.fetchone()[0]
                print(f"  [OK] {t}: {count} rows")
            else:
                print(f"  [FAIL] {t}: MISSING")

        # Check views
        print("\nBackward-compat views:")
        views = ['工装出入库单_主表', '工装出入库单_明细', '工装出入库单_操作日志',
                 '工装出入库单_通知记录', '工装出入库单_位置', '工装运输异常记录']
        for v in views:
            cursor.execute(f"SELECT COUNT(*) FROM sys.views WHERE name = N'{v}'")
            exists = cursor.fetchone()[0] > 0
            print(f"  {'[OK]' if exists else '[FAIL]'} {v}")

        conn.close()
        print("\n[MIGRATION COMPLETE]")

    except pyodbc.Error as e:
        print(f"[ERROR] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
