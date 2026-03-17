# -*- coding: utf-8 -*-
"""
执行数据库迁移脚本 - 仅用于测试环境！
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def execute_sql_file(cursor, sql_file_path):
    """Execute SQL file with GO statement splitting"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by GO statements (SQL Server batch separator)
    # But since we're using transactions, we'll execute as one batch
    statements = []

    # Simple split - in production would need proper parser
    # For this migration script, execute line by line carefully
    current_stmt = []
    in_comment = False

    for line in sql_content.split('\n'):
        stripped = line.strip()

        # Skip comment lines for execution
        if stripped.startswith('--'):
            continue

        if stripped.startswith('/*'):
            in_comment = True
            continue
        if in_comment:
            if stripped.endswith('*/'):
                in_comment = False
            continue

        current_stmt.append(line)

        # Execute on certain keywords that end statements
        if stripped.endswith(';') and not in_comment:
            stmt = '\n'.join(current_stmt)
            if stmt.strip():
                statements.append(stmt)
            current_stmt = []

    # Execute remaining
    if current_stmt:
        stmt = '\n'.join(current_stmt)
        if stmt.strip():
            statements.append(stmt)

    return statements


def main():
    print("=" * 60)
    print("EXECUTING MIGRATION SCRIPT - TEST ENVIRONMENT")
    print("=" * 60)

    # Confirmation
    print("\n[WARNING] This will create new English tables and views!")
    print("[WARNING] Old Chinese tables will be kept (not dropped)!")
    print("\nPress Ctrl+C to cancel, or wait 5 seconds to continue...")

    import time
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return 1

    conn_str = (
        f"DRIVER={settings.db.driver};"
        f"SERVER={settings.db.server};"
        f"DATABASE={settings.db.database};"
        f"UID={settings.db.username};"
        f"PWD={settings.db.password};"
        f"Connection Timeout=60;"
    )

    try:
        print(f"\nConnecting to {settings.db.server}/{settings.db.database}...")
        conn = pyodbc.connect(conn_str)
        conn.autocommit = False  # We'll use the transaction in the script
        cursor = conn.cursor()
        print("[OK] Connected\n")

        # Read and execute migration script
        sql_file = os.path.join(
            os.path.dirname(__file__),
            '001_rename_tables_to_english.sql'
        )

        print(f"Reading migration script: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        print("\nExecuting migration script...")
        print("(This may take a while due to data copying)\n")

        # Execute the entire script (it has its own BEGIN/COMMIT TRANSACTION)
        cursor.execute(sql)

        # Commit
        conn.commit()

        print("\n[MIGRATION EXECUTED SUCCESSFULLY]")
        print("\nVerifying results...")

        # Verify tables were created
        tables = [
            'tool_io_order',
            'tool_io_order_item',
            'tool_io_operation_log',
            'tool_io_notification',
            'tool_io_location',
            'tool_io_transport_issue',
            'table_english_mappings'
        ]

        print("\nCreated tables:")
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = '{t}'")
            exists = cursor.fetchone()[0] > 0
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {t}")
                count = cursor.fetchone()[0]
                print(f"  {t}: EXISTS ({count} rows)")
            else:
                print(f"  {t}: MISSING!")

        # Check views
        views = [
            '工装出入库单_主表',
            '工装出入库单_明细',
            '工装出入库单_操作日志',
            '工装出入库单_通知记录',
            '工装出入库单_位置',
            '工装运输异常记录'
        ]

        print("\nBackward-compat views:")
        for v in views:
            cursor.execute(f"SELECT COUNT(*) FROM sys.views WHERE name = N'{v}'")
            exists = cursor.fetchone()[0] > 0
            print(f"  {v}: {'EXISTS' if exists else 'MISSING'}")

        conn.close()

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Verify data in new tables")
        print("2. Test application functionality")
        print("3. When ready, drop old tables:")
        print("   DROP TABLE 工装出入库单_主表;")
        print("   DROP TABLE 工装出入库单_明细;")
        print("   ...")

    except pyodbc.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        if 'conn' in dir():
            conn.rollback()
            print("[ROLLBACK] Transaction rolled back")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
