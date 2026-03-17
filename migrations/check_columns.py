# -*- coding: utf-8 -*-
"""
检查实际数据库列名 - 输出纯ASCII用于调试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def get_columns(cursor, table_name):
    """获取表的列名"""
    cursor.execute(f"""
        SELECT name FROM sys.columns
        WHERE object_id = OBJECT_ID('{table_name}')
        ORDER BY column_id
    """)
    return [row[0] for row in cursor.fetchall()]


def main():
    print("=" * 60)
    print("CHECKING ACTUAL COLUMN NAMES")
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

    tables = [
        '工装出入库单_主表',
        '工装出入库单_明细',
        '工装出入库单_操作日志',
        '工装出入库单_通知记录',
        '工装出入库单_位置',
        '工装运输异常记录',
    ]

    for table in tables:
        print(f"\n[{table}]")
        cols = get_columns(cursor, table)
        for c in cols:
            # Print each column on separate line for clarity
            print(f"  - {repr(c)}")

    conn.close()


if __name__ == "__main__":
    main()
