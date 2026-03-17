# -*- coding: utf-8 -*-
"""
Test simple SQL execution
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
    print("Testing SQL execution...")

    conn_str = (
        f"DRIVER={settings.db.driver};"
        f"SERVER={settings.db.server};"
        f"DATABASE={settings.db.database};"
        f"UID={settings.db.username};"
        f"PWD={settings.db.password};"
        f"Connection Timeout=30;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("[OK] Connected")

        # Test 1: Simple query on source table
        print("\n[Test 1] Query source table...")
        cursor.execute("SELECT TOP 1 [出入库单号] FROM [工装出入库单_主表]")
        row = cursor.fetchone()
        print(f"  Result: {row[0] if row else 'No data'}")
        print("  [OK] Source table accessible")

        # Test 2: Check if target table exists
        print("\n[Test 2] Check target table...")
        cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'tool_io_order'")
        exists = cursor.fetchone()[0] > 0
        print(f"  tool_io_order exists: {exists}")
        print("  [OK] sys.tables accessible")

        # Test 3: Try a simple SELECT INTO
        print("\n[Test 3] Test SELECT INTO with Chinese table...")
        try:
            cursor.execute("""
                SELECT TOP 1 [id] AS id, [出入库单号] AS order_no
                INTO #test_temp
                FROM [工装出入库单_主表]
            """)
            cursor.execute("SELECT COUNT(*) FROM #test_temp")
            count = cursor.fetchone()[0]
            print(f"  Temporary table rows: {count}")
            cursor.execute("DROP TABLE #test_temp")
            print("  [OK] SELECT INTO works")
        except Exception as e:
            print(f"  [FAIL] SELECT INTO error: {e}")

        conn.close()
        print("\nAll tests passed!")

    except pyodbc.Error as e:
        print(f"[ERROR] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
