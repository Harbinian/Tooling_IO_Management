# -*- coding: utf-8 -*-
"""
Execute migration V5 - proper block parsing for IF/BEGIN/END
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def parse_sql_blocks(sql_content):
    """Parse SQL into blocks, handling IF/BEGIN/END properly"""
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

    # Parse into statements, keeping BEGIN...END together
    statements = []
    current = []
    depth = 0
    in_string = False
    i = 0

    while i < len(sql):
        c = sql[i]

        # Handle string literals
        if c == "'" and (i == 0 or sql[i-1] != "'"):
            in_string = not in_string
            current.append(c)
            i += 1
            continue

        if in_string:
            current.append(c)
            i += 1
            continue

        # Track BEGIN/END depth
        if c == 'B' and sql[i:i+5] == 'BEGIN':
            depth += 1
            current.append(c)
            i += 5
            continue
        elif c == 'E' and sql[i:i+3] == 'END':
            depth -= 1
            current.append(c)
            i += 3
            continue

        # Split on semicolon only at depth 0
        if c == ';' and depth == 0:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
            continue

        current.append(c)
        i += 1

    # Don't forget remaining content
    if current:
        stmt = ''.join(current).strip()
        if stmt:
            statements.append(stmt)

    return statements


def main():
    print("=" * 60)
    print("MIGRATION EXECUTION V5 - Proper Block Parsing")
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

        statements = parse_sql_blocks(full_sql)
        print(f"Parsed {len(statements)} blocks\n")

        success = 0
        failed = 0
        errors = []

        for i, stmt in enumerate(statements, 1):
            stmt_upper = stmt.upper().strip()

            # Skip transaction control
            if stmt_upper.startswith('SET XACT_ABORT'):
                print(f"[{i:3d}] SET XACT_ABORT - skipped")
                continue
            if stmt_upper.startswith('BEGIN TRANSACTION'):
                print(f"[{i:3d}] BEGIN TRANSACTION - skipped")
                continue
            if stmt_upper.startswith('COMMIT TRANSACTION'):
                print(f"[{i:3d}] COMMIT - executing...")
                conn.commit()
                success += 1
                continue
            if stmt_upper.startswith('ROLLBACK TRANSACTION'):
                print(f"[{i:3d}] ROLLBACK - executing...")
                conn.rollback()
                success += 1
                continue

            # Preview
            preview = stmt[:70].replace('\n', ' ')
            if len(stmt) > 70:
                preview += '...'
            print(f"[{i:3d}] {preview[:70]}")

            try:
                cursor.execute(stmt)
                success += 1
            except Exception as e:
                failed += 1
                err_msg = str(e)
                errors.append((i, preview, err_msg))
                print(f"\n[{i:3d}] ERROR: {err_msg[:100]}")

                print("\n[ROLLING BACK]")
                conn.rollback()
                break

        print(f"\n{'='*60}")
        print(f"RESULT: {success} succeeded, {failed} failed")
        print(f"{'='*60}")

        if failed == 0:
            print("\nVerifying results...")
            tables = ['tool_io_order', 'tool_io_order_item', 'tool_io_operation_log',
                      'tool_io_notification', 'tool_io_location', 'tool_io_transport_issue',
                      'table_english_mappings']
            for t in tables:
                cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = '{t}'")
                exists = cursor.fetchone()[0] > 0
                if exists:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    count = cursor.fetchone()[0]
                    print(f"  [OK] {t}: {count} rows")
                else:
                    print(f"  [FAIL] {t}: MISSING")

            print("\nBackward-compat views:")
            for v in ['工装出入库单_主表', '工装出入库单_明细']:
                cursor.execute(f"SELECT COUNT(*) FROM sys.views WHERE name = N'{v}'")
                exists = cursor.fetchone()[0] > 0
                print(f"  {'[OK]' if exists else '[FAIL]'} {v}")

            print("\n[MIGRATION COMPLETE]")
        else:
            print("\nErrors:")
            for num, preview, err in errors:
                print(f"  Statement {num}: {preview[:50]}")
                print(f"    {err}")

        conn.close()

    except pyodbc.Error as e:
        print(f"[ERROR] {e}")
        return 1

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
