# -*- coding: utf-8 -*-
"""
迁移前验证脚本 V2 - 检查列名映射是否正确
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
    output_file = os.path.join(os.path.dirname(__file__), 'validation_v2.txt')

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
        f.write("MIGRATION PREREQUISITES VALIDATION V2\n")
        f.write("=" * 60 + "\n\n")

        # Check source tables
        source_tables = [
            '工装出入库单_主表',
            '工装出入库单_明细',
            '工装出入库单_操作日志',
            '工装出入库单_通知记录',
            '工装出入库单_位置',
            '工装运输异常记录',
        ]

        target_tables = [
            'tool_io_order',
            'tool_io_order_item',
            'tool_io_operation_log',
            'tool_io_notification',
            'tool_io_location',
            'tool_io_transport_issue',
        ]

        # Check source tables exist
        f.write("[1] Source Tables Check:\n")
        for t in source_tables:
            cols = get_columns(cursor, t)
            f.write(f"  {t}: {len(cols)} columns\n")
        f.write("\n")

        # Check target tables don't exist
        f.write("[2] Target Tables Check (should NOT exist):\n")
        for t in target_tables:
            cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = '{t}'")
            exists = cursor.fetchone()[0] > 0
            f.write(f"  {t}: {'EXISTS (PROBLEM!)' if exists else 'Not exists (OK)'}\n")
        f.write("\n")

        # Check mapping table
        cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name = 'table_english_mappings'")
        mappings_exists = cursor.fetchone()[0] > 0
        f.write(f"[3] Mappings Table: {'EXISTS' if mappings_exists else 'Not exists (OK)'}\n\n")

        # Check main table columns match expected
        f.write("[4] Main Table Column Validation:\n")
        cols = get_columns(cursor, '工装出入库单_主表')
        f.write(f"  Actual columns in source: {len(cols)}\n")

        # The new migration uses explicit SELECT with these columns:
        expected_select = [
            'id', '出入库单号', '单据类型', '单据状态', '发起人ID', '发起人姓名',
            '发起人角色', '部门', '项目代号', '用途', '计划使用时间', '计划归还时间',
            '目标位置ID', '目标位置文本', '保管员ID', '保管员姓名', '运输类型',
            '运输AssigneeID', '运输AssigneeName', '保管员需求文本', '运输通知文本',
            '微信复制文本', '保管员确认时间', '运输通知时间', '最终确认时间',
            '工装数量', '已确认数量', '最终确认人', '驳回原因', '取消原因',
            '备注', 'org_id', '创建时间', '修改时间', '创建人', '修改人', 'IS_DELETED'
        ]

        missing = set(expected_select) - set(cols)
        if missing:
            f.write(f"  [WARN] Missing columns in source: {missing}\n")
        else:
            f.write(f"  [OK] All expected columns exist in source\n")

        extra = set(cols) - set(expected_select)
        if extra:
            f.write(f"  [INFO] Extra columns in source (will be ignored): {extra}\n")

        # Summary
        f.write("\n" + "=" * 60 + "\n")
        f.write("VALIDATION SUMMARY:\n")
        f.write("=" * 60 + "\n")

        cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = 'tool_io_order'")
        target_exists = cursor.fetchone()[0] > 0

        if target_exists:
            f.write("[FAIL] Target tables already exist - migration may have been run\n")
        elif missing:
            f.write("[FAIL] Missing source columns - migration script needs fix\n")
        else:
            f.write("[PASS] Ready for migration\n")
            f.write("\nNext steps:\n")
            f.write("1. Backup database\n")
            f.write("2. Run: migrations/001_rename_tables_to_english.sql\n")
            f.write("3. Verify data in new tables\n")
            f.write("4. Drop old tables (after verification)\n")

    conn.close()
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
