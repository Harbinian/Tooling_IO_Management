# -*- coding: utf-8 -*-
"""
Debug statement 3 - print exact content
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def split_sql_statements(sql_content):
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
    parts = sql.split(';')

    statements = []
    for part in parts:
        stmt = part.strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)

    return statements


def main():
    sql_file = os.path.join(
        os.path.dirname(__file__),
        '001_rename_tables_to_english.sql'
    )

    with open(sql_file, 'r', encoding='utf-8') as f:
        full_sql = f.read()

    statements = split_sql_statements(full_sql)

    # Print statement 3
    stmt3 = statements[2]  # 0-indexed, so statement 3 is index 2

    print("Statement 3 content:")
    print("-" * 60)
    print(stmt3)
    print("-" * 60)
    print(f"\nLength: {len(stmt3)} characters")

    # Try to execute it
    print("\nTrying to execute...")

    conn_str = (
        f"DRIVER={settings.db.driver};"
        f"SERVER={settings.db.server};"
        f"DATABASE={settings.db.database};"
        f"UID={settings.db.username};"
        f"PWD={settings.db.password};"
        f"Connection Timeout=30;"
    )

    conn = pyodbc.connect(conn_str)
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        cursor.execute(stmt3)
        conn.commit()
        print("[OK] Statement 3 executed successfully")
    except Exception as e:
        print(f"[ERROR] {e}")

        # Try character by character to find the problem
        print("\n\nTrying with just the IF part...")
        if_part = stmt3[:stmt3.index('BEGIN') + 5]
        print(f"IF part: {if_part}")
        try:
            cursor.execute(if_part)
            print("[OK] IF part works")
        except Exception as e2:
            print(f"[ERROR] IF part: {e2}")

    conn.close()


if __name__ == "__main__":
    main()
