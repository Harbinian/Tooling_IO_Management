# -*- coding: utf-8 -*-
"""
Check actual database column names - write to file
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def get_columns(cursor, table_name):
    cursor.execute(f"""
        SELECT name FROM sys.columns
        WHERE object_id = OBJECT_ID('{table_name}')
        ORDER BY column_id
    """)
    return [row[0] for row in cursor.fetchall()]


def main():
    output_file = os.path.join(os.path.dirname(__file__), 'actual_columns.txt')

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

    tables = [
        '工装出入库单_主表',
        '工装出入库单_明细',
        '工装出入库单_操作日志',
        '工装出入库单_通知记录',
        '工装出入库单_位置',
        '工装运输异常记录',
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ACTUAL COLUMN NAMES IN DATABASE\n")
        f.write("=" * 60 + "\n\n")

        for table in tables:
            f.write(f"[{table}]\n")
            cols = get_columns(cursor, table)
            for c in cols:
                f.write(f"  - {c}\n")
            f.write("\n")

    conn.close()
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
