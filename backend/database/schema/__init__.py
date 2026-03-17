# -*- coding: utf-8 -*-
"""Database schema management."""

from backend.database.schema.schema_manager import (
    ensure_tool_io_tables,
    ensure_schema_alignment,
    ensure_feedback_table,
    ensure_feedback_reply_table,
    ensure_tool_status_change_history_table,
    SCHEMA_ALIGNMENT_INDEXES,
)
from backend.database.schema.column_names import (
    ORDER_COLUMNS,
    ITEM_COLUMNS,
    LOG_COLUMNS,
    NOTIFY_COLUMNS,
    LOCATION_COLUMNS,
    TOOL_MASTER_COLUMNS,
    TOOL_STATUS_HISTORY_COLUMNS,
    FEEDBACK_COLUMNS,
    FEEDBACK_REPLY_COLUMNS,
    ORG_COLUMNS,
    USER_ORG_REL_COLUMNS,
    SYS_USER_COLUMNS,
    PASSWORD_CHANGE_LOG_COLUMNS,
)

__all__ = [
    # Schema manager
    "ensure_tool_io_tables",
    "ensure_schema_alignment",
    "ensure_feedback_table",
    "ensure_feedback_reply_table",
    "ensure_tool_status_change_history_table",
    "SCHEMA_ALIGNMENT_INDEXES",
    # Column name constants
    "ORDER_COLUMNS",
    "ITEM_COLUMNS",
    "LOG_COLUMNS",
    "NOTIFY_COLUMNS",
    "LOCATION_COLUMNS",
    "TOOL_MASTER_COLUMNS",
    "TOOL_STATUS_HISTORY_COLUMNS",
    "FEEDBACK_COLUMNS",
    "FEEDBACK_REPLY_COLUMNS",
    "ORG_COLUMNS",
    "USER_ORG_REL_COLUMNS",
    "SYS_USER_COLUMNS",
    "PASSWORD_CHANGE_LOG_COLUMNS",
]
