# -*- coding: utf-8 -*-
"""
Execute migration V4 - split by semicolons and execute individually
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def split_sql_statements(sql_content):
    """Split SQL content into individual statements by semicolon"""
    statements = []

    # Remove comments
    lines = []
    for line in sql_content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('--'):
            continue
        if '/*' in stripped:
            stripped = stripped[:stripped.index('/*')]
        if '*/' in stripped:
            stripped = stripped[stripped.index('*/')+2:]
        if stripped:
            lines.append(line)

    sql = '\n'.join(lines)

    # Split by semicolon, keeping the statement
    parts = sql.split(';')

    for part in parts:
        stmt = part.strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)

    return statements


def main():
    print("=" * 60)
    print("MIGRATION EXECUTION V4 - Individual Statements")
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

        statements = split_sql_statements(full_sql)
        print(f"Parsed {len(statements)} statements\n")

        # Skip transaction control, handle manually
        success = 0
        failed = 0
        errors = []

        for i, stmt in enumerate(statements, 1):
            stmt_upper = stmt.upper().strip()

            # Skip transaction control statements
            if stmt_upper.startswith('SET XACT_ABORT ON'):
                print(f"[{i:3d}] SET XACT_ABORT - skipped")
                continue
            if stmt_upper.startswith('BEGIN TRANSACTION'):
                print(f"[{i:3d}] BEGIN TRANSACTION - skipped")
                continue
            if stmt_upper.startswith('COMMIT TRANSACTION'):
                print(f"[{i:3d}] COMMIT - executing...")
                conn.commit()
                success += 1
                print(f"[{i:3d}] COMMIT - OK")
                continue
            if stmt_upper.startswith('ROLLBACK TRANSACTION'):
                print(f"[{i:3d}] ROLLBACK - executing...")
                conn.rollback()
                success += 1
                continue

            # Preview
            preview = stmt[:60].replace('\n', ' ')
            if len(stmt) > 60:
                preview += '...'
            print(f"[{i:3d}] {preview}")

            try:
                cursor.execute(stmt)
                success += 1
            except Exception as e:
                failed += 1
                err_msg = str(e)
                errors.append((i, preview, err_msg))
                print(f"[{i:3d}] ERROR: {err_msg[:80]}")

                # Rollback on first error
                print("\n[ROLLING BACK]")
                conn.rollback()
                break

        print(f"\n{'='*60}")
        print(f"RESULT: {success} succeeded, {failed} failed")
        print(f"{'='*60}")

        if errors:
            print("\nErrors encountered:")
            for num, preview, err in errors:
                print(f"  Statement {num}: {preview}")
                print(f"    Error: {err}")

        if failed == 0:
            print("\nVerifying results...")
            tables = ['tool_io_order', 'tool_io_order_item', 'tool_io_operation_log',
                      'tool_io_notification', 'tool_io_location', 'tool_io_transport_issue']
            for t in tables:
                cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = '{t}'")
                exists = cursor.fetchone()[0] > 0
                if exists:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    count = cursor.fetchone()[0]
                    print(f"  [OK] {t}: {count} rows")

        conn.close()

    except pyodbc.Error as e:
        print(f"[ERROR] {e}")
        return 1

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
