# -*- coding: utf-8 -*-
"""
迁移前验证脚本 - 检查源中文表是否存在，列名是否匹配
仅用于测试环境验证！
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
import pyodbc


def check_source_tables_exist(cursor):
    """检查源中文表是否存在"""
    tables_to_check = [
        '工装出入库单_主表',
        '工装出入库单_明细',
        '工装出入库单_操作日志',
        '工装出入库单_通知记录',
        '工装出入库单_位置',
        '工装运输异常记录',
    ]

    existing_tables = []
    missing_tables = []

    for table in tables_to_check:
        cursor.execute(f"""
            SELECT COUNT(*) FROM sys.tables
            WHERE name = '{table}'
        """)
        if cursor.fetchone()[0] > 0:
            existing_tables.append(table)
            print(f"  [OK] 表存在: {table}")
        else:
            missing_tables.append(table)
            print(f"  [MISSING] 表不存在: {table}")

    return existing_tables, missing_tables


def check_target_tables_not_exist(cursor):
    """检查目标英文表是否已存在（迁移前应该不存在）"""
    tables_to_check = [
        'tool_io_order',
        'tool_io_order_item',
        'tool_io_operation_log',
        'tool_io_notification',
        'tool_io_location',
        'tool_io_transport_issue',
    ]

    existing = []
    not_exist = []

    for table in tables_to_check:
        cursor.execute(f"""
            SELECT COUNT(*) FROM sys.tables
            WHERE name = '{table}'
        """)
        if cursor.fetchone()[0] > 0:
            existing.append(table)
            print(f"  [EXISTS] 目标表已存在: {table} (迁移可能已执行)")
        else:
            not_exist.append(table)
            print(f"  [OK] 目标表不存在: {table}")

    return existing, not_exist


def check_column_names(cursor, table_name):
    """检查表的列名"""
    cursor.execute(f"""
        SELECT name FROM sys.columns
        WHERE object_id = OBJECT_ID('{table_name}')
        ORDER BY column_id
    """)
    columns = [row[0] for row in cursor.fetchall()]
    return columns


def validate_main_table_columns(cursor):
    """验证主表列名"""
    print("\n[主表列名检查]")
    expected_chinese = [
        'id', '出入库单号', '单据类型', '单据状态', '发起人ID', '发起人姓名',
        '发起人角色', '部门', '项目代号', '用途', '计划使用时间', '计划归还时间',
        '目标位置ID', '目标位置文本', '保管员ID', '保管员姓名', '运输类型',
        '运输AssigneeID', '运输AssigneeName', '工装数量', '已确认数量',
        '最终确认人', '最终确认时间', '取消原因', '驳回原因', '备注',
        '创建时间', '修改时间', '创建人', '修改人', 'IS_DELETED', 'org_id'
    ]

    columns = check_column_names(cursor, '工装出入库单_主表')
    print(f"  实际列名: {columns}")

    missing = set(expected_chinese) - set(columns)
    extra = set(columns) - set(expected_chinese)

    if missing:
        print(f"  [WARN] 缺失列: {missing}")
    if extra:
        print(f"  [WARN] 额外列: {extra}")
    if not missing and not extra:
        print(f"  [OK] 列名全部匹配")

    return columns


def validate_mappings_table(cursor):
    """检查映射表是否已存在"""
    cursor.execute("""
        SELECT COUNT(*) FROM sys.tables
        WHERE name = 'table_english_mappings'
    """)
    exists = cursor.fetchone()[0] > 0

    if exists:
        print("\n[映射表检查]")
        print("  [EXISTS] table_english_mappings 已存在")
        cursor.execute("SELECT COUNT(*) FROM table_english_mappings")
        count = cursor.fetchone()[0]
        print(f"  映射记录数: {count}")
    else:
        print("\n[映射表检查]")
        print("  [OK] table_english_mappings 不存在（迁移前应该不存在）")

    return exists


def main():
    print("=" * 60)
    print("迁移前验证 - 测试环境检查")
    print("=" * 60)

    try:
        # Build connection string
        conn_str = (
            f"DRIVER={settings.db.driver};"
            f"SERVER={settings.db.server};"
            f"DATABASE={settings.db.database};"
            f"UID={settings.db.username};"
            f"PWD={settings.db.password};"
            f"Connection Timeout=30;"
        )

        print(f"\n连接到: {settings.db.server}/{settings.db.database}")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("[OK] 数据库连接成功\n")

        # Run validations
        print("[源中文表检查]")
        existing, missing = check_source_tables_exist(cursor)
        print(f"\n  存在: {len(existing)}, 缺失: {len(missing)}")

        print("\n[目标英文表检查]")
        target_exists, target_missing = check_target_tables_not_exist(cursor)

        # Validate main table columns
        columns = validate_main_table_columns(cursor)

        # Check mapping table
        mappings_exists = validate_mappings_table(cursor)

        # Summary
        print("\n" + "=" * 60)
        print("验证结果汇总")
        print("=" * 60)

        if missing:
            print("[WARN] 部分源表缺失，迁移脚本可能需要调整")
            for t in missing:
                print(f"    - {t}")
        elif target_exists:
            print("[WARN] 目标表已存在，迁移可能已执行")
        elif mappings_exists:
            print("[WARN] 映射表已存在，迁移可能已执行")
        else:
            print("[OK] 所有检查通过，可以执行迁移")
            print("    - 源表全部存在")
            print("    - 目标表不存在")
            print("    - 映射表不存在")
            print("\n[建议] 在测试环境执行迁移脚本:")
            print("    migrations/001_rename_tables_to_english.sql")

        conn.close()

    except pyodbc.Error as e:
        print(f"[ERROR] 数据库连接失败: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] 验证失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
