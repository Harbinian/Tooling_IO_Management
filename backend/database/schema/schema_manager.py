# -*- coding: utf-8 -*-
"""
Schema management for Tool IO tables.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

# Schema alignment indexes - using English table/column names
SCHEMA_ALIGNMENT_INDEXES = (
    ("tool_io_order", "IX_tool_io_order_order_type", "order_type"),
    ("tool_io_order", "IX_tool_io_order_order_status", "order_status"),
    ("tool_io_order", "IX_tool_io_order_initiator_id", "initiator_id"),
    ("tool_io_order", "IX_tool_io_order_keeper_id", "keeper_id"),
    ("tool_io_order", "IX_tool_io_order_created_at", "created_at"),
    ("tool_io_order_item", "IX_tool_io_order_item_order_no", "order_no"),
    ("tool_io_order_item", "IX_tool_io_order_item_serial_no", "serial_no"),
    ("tool_io_order_item", "IX_tool_io_order_item_item_status", "item_status"),
    ("tool_io_operation_log", "IX_tool_io_operation_log_order_no", "order_no"),
    ("tool_io_operation_log", "IX_tool_io_operation_log_operation_time", "operation_time"),
    ("tool_io_notification", "IX_tool_io_notification_order_no", "order_no"),
    ("tool_io_notification", "IX_tool_io_notification_send_status", "send_status"),
    ("tool_io_notification", "IX_tool_io_notification_notify_channel", "notify_channel"),
    ("tool_io_transport_issue", "IX_tool_io_transport_issue_order_no", "order_no"),
    ("tool_io_transport_issue", "IX_tool_io_transport_issue_status", "status"),
    ("tool_io_transport_issue", "IX_tool_io_transport_issue_report_time", "report_time"),
    ("tool_io_inspection_plan", "IX_tool_io_inspection_plan_year_month", "plan_year, plan_month"),
    ("tool_io_inspection_plan", "IX_tool_io_inspection_plan_status", "status"),
    ("tool_io_inspection_task", "IX_tool_io_inspection_task_plan_no", "plan_no"),
    ("tool_io_inspection_task", "IX_tool_io_inspection_task_serial_no", "serial_no"),
    ("tool_io_inspection_task", "IX_tool_io_inspection_task_status", "task_status"),
    ("tool_io_inspection_task", "IX_tool_io_inspection_task_deadline", "deadline"),
    ("tool_io_inspection_report", "IX_tool_io_inspection_report_task_no", "task_no"),
    ("tool_io_tool_inspection_status", "IX_tool_io_tool_inspection_status_next_date", "next_inspection_date"),
    ("tool_io_tool_inspection_status", "IX_tool_io_tool_inspection_status_status", "inspection_status"),
)


def _execute_statements_in_transaction(sql_statements: List[str], success_message: str) -> bool:
    """Execute schema DDL statements atomically."""
    from backend.database.core.database_manager import DatabaseManager

    db = DatabaseManager()
    conn = None
    cursor = None

    try:
        conn = db.connect()
        cursor = conn.cursor()
        for sql in sql_statements:
            cursor.execute(sql)
        conn.commit()
        logger.info(success_message)
        return True
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        logger.error('%s failed: %s', success_message, exc)
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            db.close(conn)


def _build_schema_alignment_sql() -> List[str]:
    """Build SQL statements for schema alignment."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        build_add_column_sql("tool_io_order", "org_id", "VARCHAR(64) NULL"),
        build_add_column_sql("tool_io_order", "tool_quantity", "INT NULL"),
        build_add_column_sql("tool_io_order", "confirmed_count", "INT NULL"),
        build_add_column_sql("tool_io_order", "final_confirm_by", "VARCHAR(64) NULL"),
        build_add_column_sql("tool_io_order", "cancel_reason", "VARCHAR(500) NULL"),
        build_add_column_sql("tool_io_order_item", "confirm_time", "DATETIME NULL"),
        build_add_column_sql("tool_io_order_item", "io_complete_time", "DATETIME NULL"),
    ]

    for table_name, index_name, column_list in SCHEMA_ALIGNMENT_INDEXES:
        sql_statements.append(build_create_index_sql(table_name, index_name, column_list))

    return sql_statements


