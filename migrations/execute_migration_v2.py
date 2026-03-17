# -*- coding: utf-8 -*-
"""
执行数据库迁移脚本 V2 - 分段执行
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def parse_sql_file(sql_file_path):
    """Parse SQL file into individual statements"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    statements = []
    current_stmt = []
    in_multiline_comment = False

    for line in content.split('\n'):
        stripped = line.strip()

        # Skip single-line comments
        if stripped.startswith('--'):
            continue

        # Handle multiline comments
        if '/*' in stripped:
            in_multiline_comment = True
        if in_multiline_comment:
            if '*/' in stripped:
                in_multiline_comment = False
            continue

        current_stmt.append(line)

        # End statement on semicolon
        if stripped.endswith(';'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt and not stmt.startswith('/*'):
                statements.append(stmt)
            current_stmt = []

    return statements


def main():
    print("=" * 60)
    print("MIGRATION SCRIPT EXECUTION V2")
    print("=" * 60)

    conn_str = (
        f"DRIVER={settings.db.driver};"
        f"SERVER={settings.db.server};"
        f"DATABASE={settings.db.database};"
        f"UID={settings.db.username};"
        f"PWD={settings.db.password};"
        f"Connection Timeout=60;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        conn.autocommit = False
        cursor = conn.cursor()
        print(f"[OK] Connected to {settings.db.database}\n")

        # Parse migration script
        sql_file = os.path.join(
            os.path.dirname(__file__),
            '001_rename_tables_to_english.sql'
        )

        statements = parse_sql_file(sql_file)
        print(f"Parsed {len(statements)} SQL statements\n")

        # Execute each statement
        success_count = 0
        fail_count = 0

        for i, stmt in enumerate(statements, 1):
            # Skip transaction control statements
            if 'SET XACT_ABORT' in stmt.upper():
                print(f"[{i:3d}] SET XACT_ABORT ON - skipped (handled by Python)")
                continue
            if 'BEGIN TRANSACTION' in stmt.upper():
                print(f"[{i:3d}] BEGIN TRANSACTION - skipped (handled by Python)")
                continue
            if 'COMMIT TRANSACTION' in stmt.upper():
                print(f"[{i:3d}] COMMIT TRANSACTION - executing...")
                conn.commit()
                success_count += 1
                print(f"[{i:3d}] COMMIT - OK")
                continue
            if 'ROLLBACK TRANSACTION' in stmt.upper():
                print(f"[{i:3d}] ROLLBACK TRANSACTION - executing...")
                conn.rollback()
                success_count += 1
                print(f"[{i:3d}] ROLLBACK - OK")
                continue

            # Print statement preview
            preview = stmt[:80].replace('\n', ' ')
            if len(stmt) > 80:
                preview += '...'
            print(f"[{i:3d}] {preview}")

            try:
                cursor.execute(stmt)
                success_count += 1
            except pyodbc.Error as e:
                print(f"[{i:3d}] ERROR: {e}")
                fail_count += 1
                print("\n[ROLLBACK] Due to error, rolling back transaction...")
                conn.rollback()
                return 1

        print(f"\n{'='*60}")
        print(f"EXECUTION COMPLETE: {success_count} succeeded, {fail_count} failed")
        print(f"{'='*60}")

        # Verify results
        print("\nVerifying created objects...")
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
                print(f"  {t}: OK ({count} rows)")
            else:
                print(f"  {t}: MISSING!")

        views = ['工装出入库单_主表', '工装出入库单_明细']
        for v in views:
            cursor.execute(f"SELECT COUNT(*) FROM sys.views WHERE name = N'{v}'")
            exists = cursor.fetchone()[0] > 0
            print(f"  View {v}: {'OK' if exists else 'MISSING'}")

        conn.close()

    except pyodbc.Error as e:
        print(f"[ERROR] {e}")
        if 'conn' in dir():
            conn.rollback()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
