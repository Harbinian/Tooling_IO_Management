# -*- coding: utf-8 -*-
"""
Schema management for Tool IO tables.
"""

import logging
from typing import List

from backend.database.core.database_manager import DatabaseManager, ORDER_NO_SEQUENCE_TABLE

logger = logging.getLogger(__name__)

# Schema alignment indexes
SCHEMA_ALIGNMENT_INDEXES = (
    ("工装出入库单_主表", "IX_工装出入库单_主表_单据类型", "单据类型"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_单据状态", "单据状态"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_发起人ID", "发起人ID"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_保管员ID", "保管员ID"),
    ("工装出入库单_主表", "IX_工装出入库单_主表_创建时间", "创建时间"),
    ("工装出入库单_明细", "IX_工装出入库单_明细_出入库单号", "出入库单号"),
    ("工装出入库单_明细", "IX_工装出入库单_明细_工装编码", "工装编码"),
    ("工装出入库单_明细", "IX_工装出入库单_明细_明细状态", "明细状态"),
    ("工装出入库单_操作日志", "IX_工装出入库单_操作日志_出入库单号", "出入库单号"),
    ("工装出入库单_操作日志", "IX_工装出入库单_操作日志_操作时间", "操作时间"),
    ("工装出入库单_通知记录", "IX_工装出入库单_通知记录_出入库单号", "出入库单号"),
    ("工装出入库单_通知记录", "IX_工装出入库单_通知记录_发送状态", "发送状态"),
    ("工装出入库单_通知记录", "IX_工装出入库单_通知记录_通知渠道", "通知渠道"),
)


def _build_schema_alignment_sql() -> List[str]:
    """Build SQL statements for schema alignment."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        build_add_column_sql("工装出入库单_主表", "工装数量", "INT NULL"),
        build_add_column_sql("工装出入库单_主表", "已确认数量", "INT NULL"),
        build_add_column_sql("工装出入库单_主表", "最终确认人", "VARCHAR(64) NULL"),
        build_add_column_sql("工装出入库单_主表", "取消原因", "VARCHAR(500) NULL"),
        build_add_column_sql("工装出入库单_明细", "确认时间", "DATETIME NULL"),
        build_add_column_sql("工装出入库单_明细", "出入库完成时间", "DATETIME NULL"),
    ]

    for table_name, index_name, column_list in SCHEMA_ALIGNMENT_INDEXES:
        sql_statements.append(build_create_index_sql(table_name, index_name, column_list))

    return sql_statements


def ensure_tool_io_tables() -> bool:
    """
    Create the Tool IO tables required by the runtime if they do not exist.

    Returns:
        True if successful, False otherwise
    """
    db = DatabaseManager()
    create_statements = [
        """
        IF OBJECT_ID(N'工装出入库单_主表', N'U') IS NULL
        CREATE TABLE [工装出入库单_主表] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [出入库单号] VARCHAR(64) NOT NULL UNIQUE,
            [单据类型] VARCHAR(16) NOT NULL,
            [单据状态] VARCHAR(32) NOT NULL DEFAULT 'draft',
            [发起人ID] VARCHAR(64) NOT NULL,
            [发起人姓名] VARCHAR(64) NOT NULL,
            [发起人角色] VARCHAR(32) NOT NULL,
            [部门] VARCHAR(64) NULL,
            [项目代号] VARCHAR(64) NULL,
            [用途] VARCHAR(255) NULL,
            [计划使用时间] DATETIME NULL,
            [计划归还时间] DATETIME NULL,
            [目标位置ID] BIGINT NULL,
            [目标位置文本] VARCHAR(255) NULL,
            [保管员ID] VARCHAR(64) NULL,
            [保管员姓名] VARCHAR(64) NULL,
            [运输类型] VARCHAR(32) NULL,
            [运输AssigneeID] VARCHAR(64) NULL,
            [运输AssigneeName] VARCHAR(64) NULL,
            [保管员确认时间] DATETIME NULL,
            [已确认数量] INT NOT NULL DEFAULT 0,
            [最终确认人] VARCHAR(64) NULL,
            [最终确认时间] DATETIME NULL,
            [取消原因] VARCHAR(500) NULL,
            [驳回原因] VARCHAR(500) NULL,
            [备注] VARCHAR(500) NULL,
            [org_id] VARCHAR(64) NULL,
            [创建时间] DATETIME NOT NULL DEFAULT GETDATE(),
            [修改时间] DATETIME NOT NULL DEFAULT GETDATE(),
            [创建人] VARCHAR(64) NULL,
            [修改人] VARCHAR(64) NULL,
            [IS_DELETED] TINYINT NOT NULL DEFAULT 0
        )
        """,
        """
        IF OBJECT_ID(N'工装出入库单_明细', N'U') IS NULL
        CREATE TABLE [工装出入库单_明细] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [出入库单号] VARCHAR(64) NOT NULL,
            [工装ID] BIGINT NULL,
            [序列号] VARCHAR(64) NOT NULL,
            [工装名称] VARCHAR(255) NULL,
            [工装图号] VARCHAR(255) NULL,
            [机型] VARCHAR(255) NULL,
            [申请数量] DECIMAL(18,2) NOT NULL DEFAULT 1,
            [确认数量] DECIMAL(18,2) NOT NULL DEFAULT 0,
            [明细状态] VARCHAR(32) NOT NULL DEFAULT 'pending_check',
            [工装快照状态] VARCHAR(255) NULL,
            [工装快照位置文本] VARCHAR(255) NULL,
            [工装快照位置ID] BIGINT NULL,
            [确认人] VARCHAR(255) NULL,
            [确认人ID] BIGINT NULL,
            [确认人姓名] VARCHAR(64) NULL,
            [确认时间] VARCHAR(500) NULL,
            [驳回原因] VARCHAR(500) NULL,
            [出入库完成时间] DATETIME NULL,
            [排序号] INT NOT NULL DEFAULT 1,
            [创建时间] DATETIME NOT NULL DEFAULT GETDATE(),
            [修改时间] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'工装出入库单_操作日志', N'U') IS NULL
        CREATE TABLE [工装出入库单_操作日志] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [出入库单号] VARCHAR(64) NOT NULL,
            [明细ID] BIGINT NULL,
            [操作类型] VARCHAR(64) NOT NULL,
            [操作人ID] VARCHAR(64) NULL,
            [操作人姓名] VARCHAR(64) NULL,
            [操作人角色] VARCHAR(64) NULL,
            [变更前状态] VARCHAR(64) NULL,
            [变更后状态] VARCHAR(64) NULL,
            [操作内容] TEXT NULL,
            [操作时间] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'工装出入库单_通知记录', N'U') IS NULL
        CREATE TABLE [工装出入库单_通知记录] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [出入库单号] VARCHAR(64) NOT NULL,
            [通知类型] VARCHAR(64) NOT NULL,
            [通知渠道] VARCHAR(64) NULL,
            [接收人] VARCHAR(255) NULL,
            [通知标题] VARCHAR(255) NULL,
            [通知内容] TEXT NULL,
            [复制文本] TEXT NULL,
            [发送状态] VARCHAR(32) NOT NULL DEFAULT 'pending',
            [发送时间] DATETIME NULL,
            [发送结果] TEXT NULL,
            [重试次数] INT NOT NULL DEFAULT 0,
            [创建时间] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'工装出入库单_位置', N'U') IS NULL
        CREATE TABLE [工装出入库单_位置] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [位置编码] VARCHAR(64) NOT NULL,
            [位置名称] VARCHAR(255) NOT NULL,
            [位置描述] VARCHAR(255) NULL,
            [库区] VARCHAR(64) NULL,
            [库位] VARCHAR(64) NULL,
            [货架] VARCHAR(255) NULL,
            [备注] VARCHAR(500) NULL
        )
        """,
        f"""
        IF OBJECT_ID(N'{ORDER_NO_SEQUENCE_TABLE}', N'U') IS NULL
        CREATE TABLE {ORDER_NO_SEQUENCE_TABLE} (
            [sequence_key] VARCHAR(32) NOT NULL PRIMARY KEY,
            [current_value] INT NOT NULL,
            [updated_at] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_工装出入库单_主表_出入库单号' AND object_id = OBJECT_ID(N'工装出入库单_主表'))
        CREATE INDEX [IX_工装出入库单_主表_出入库单号] ON [工装出入库单_主表]([出入库单号])
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_工装出入库单_主表_单据状态' AND object_id = OBJECT_ID(N'工装出入库单_主表'))
        CREATE INDEX [IX_工装出入库单_主表_单据状态] ON [工装出入库单_主表]([单据状态])
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_工装出入库单_主表_创建时间' AND object_id = OBJECT_ID(N'工装出入库单_主表'))
        CREATE INDEX [IX_工装出入库单_主表_创建时间] ON [工装出入库单_主表]([创建时间])
        """,
    ]

    try:
        for sql in create_statements:
            db.execute_query(sql, fetch=False)
        logger.info('Tool IO tables created successfully')
        return True
    except Exception as e:
        logger.error('Failed to create Tool IO tables: %s', e)
        return False


def ensure_schema_alignment() -> bool:
    """
    Ensure schema alignment by adding missing columns and indexes.

    Returns:
        True if successful, False otherwise
    """
    db = DatabaseManager()
    sql_statements = _build_schema_alignment_sql()

    try:
        for sql in sql_statements:
            db.execute_query(sql, fetch=False)
        logger.info('Schema alignment completed')
        return True
    except Exception as e:
        logger.error('Schema alignment failed: %s', e)
        return False