def ensure_feedback_table() -> bool:
    """Create or align feedback persistence table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_feedback', N'U') IS NULL
        CREATE TABLE [tool_io_feedback] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [category] VARCHAR(32) NOT NULL,
            [subject] NVARCHAR(200) NOT NULL,
            [content] NVARCHAR(2000) NOT NULL,
            [login_name] VARCHAR(100) NOT NULL,
            [user_name] NVARCHAR(100) NOT NULL,
            [status] VARCHAR(32) NOT NULL DEFAULT 'pending',
            [created_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [updated_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME()
        )
        """,
        build_add_column_sql("tool_io_feedback", "category", "VARCHAR(32) NOT NULL DEFAULT 'other'"),
        build_add_column_sql("tool_io_feedback", "subject", "NVARCHAR(200) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_feedback", "content", "NVARCHAR(2000) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_feedback", "login_name", "VARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_feedback", "user_name", "NVARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_feedback", "status", "VARCHAR(32) NOT NULL DEFAULT 'pending'"),
        build_add_column_sql("tool_io_feedback", "created_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_feedback", "updated_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_create_index_sql("tool_io_feedback", "IX_tool_io_feedback_login_name", "login_name"),
        build_create_index_sql("tool_io_feedback", "IX_tool_io_feedback_created_at", "created_at"),
    ]
    return _execute_statements_in_transaction(sql_statements, "Feedback table ensured")


def ensure_feedback_reply_table() -> bool:
    """Create or align feedback reply table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_feedback_reply', N'U') IS NULL
        CREATE TABLE [tool_io_feedback_reply] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [feedback_id] BIGINT NOT NULL,
            [reply_content] NVARCHAR(1000) NOT NULL,
            [replier_login_name] VARCHAR(100) NOT NULL,
            [replier_user_name] NVARCHAR(100) NOT NULL,
            [created_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            CONSTRAINT FK_feedback_reply FOREIGN KEY (feedback_id) REFERENCES [tool_io_feedback](id) ON DELETE CASCADE
        )
        """,
        build_add_column_sql("tool_io_feedback_reply", "feedback_id", "BIGINT NOT NULL DEFAULT 0"),
        build_add_column_sql("tool_io_feedback_reply", "reply_content", "NVARCHAR(1000) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_feedback_reply", "replier_login_name", "VARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_feedback_reply", "replier_user_name", "NVARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_feedback_reply", "created_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        """
        IF OBJECT_ID(N'tool_io_feedback_reply', N'U') IS NOT NULL
           AND OBJECT_ID(N'FK_feedback_reply', N'F') IS NULL
        BEGIN
            ALTER TABLE [tool_io_feedback_reply]
            ADD CONSTRAINT FK_feedback_reply
            FOREIGN KEY (feedback_id)
            REFERENCES [tool_io_feedback](id)
            ON DELETE CASCADE
        END
        """,
        build_create_index_sql("tool_io_feedback_reply", "IX_tool_io_feedback_reply_feedback_id", "feedback_id"),
    ]
    return _execute_statements_in_transaction(sql_statements, "Feedback reply table ensured")


def ensure_tool_status_change_history_table() -> bool:
    """Create or align tool status change history table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_status_change_history', N'U') IS NULL
        CREATE TABLE [tool_status_change_history] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [serial_no] NVARCHAR(100) NOT NULL,
            [old_status] NVARCHAR(50) NOT NULL,
            [new_status] NVARCHAR(50) NOT NULL,
            [remark] NVARCHAR(500) NULL,
            [operator_id] NVARCHAR(64) NOT NULL,
            [operator_name] NVARCHAR(100) NOT NULL,
            [change_time] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [client_ip] NVARCHAR(64) NULL
        )
        """,
        build_add_column_sql("tool_status_change_history", "serial_no", "NVARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_status_change_history", "old_status", "NVARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_status_change_history", "new_status", "NVARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_status_change_history", "remark", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_status_change_history", "operator_id", "NVARCHAR(64) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_status_change_history", "operator_name", "NVARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_status_change_history", "change_time", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_status_change_history", "client_ip", "NVARCHAR(64) NULL"),
        build_create_index_sql(
            "tool_status_change_history",
            "IX_tool_status_change_history_serial_no_time",
            "serial_no, change_time",
        ),
    ]
    return _execute_statements_in_transaction(sql_statements, "Tool status change history table ensured")


def ensure_transport_issue_table() -> bool:
    """Create or align transport issue persistence table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_transport_issue', N'U') IS NULL
        CREATE TABLE [tool_io_transport_issue] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [order_no] VARCHAR(64) NOT NULL,
            [issue_type] VARCHAR(50) NOT NULL,
            [description] NVARCHAR(500) NULL,
            [image_urls] NVARCHAR(2000) NULL,
            [reporter_id] VARCHAR(64) NULL,
            [reporter_name] NVARCHAR(50) NULL,
            [report_time] DATETIME NOT NULL DEFAULT GETDATE(),
            [status] VARCHAR(20) NOT NULL DEFAULT 'pending',
            [handler_id] VARCHAR(64) NULL,
            [handler_name] NVARCHAR(50) NULL,
            [handle_time] DATETIME NULL,
            [handle_reply] NVARCHAR(500) NULL,
            [created_at] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        build_add_column_sql("tool_io_transport_issue", "order_no", "VARCHAR(64) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_transport_issue", "issue_type", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_transport_issue", "description", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_io_transport_issue", "image_urls", "NVARCHAR(2000) NULL"),
        build_add_column_sql("tool_io_transport_issue", "reporter_id", "VARCHAR(64) NULL"),
        build_add_column_sql("tool_io_transport_issue", "reporter_name", "NVARCHAR(50) NULL"),
        build_add_column_sql("tool_io_transport_issue", "report_time", "DATETIME NOT NULL DEFAULT GETDATE()"),
        build_add_column_sql("tool_io_transport_issue", "status", "VARCHAR(20) NOT NULL DEFAULT 'pending'"),
        build_add_column_sql("tool_io_transport_issue", "handler_id", "VARCHAR(64) NULL"),
        build_add_column_sql("tool_io_transport_issue", "handler_name", "NVARCHAR(50) NULL"),
        build_add_column_sql("tool_io_transport_issue", "handle_time", "DATETIME NULL"),
        build_add_column_sql("tool_io_transport_issue", "handle_reply", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_io_transport_issue", "created_at", "DATETIME NOT NULL DEFAULT GETDATE()"),
        build_create_index_sql("tool_io_transport_issue", "IX_tool_io_transport_issue_order_no", "order_no"),
        build_create_index_sql("tool_io_transport_issue", "IX_tool_io_transport_issue_status", "status"),
        build_create_index_sql("tool_io_transport_issue", "IX_tool_io_transport_issue_report_time", "report_time"),
    ]
    return _execute_statements_in_transaction(sql_statements, "Transport issue table ensured")


