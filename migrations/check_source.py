# -*- coding: utf-8 -*-
"""
Check if source table has BOTH 运输人ID and 运输AssigneeID columns
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def check_columns(cursor, table_name, column_names):
    """Check if columns exist in table"""
    cursor.execute(f"""
        SELECT name FROM sys.columns
        WHERE object_id = OBJECT_ID('{table_name}')
        AND name IN ({','.join(['?' for _ in column_names])})
    """, column_names)
    return [row[0] for row in cursor.fetchall()]


def main():
    print("=" * 60)
    print("CHECKING FOR COLUMN CONFLICTS")
    print("=" * 60)

    conn_str = (
        f"DRIVER={settings.db.driver};"
        f"SERVER={settings.db.server};"
        f"DATABASE={settings.db.database};"
        f"UID={settings.db.username};"
        f"PWD={settings.db.password};"
        f"Connection Timeout=30;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    table = '工装出入库单_主表'

    # Check specific columns
    cols_to_check = [
        '运输人ID',
        '运输人姓名',
        '运输AssigneeID',
        '运输AssigneeName',
    ]

    print(f"\nChecking columns in [{table}]:")
    found = check_columns(cursor, table, cols_to_check)
    print(f"  Found: {found}")

    if '运输人ID' in found and '运输AssigneeID' in found:
        print("\n[ERROR] Table has BOTH columns - SELECT * INTO would FAIL!")
        print("  This is a schema inconsistency.")
    elif '运输人ID' in found:
        print("\n[INFO] Table has 运输人ID (NOT 运输AssigneeID)")
    elif '运输AssigneeID' in found:
        print("\n[INFO] Table has 运输AssigneeID (NOT 运输人ID)")
    else:
        print("\n[WARN] Neither column found")

    conn.close()


if __name__ == "__main__":
    main()
