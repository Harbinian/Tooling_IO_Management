# -*- coding: utf-8 -*-
"""
Check if 运输人ID/姓名 and 运输AssigneeID/姓名 have same or different data
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
    output_file = os.path.join(os.path.dirname(__file__), 'transport_column_comparison.txt')

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

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Comparing transport operator columns:\n")
        f.write("=" * 60 + "\n\n")

        # Get sample data comparing the columns
        cursor.execute("""
            SELECT TOP 20
                [出入库单号],
                [运输人ID],
                [运输人姓名],
                [运输AssigneeID],
                [运输AssigneeName]
            FROM [工装出入库单_主表]
            WHERE [运输人ID] IS NOT NULL OR [运输AssigneeID] IS NOT NULL
        """)

        f.write("order_no | 运输人ID | 运输人姓名 | 运输AssigneeID | 运输AssigneeName\n")
        f.write("-" * 80 + "\n")

        for row in cursor.fetchall():
            order_no = row[0] if row[0] else 'NULL'
            col1 = row[1] if row[1] else 'NULL'
            col2 = row[2] if row[2] else 'NULL'
            col3 = row[3] if row[3] else 'NULL'
            col4 = row[4] if row[4] else 'NULL'
            f.write(f"{order_no} | {col1} | {col2} | {col3} | {col4}\n")

        # Count non-null values
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN [运输人ID] IS NOT NULL THEN 1 ELSE 0 END) as has_运输人ID,
                SUM(CASE WHEN [运输AssigneeID] IS NOT NULL THEN 1 ELSE 0 END) as has_运输AssigneeID,
                SUM(CASE WHEN [运输人ID] = [运输AssigneeID] THEN 1 ELSE 0 END) as same_values
            FROM [工装出入库单_主表]
            WHERE [运输人ID] IS NOT NULL OR [运输AssigneeID] IS NOT NULL
        """)

        row = cursor.fetchone()
        f.write(f"\nStatistics:\n")
        f.write(f"  Total rows with any transport ID: {row[0]}\n")
        f.write(f"  Rows with 运输人ID: {row[1]}\n")
        f.write(f"  Rows with 运输AssigneeID: {row[2]}\n")
        f.write(f"  Rows where both are equal: {row[3]}\n")

    conn.close()
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