def ensure_system_config_table() -> bool:
    """Create or align system configuration table and seed default values."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'sys_system_config', N'U') IS NULL
        CREATE TABLE [sys_system_config] (
            [config_key] VARCHAR(128) PRIMARY KEY,
            [config_value] NVARCHAR(256) NULL,
            [description] NVARCHAR(512) NULL,
            [updated_by] VARCHAR(64) NULL,
            [updated_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME()
        )
        """,
        build_add_column_sql("sys_system_config", "config_value", "NVARCHAR(256) NULL"),
        build_add_column_sql("sys_system_config", "description", "NVARCHAR(512) NULL"),
        build_add_column_sql("sys_system_config", "updated_by", "VARCHAR(64) NULL"),
        build_add_column_sql("sys_system_config", "updated_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        """
        IF NOT EXISTS (SELECT 1 FROM [sys_system_config] WHERE [config_key] = 'mpl_enabled')
        INSERT INTO [sys_system_config] ([config_key], [config_value], [description], [updated_by], [updated_at])
        VALUES ('mpl_enabled', N'false', N'Enable MPL validation during keeper confirmation', 'system', SYSDATETIME())
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM [sys_system_config] WHERE [config_key] = 'mpl_strict_mode')
        INSERT INTO [sys_system_config] ([config_key], [config_value], [description], [updated_by], [updated_at])
        VALUES ('mpl_strict_mode', N'false', N'Block keeper confirmation when MPL is missing', 'system', SYSDATETIME())
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM [sys_system_config] WHERE [config_key] = 'feishu_notification_enabled')
        INSERT INTO [sys_system_config] ([config_key], [config_value], [description], [updated_by], [updated_at])
        VALUES ('feishu_notification_enabled', N'false', N'Enable Feishu notification delivery', 'system', SYSDATETIME())
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM [sys_system_config] WHERE [config_key] = 'feishu_webhook_supply_team')
        INSERT INTO [sys_system_config] ([config_key], [config_value], [description], [updated_by], [updated_at])
        VALUES ('feishu_webhook_supply_team', N'', N'Feishu webhook URL for supply team notification', 'system', SYSDATETIME())
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM [sys_system_config] WHERE [config_key] = 'feishu_webhook_transport')
        INSERT INTO [sys_system_config] ([config_key], [config_value], [description], [updated_by], [updated_at])
        VALUES ('feishu_webhook_transport', N'', N'Feishu webhook URL for transport notification', 'system', SYSDATETIME())
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM [sys_system_config] WHERE [config_key] = 'feishu_webhook_url')
        INSERT INTO [sys_system_config] ([config_key], [config_value], [description], [updated_by], [updated_at])
        VALUES ('feishu_webhook_url', N'', N'Feishu default webhook URL', 'system', SYSDATETIME())
        """,
        build_create_index_sql("sys_system_config", "IX_sys_system_config_updated_at", "updated_at"),
    ]
    return _execute_statements_in_transaction(sql_statements, "System config table ensured")


def ensure_mpl_table() -> bool:
    """Create or align MPL persistence table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_mpl', N'U') IS NULL
        CREATE TABLE [tool_io_mpl] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [mpl_no] VARCHAR(128) NOT NULL,
            [tool_drawing_no] VARCHAR(64) NOT NULL,
            [tool_revision] VARCHAR(32) NOT NULL,
            [component_no] VARCHAR(64) NOT NULL,
            [component_name] NVARCHAR(256) NOT NULL,
            [quantity] INT NOT NULL DEFAULT 1,
            [photo_data] NVARCHAR(MAX) NULL,
            [created_by] VARCHAR(64) NULL,
            [created_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [updated_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME()
        )
        """,
        build_add_column_sql("tool_io_mpl", "mpl_no", "VARCHAR(128) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_mpl", "tool_drawing_no", "VARCHAR(64) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_mpl", "tool_revision", "VARCHAR(32) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_mpl", "component_no", "VARCHAR(64) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_mpl", "component_name", "NVARCHAR(256) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_mpl", "quantity", "INT NOT NULL DEFAULT 1"),
        build_add_column_sql("tool_io_mpl", "photo_data", "NVARCHAR(MAX) NULL"),
        build_add_column_sql("tool_io_mpl", "created_by", "VARCHAR(64) NULL"),
        build_add_column_sql("tool_io_mpl", "created_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_mpl", "updated_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_create_index_sql("tool_io_mpl", "IX_tool_io_mpl_tool", "tool_drawing_no, tool_revision"),
        build_create_index_sql("tool_io_mpl", "IX_tool_io_mpl_mpl_no", "mpl_no"),
        """
        IF NOT EXISTS (
            SELECT 1
            FROM sys.indexes
            WHERE name = N'UX_tool_io_mpl_tool_component'
              AND object_id = OBJECT_ID(N'tool_io_mpl')
        )
        CREATE UNIQUE INDEX [UX_tool_io_mpl_tool_component]
        ON [tool_io_mpl]([tool_drawing_no], [tool_revision], [component_no])
        """,
    ]
    return _execute_statements_in_transaction(sql_statements, "MPL table ensured")


def ensure_inspection_plan_table() -> bool:
    """Create or align inspection plan table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_inspection_plan', N'U') IS NULL
        CREATE TABLE [tool_io_inspection_plan] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [plan_no] VARCHAR(50) NOT NULL UNIQUE,
            [plan_name] NVARCHAR(200) NOT NULL,
            [plan_year] INT NOT NULL,
            [plan_month] INT NOT NULL,
            [inspection_type] VARCHAR(50) NOT NULL,
            [status] VARCHAR(20) NOT NULL DEFAULT 'draft',
            [creator_id] VARCHAR(50) NOT NULL,
            [creator_name] NVARCHAR(100) NOT NULL,
            [publish_time] DATETIME NULL,
            [remark] NVARCHAR(500) NULL,
            [created_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [updated_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [created_by] VARCHAR(100) NULL,
            [updated_by] VARCHAR(100) NULL
        )
        """,
        build_add_column_sql("tool_io_inspection_plan", "plan_no", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_plan", "plan_name", "NVARCHAR(200) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_plan", "plan_year", "INT NOT NULL DEFAULT 0"),
        build_add_column_sql("tool_io_inspection_plan", "plan_month", "INT NOT NULL DEFAULT 0"),
        build_add_column_sql("tool_io_inspection_plan", "inspection_type", "VARCHAR(50) NOT NULL DEFAULT 'regular'"),
        build_add_column_sql("tool_io_inspection_plan", "status", "VARCHAR(20) NOT NULL DEFAULT 'draft'"),
        build_add_column_sql("tool_io_inspection_plan", "creator_id", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_plan", "creator_name", "NVARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_plan", "publish_time", "DATETIME NULL"),
        build_add_column_sql("tool_io_inspection_plan", "remark", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_io_inspection_plan", "created_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_inspection_plan", "updated_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_inspection_plan", "created_by", "VARCHAR(100) NULL"),
        build_add_column_sql("tool_io_inspection_plan", "updated_by", "VARCHAR(100) NULL"),
        build_create_index_sql("tool_io_inspection_plan", "IX_tool_io_inspection_plan_year_month", "plan_year, plan_month"),
        build_create_index_sql("tool_io_inspection_plan", "IX_tool_io_inspection_plan_status", "status"),
    ]
    return _execute_statements_in_transaction(sql_statements, "Inspection plan table ensured")


def ensure_inspection_task_table() -> bool:
    """Create or align inspection task table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_inspection_task', N'U') IS NULL
        CREATE TABLE [tool_io_inspection_task] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [task_no] VARCHAR(50) NOT NULL UNIQUE,
            [plan_no] VARCHAR(50) NOT NULL,
            [serial_no] VARCHAR(100) NOT NULL,
            [tool_name] NVARCHAR(200) NULL,
            [drawing_no] VARCHAR(100) NULL,
            [spec_model] VARCHAR(100) NULL,
            [task_status] VARCHAR(30) NOT NULL DEFAULT 'pending',
            [assigned_to_id] VARCHAR(50) NULL,
            [assigned_to_name] NVARCHAR(100) NULL,
            [receive_time] DATETIME NULL,
            [outbound_order_no] VARCHAR(50) NULL,
            [inbound_order_no] VARCHAR(50) NULL,
            [inspection_result] VARCHAR(20) NULL,
            [reject_reason] NVARCHAR(500) NULL,
            [report_no] VARCHAR(50) NULL,
            [next_inspection_date] DATE NULL,
            [deadline] DATETIME NULL,
            [actual_complete_time] DATETIME NULL,
            [remark] NVARCHAR(500) NULL,
            [created_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [updated_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [created_by] VARCHAR(100) NULL,
            [updated_by] VARCHAR(100) NULL
        )
        """,
        build_add_column_sql("tool_io_inspection_task", "task_no", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_task", "plan_no", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_task", "serial_no", "VARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_task", "tool_name", "NVARCHAR(200) NULL"),
        build_add_column_sql("tool_io_inspection_task", "drawing_no", "VARCHAR(100) NULL"),
        build_add_column_sql("tool_io_inspection_task", "spec_model", "VARCHAR(100) NULL"),
        build_add_column_sql("tool_io_inspection_task", "task_status", "VARCHAR(30) NOT NULL DEFAULT 'pending'"),
        build_add_column_sql("tool_io_inspection_task", "assigned_to_id", "VARCHAR(50) NULL"),
        build_add_column_sql("tool_io_inspection_task", "assigned_to_name", "NVARCHAR(100) NULL"),
        build_add_column_sql("tool_io_inspection_task", "receive_time", "DATETIME NULL"),
        build_add_column_sql("tool_io_inspection_task", "outbound_order_no", "VARCHAR(50) NULL"),
        build_add_column_sql("tool_io_inspection_task", "inbound_order_no", "VARCHAR(50) NULL"),
        build_add_column_sql("tool_io_inspection_task", "inspection_result", "VARCHAR(20) NULL"),
        build_add_column_sql("tool_io_inspection_task", "reject_reason", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_io_inspection_task", "report_no", "VARCHAR(50) NULL"),
        build_add_column_sql("tool_io_inspection_task", "next_inspection_date", "DATE NULL"),
        build_add_column_sql("tool_io_inspection_task", "deadline", "DATETIME NULL"),
        build_add_column_sql("tool_io_inspection_task", "actual_complete_time", "DATETIME NULL"),
        build_add_column_sql("tool_io_inspection_task", "remark", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_io_inspection_task", "created_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_inspection_task", "updated_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_inspection_task", "created_by", "VARCHAR(100) NULL"),
        build_add_column_sql("tool_io_inspection_task", "updated_by", "VARCHAR(100) NULL"),
        build_create_index_sql("tool_io_inspection_task", "IX_tool_io_inspection_task_plan_no", "plan_no"),
        build_create_index_sql("tool_io_inspection_task", "IX_tool_io_inspection_task_serial_no", "serial_no"),
        build_create_index_sql("tool_io_inspection_task", "IX_tool_io_inspection_task_status", "task_status"),
        build_create_index_sql("tool_io_inspection_task", "IX_tool_io_inspection_task_deadline", "deadline"),
    ]
    return _execute_statements_in_transaction(sql_statements, "Inspection task table ensured")


def ensure_inspection_report_table() -> bool:
    """Create or align inspection report table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_inspection_report', N'U') IS NULL
        CREATE TABLE [tool_io_inspection_report] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [report_no] VARCHAR(50) NOT NULL UNIQUE,
            [task_no] VARCHAR(50) NOT NULL,
            [inspector_id] VARCHAR(50) NOT NULL,
            [inspector_name] NVARCHAR(100) NOT NULL,
            [inspection_date] DATE NOT NULL,
            [inspection_result] VARCHAR(20) NOT NULL,
            [measurement_data] NVARCHAR(MAX) NULL,
            [attachment_data] NVARCHAR(MAX) NULL,
            [attachment_name] NVARCHAR(200) NULL,
            [remark] NVARCHAR(500) NULL,
            [created_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [updated_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [created_by] VARCHAR(100) NULL,
            [updated_by] VARCHAR(100) NULL
        )
        """,
        build_add_column_sql("tool_io_inspection_report", "report_no", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_report", "task_no", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_report", "inspector_id", "VARCHAR(50) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_report", "inspector_name", "NVARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_inspection_report", "inspection_date", "DATE NOT NULL DEFAULT '2000-01-01'"),
        build_add_column_sql("tool_io_inspection_report", "inspection_result", "VARCHAR(20) NOT NULL DEFAULT 'pass'"),
        build_add_column_sql("tool_io_inspection_report", "measurement_data", "NVARCHAR(MAX) NULL"),
        build_add_column_sql("tool_io_inspection_report", "attachment_data", "NVARCHAR(MAX) NULL"),
        build_add_column_sql("tool_io_inspection_report", "attachment_name", "NVARCHAR(200) NULL"),
        build_add_column_sql("tool_io_inspection_report", "remark", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_io_inspection_report", "created_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_inspection_report", "updated_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_inspection_report", "created_by", "VARCHAR(100) NULL"),
        build_add_column_sql("tool_io_inspection_report", "updated_by", "VARCHAR(100) NULL"),
        build_create_index_sql("tool_io_inspection_report", "IX_tool_io_inspection_report_task_no", "task_no"),
    ]
    return _execute_statements_in_transaction(sql_statements, "Inspection report table ensured")


def ensure_tool_inspection_status_table() -> bool:
    """Create or align tool inspection status table."""
    from backend.database.utils.sql_utils import build_add_column_sql, build_create_index_sql

    sql_statements = [
        """
        IF OBJECT_ID(N'tool_io_tool_inspection_status', N'U') IS NULL
        CREATE TABLE [tool_io_tool_inspection_status] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [serial_no] VARCHAR(100) NOT NULL UNIQUE,
            [tool_name] NVARCHAR(200) NULL,
            [drawing_no] VARCHAR(100) NULL,
            [last_inspection_date] DATE NULL,
            [next_inspection_date] DATE NULL,
            [inspection_cycle_days] INT NULL,
            [inspection_status] VARCHAR(20) NOT NULL DEFAULT 'pending',
            [remark] NVARCHAR(500) NULL,
            [updated_at] DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
            [updated_by] VARCHAR(100) NULL
        )
        """,
        build_add_column_sql("tool_io_tool_inspection_status", "serial_no", "VARCHAR(100) NOT NULL DEFAULT ''"),
        build_add_column_sql("tool_io_tool_inspection_status", "tool_name", "NVARCHAR(200) NULL"),
        build_add_column_sql("tool_io_tool_inspection_status", "drawing_no", "VARCHAR(100) NULL"),
        build_add_column_sql("tool_io_tool_inspection_status", "last_inspection_date", "DATE NULL"),
        build_add_column_sql("tool_io_tool_inspection_status", "next_inspection_date", "DATE NULL"),
        build_add_column_sql("tool_io_tool_inspection_status", "inspection_cycle_days", "INT NULL"),
        build_add_column_sql("tool_io_tool_inspection_status", "inspection_status", "VARCHAR(20) NOT NULL DEFAULT 'pending'"),
        build_add_column_sql("tool_io_tool_inspection_status", "remark", "NVARCHAR(500) NULL"),
        build_add_column_sql("tool_io_tool_inspection_status", "updated_at", "DATETIME2 NOT NULL DEFAULT SYSDATETIME()"),
        build_add_column_sql("tool_io_tool_inspection_status", "updated_by", "VARCHAR(100) NULL"),
        build_create_index_sql("tool_io_tool_inspection_status", "IX_tool_io_tool_inspection_status_next_date", "next_inspection_date"),
        build_create_index_sql("tool_io_tool_inspection_status", "IX_tool_io_tool_inspection_status_status", "inspection_status"),
    ]
    return _execute_statements_in_transaction(sql_statements, "Tool inspection status table ensured")


def ensure_tool_io_tables() -> bool:
    """
    Create the Tool IO tables required by the runtime if they do not exist.

    Returns:
        True if successful, False otherwise
    """
    from backend.database.core.database_manager import ORDER_NO_SEQUENCE_TABLE

    create_statements = [
        """
        IF OBJECT_ID(N'tool_io_order', N'U') IS NULL
        CREATE TABLE [tool_io_order] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [order_no] VARCHAR(64) NOT NULL UNIQUE,
            [order_type] VARCHAR(16) NOT NULL,
            [order_status] VARCHAR(32) NOT NULL DEFAULT 'draft',
            [initiator_id] VARCHAR(64) NOT NULL,
            [initiator_name] VARCHAR(64) NOT NULL,
            [initiator_role] VARCHAR(32) NOT NULL,
            [department] VARCHAR(64) NULL,
            [project_code] VARCHAR(64) NULL,
            [usage_purpose] VARCHAR(255) NULL,
            [planned_use_time] DATETIME NULL,
            [planned_return_time] DATETIME NULL,
            [target_location_id] BIGINT NULL,
            [target_location_text] VARCHAR(255) NULL,
            [keeper_id] VARCHAR(64) NULL,
            [keeper_name] VARCHAR(64) NULL,
            [transport_type] VARCHAR(32) NULL,
            [transport_operator_id] VARCHAR(64) NULL,
            [transport_operator_name] VARCHAR(64) NULL,
            [keeper_confirm_time] DATETIME NULL,
            [tool_quantity] INT NOT NULL DEFAULT 0,
            [confirmed_count] INT NOT NULL DEFAULT 0,
            [final_confirm_by] VARCHAR(64) NULL,
            [final_confirm_time] DATETIME NULL,
            [cancel_reason] VARCHAR(500) NULL,
            [reject_reason] VARCHAR(500) NULL,
            [remark] VARCHAR(500) NULL,
            [org_id] VARCHAR(64) NULL,
            [created_at] DATETIME NOT NULL DEFAULT GETDATE(),
            [updated_at] DATETIME NOT NULL DEFAULT GETDATE(),
            [created_by] VARCHAR(64) NULL,
            [updated_by] VARCHAR(64) NULL,
            [is_deleted] TINYINT NOT NULL DEFAULT 0
        )
        """,
        """
        IF OBJECT_ID(N'tool_io_order_item', N'U') IS NULL
        CREATE TABLE [tool_io_order_item] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [order_no] VARCHAR(64) NOT NULL,
            [tool_id] BIGINT NULL,
            [serial_no] VARCHAR(64) NOT NULL,
            [tool_name] VARCHAR(255) NULL,
            [drawing_no] VARCHAR(255) NULL,
            [spec_model] VARCHAR(255) NULL,
            [apply_qty] DECIMAL(18,2) NOT NULL DEFAULT 1,
            [confirmed_qty] DECIMAL(18,2) NOT NULL DEFAULT 0,
            [item_status] VARCHAR(32) NOT NULL DEFAULT 'pending_check',
            [tool_snapshot_status] VARCHAR(255) NULL,
            [tool_snapshot_location_text] VARCHAR(255) NULL,
            [tool_snapshot_location_id] BIGINT NULL,
            [confirm_by] VARCHAR(255) NULL,
            [confirm_by_id] BIGINT NULL,
            [confirm_by_name] VARCHAR(64) NULL,
            [confirm_time] DATETIME NULL,
            [reject_reason] VARCHAR(500) NULL,
            [io_complete_time] DATETIME NULL,
            [sort_order] INT NOT NULL DEFAULT 1,
            [created_at] DATETIME NOT NULL DEFAULT GETDATE(),
            [updated_at] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'tool_io_operation_log', N'U') IS NULL
        CREATE TABLE [tool_io_operation_log] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [order_no] VARCHAR(64) NOT NULL,
            [item_id] BIGINT NULL,
            [operation_type] VARCHAR(64) NOT NULL,
            [operator_id] VARCHAR(64) NULL,
            [operator_name] VARCHAR(64) NULL,
            [operator_role] VARCHAR(64) NULL,
            [from_status] VARCHAR(64) NULL,
            [to_status] VARCHAR(64) NULL,
            [operation_content] TEXT NULL,
            [operation_time] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'tool_io_notification', N'U') IS NULL
        CREATE TABLE [tool_io_notification] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [order_no] VARCHAR(64) NOT NULL,
            [notify_type] VARCHAR(64) NOT NULL,
            [notify_channel] VARCHAR(64) NULL,
            [receiver] VARCHAR(255) NULL,
            [notify_title] VARCHAR(255) NULL,
            [notify_content] TEXT NULL,
            [copy_text] TEXT NULL,
            [send_status] VARCHAR(32) NOT NULL DEFAULT 'pending',
            [send_time] DATETIME NULL,
            [send_result] TEXT NULL,
            [retry_count] INT NOT NULL DEFAULT 0,
            [created_at] DATETIME NOT NULL DEFAULT GETDATE()
        )
        """,
        """
        IF OBJECT_ID(N'tool_io_location', N'U') IS NULL
        CREATE TABLE [tool_io_location] (
            [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
            [location_code] VARCHAR(64) NOT NULL,
            [location_name] VARCHAR(255) NOT NULL,
            [location_desc] VARCHAR(255) NULL,
            [warehouse_area] VARCHAR(64) NULL,
            [storage_slot] VARCHAR(64) NULL,
            [shelf] VARCHAR(255) NULL,
            [remark] VARCHAR(500) NULL
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
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_tool_io_order_order_no' AND object_id = OBJECT_ID(N'tool_io_order'))
        CREATE INDEX [IX_tool_io_order_order_no] ON [tool_io_order]([order_no])
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_tool_io_order_order_status' AND object_id = OBJECT_ID(N'tool_io_order'))
        CREATE INDEX [IX_tool_io_order_order_status] ON [tool_io_order]([order_status])
        """,
        """
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_tool_io_order_created_at' AND object_id = OBJECT_ID(N'tool_io_order'))
        CREATE INDEX [IX_tool_io_order_created_at] ON [tool_io_order]([created_at])
        """,
    ]

    if not _execute_statements_in_transaction(create_statements, 'Tool IO tables ensured'):
        return False
    if not ensure_schema_alignment():
        return False
    if not ensure_feedback_table():
        return False
    if not ensure_feedback_reply_table():
        return False
    if not ensure_tool_status_change_history_table():
        return False
    if not ensure_transport_issue_table():
        return False
    if not ensure_system_config_table():
        return False
    if not ensure_mpl_table():
        return False
    if not ensure_inspection_plan_table():
        return False
    if not ensure_inspection_task_table():
        return False
    if not ensure_inspection_report_table():
        return False
    return ensure_tool_inspection_status_table()


def ensure_schema_alignment() -> bool:
    """
    Ensure schema alignment by adding missing columns and indexes.

    Returns:
        True if successful, False otherwise
    """
    sql_statements = _build_schema_alignment_sql()
    return _execute_statements_in_transaction(sql_statements, 'Schema alignment completed')
