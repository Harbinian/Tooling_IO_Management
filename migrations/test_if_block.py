# -*- coding: utf-8 -*-
"""
Test IF statement with Chinese table name
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
    print("Testing IF statement with Chinese table name...")

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

    # Test 1: Simple IF EXISTS
    print("\n[Test 1] IF OBJECT_ID check...")
    sql1 = """
    IF OBJECT_ID(N'工装出入库单_主表', N'U') IS NOT NULL
        SELECT 1 AS result
    ELSE
        SELECT 0 AS result
    """
    cursor.execute(sql1)
    row = cursor.fetchone()
    print(f"  Result: {row[0]}")

    # Test 2: IF NOT EXISTS with CREATE TABLE
    print("\n[Test 2] IF NOT EXISTS with CREATE TABLE...")
    sql2 = """
    IF OBJECT_ID(N'test_chinese_table', N'U') IS NULL
    BEGIN
        CREATE TABLE test_chinese_table (
            id INT,
            名称 NVARCHAR(100)
        )
        SELECT 'Created' AS result
    END
    ELSE
        SELECT 'Exists' AS result
    """
    try:
        cursor.execute(sql2)
        row = cursor.fetchone()
        print(f"  Result: {row[0]}")
        print("  [OK] IF block works")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS test_chinese_table")

    conn.close()
    print("\nDone")


if __name__ == "__main__":
    main()
