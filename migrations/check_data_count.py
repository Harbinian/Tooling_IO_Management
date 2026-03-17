# -*- coding: utf-8 -*-
"""Check data count in all tables"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
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

    print("Data count in tables:")
    print("-" * 40)
    total = 0
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{t}]")
            count = cursor.fetchone()[0]
            print(f"  {t}: {count} rows")
            total += count
        except:
            print(f"  {t}: ERROR")
    print("-" * 40)
    print(f"  TOTAL: {total} rows")

    # Check 工装身份卡_主表 (EXTERNAL - DO NOT TOUCH!)
    print("\n[EXTERNAL TABLE - DO NOT TOUCH]")
    cursor.execute("SELECT COUNT(*) FROM [工装身份卡_主表]")
    external_count = cursor.fetchone()[0]
    print(f"  工装身份卡_主表: {external_count} rows")

    conn.close()


if __name__ == "__main__":
    main()
