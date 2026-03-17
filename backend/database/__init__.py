# -*- coding: utf-8 -*-
"""Database modularization package - Public API exports."""

# Core layer
from backend.database.core import (
    ConnectionPool,
    DatabaseManager,
    db_manager,
    QueryExecutor,
)

# Schema layer
from backend.database.schema import (
    ensure_tool_io_tables,
    ensure_schema_alignment,
    SCHEMA_ALIGNMENT_INDEXES,
)

# Utils layer
from backend.database.utils import (
    normalize_date,
    format_date,
    format_datetime,
    get_date_range,
    is_date_in_range,
    quote_sql_string,
    build_add_column_sql,
    build_create_index_sql,
    build_rename_column_sql,
    build_in_clause,
    build_pagination_sql,
    build_count_sql,
    is_duplicate_key_error,
    safe_bigint,
    build_where_clause,
    build_set_clause,
)

# Repositories
from backend.database.repositories import (
    ToolRepository,
    DispatchRepository,
    TPITRRepository,
    AcceptanceRepository,
    OrderRepository,
    ToolIOAction,
)

# Services
from backend.database.services import (
    OrderService,
    generate_order_no_atomic,
    DashboardService,
    get_monitor_stats,
    get_tpitr_status,
    get_expiry_detail,
    get_dispatch_detail,
    get_acceptance_detail,
    calculate_alert_level,
)

__all__ = [
    # Core
    "ConnectionPool",
    "DatabaseManager",
    "db_manager",
    "QueryExecutor",
    # Schema
    "ensure_tool_io_tables",
    "ensure_schema_alignment",
    "SCHEMA_ALIGNMENT_INDEXES",
    # Utils - date
    "normalize_date",
    "format_date",
    "format_datetime",
    "get_date_range",
    "is_date_in_range",
    # Utils - sql
    "quote_sql_string",
    "build_add_column_sql",
    "build_create_index_sql",
    "build_rename_column_sql",
    "build_in_clause",
    "build_pagination_sql",
    "build_count_sql",
    "is_duplicate_key_error",
    "safe_bigint",
    "build_where_clause",
    "build_set_clause",
    # Repositories
    "ToolRepository",
    "DispatchRepository",
    "TPITRRepository",
    "AcceptanceRepository",
    "OrderRepository",
    "ToolIOAction",
    # Services
    "OrderService",
    "generate_order_no_atomic",
    "DashboardService",
    "get_monitor_stats",
    "get_tpitr_status",
    "get_expiry_detail",
    "get_dispatch_detail",
    "get_acceptance_detail",
    "calculate_alert_level",
]
