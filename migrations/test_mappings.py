# -*- coding: utf-8 -*-
"""
Test the exact mappings table creation statement
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def main():
    print("Testing mappings table creation...")

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

    # The exact statement from migration script
    sql = """
IF OBJECT_ID(N'table_english_mappings', N'U') IS NULL
BEGIN
    CREATE TABLE table_english_mappings (
        id INT IDENTITY(1,1) PRIMARY KEY,
        original_table NVARCHAR(100) NOT NULL,
        english_table NVARCHAR(100) NOT NULL,
        original_column NVARCHAR(100) NOT NULL,
        english_column NVARCHAR(100) NOT NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT UX_mapping UNIQUE(original_table, original_column)
    )
    PRINT 'Mappings table created'
END
ELSE
BEGIN
    PRINT 'Mappings table already exists'
END
"""

    print("Executing IF...CREATE TABLE statement...")
    try:
        cursor.execute(sql)
        print("[OK] Statement executed")
        conn.commit()
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()

    # Check if table was created
    cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'table_english_mappings'")
    exists = cursor.fetchone()[0] > 0
    print(f"table_english_mappings exists: {exists}")

    conn.close()


if __name__ == "__main__":
    main()
