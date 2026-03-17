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
    cursor.execute(f"""
        SELECT name FROM sys.columns
        WHERE object_id = OBJECT_ID('{table_name}')
        AND name IN ({','.join(['?' for _ in column_names])})
    """, column_names)
    return [row[0] for row in cursor.fetchall()]


def main():
    output_file = os.path.join(os.path.dirname(__file__), 'column_conflict_check.txt')

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

    cols_to_check = [
        '运输人ID',
        '运输人姓名',
        '运输AssigneeID',
        '运输AssigneeName',
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Checking columns in [{table}]:\n\n")
        found = check_columns(cursor, table, cols_to_check)
        f.write(f"Found columns: {found}\n\n")

        if '运输人ID' in found and '运输AssigneeID' in found:
            f.write("[ERROR] Table has BOTH '运输人ID' and '运输AssigneeID'!\n")
            f.write("SELECT * INTO would create duplicate column names and FAIL.\n")
        elif '运输人ID' in found:
            f.write("[INFO] Table has '运输人ID' (NOT '运输AssigneeID')\n")
        elif '运输AssigneeID' in found:
            f.write("[INFO] Table has '运输AssigneeID' (NOT '运输人ID')\n")
        else:
            f.write("[WARN] Neither column found\n")

    conn.close()
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
