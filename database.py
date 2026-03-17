# -*- coding: utf-8 -*-
"""
工装定检全流程监控系统 - 数据库连接模块
========================================
功能: 提供数据库连接和查询功能（含连接池）
版本: V5.0 (Facade + 分层架构)
日期: 2025-01-23
========================================

支持:
- 环境变量配置 (CESOFT_ 前缀)
- 统一配置层 config.settings
- 数据库连接池
- 连接复用
- 日期类型标准化

本模块为Facade层，实际实现委托给 backend.database 分层架构。

环境变量配置:
  CESOFT_DB_SERVER     - 数据库服务器地址 (默认: 192.168.19.220,1433)
  CESOFT_DB_DATABASE   - 数据库名称 (默认: CXSYSYS)
  CESOFT_DB_USERNAME   - 用户名 (默认: sa)
  CESOFT_DB_PASSWORD   - 密码
  CESOFT_DB_DRIVER     - ODBC驱动 (默认: {SQL Server})
  CESOFT_DB_POOL_SIZE  - 连接池大小 (默认: 5)
  CESOFT_DB_POOL_TIMEOUT - 连接超时(秒) (默认: 30)
========================================
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

# 添加项目根目录到路径
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

logger = logging.getLogger(__name__)

# ========================================
# 导入分层架构模块 (Facade Delegation)
# ========================================

# Core layer - 连接池和数据库管理器
from backend.database.core import (
    ConnectionPool,
    DatabaseManager,
    db_manager,
    QueryExecutor,
)

# Schema layer - 表结构管理
from backend.database.schema import (
    ensure_tool_io_tables,
    ensure_schema_alignment,
    ensure_feedback_table,
    ensure_feedback_reply_table,
    ensure_tool_status_change_history_table,
    SCHEMA_ALIGNMENT_INDEXES,
)

# Utils layer - 工具函数
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

# Repositories - 数据访问层
from backend.database.repositories import (
    ToolRepository,
    DispatchRepository,
    TPITRRepository,
    AcceptanceRepository,
    OrderRepository,
    ToolIOAction,
)

# Services - 业务服务层
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

# ========================================
# 保留原有的常量和辅助函数 (向後兼容)
# ========================================

# 订单号序列表
ORDER_NO_SEQUENCE_TABLE = "tool_io_order_no_sequence"
ORDER_NO_RETRY_LIMIT = 3

# 保留原始辅助函数 (供内部使用)
def _quote_sql_string(value: str) -> str:
    """Quote SQL string for safe execution."""
    return quote_sql_string(value)

def _build_add_column_sql(table_name: str, column_name: str, definition: str) -> str:
    """Build ADD COLUMN SQL statement."""
    return build_add_column_sql(table_name, column_name, definition)

def _build_create_index_sql(table_name: str, index_name: str, column_list: str) -> str:
    """Build CREATE INDEX SQL statement."""
    return build_create_index_sql(table_name, index_name, column_list)

def _build_rename_column_sql(table_name: str, old_name: str, new_name: str) -> str:
    """Build RENAME COLUMN SQL statement."""
    return build_rename_column_sql(table_name, old_name, new_name)

def _is_duplicate_key_error(error: Exception) -> bool:
    """Check if error is a duplicate key error."""
    return is_duplicate_key_error(error)

def _normalize_date(value: Any) -> Optional[datetime]:
    """Normalize date value."""
    return normalize_date(value)

def _format_date(value: Any, fmt: str = '%Y-%m-%d') -> str:
    """Format date to string."""
    return format_date(value, fmt)

def _safe_bigint(value: Any) -> Optional[int]:
    """Safely convert to bigint."""
    return safe_bigint(value)

# ========================================
# 向后兼容的公共 API (委托给分层架构)
# ========================================

def get_db_manager() -> DatabaseManager:
    """Get database manager singleton (backward compatibility)."""
    return db_manager

def test_db_connection() -> Tuple[bool, str]:
    """Test database connection."""
    try:
        manager = db_manager
        with manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
        return True, "Connection successful"
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False, str(e)

def get_tpitr_status_detail(tpitr: Dict) -> Dict:
    """Get TPITR status detail (backward compatibility)."""
    from backend.database.repositories.tpitr_repository import TPITRRepository
    repo = TPITRRepository()
    return repo.get_tpitr_status_detail(tpitr)

def get_tpitr_categories() -> Dict:
    """Get TPITR categories (backward compatibility)."""
    from backend.database.repositories.tpitr_repository import TPITRRepository
    repo = TPITRRepository()
    return repo.get_tpitr_categories()

def get_expired_tpitr_status() -> Dict:
    """Get expired TPITR status (backward compatibility)."""
    from backend.database.repositories.tpitr_repository import TPITRRepository
    repo = TPITRRepository()
    return repo.get_expired_tpitr_status()

def get_overdue_dispatch_status() -> Dict:
    """Get overdue dispatch status (backward compatibility)."""
    from backend.database.repositories.dispatch_repository import DispatchRepository
    repo = DispatchRepository()
    return repo.get_overdue_dispatch_status()

# ========================================
# 工装出入库订单相关函数 (委托给 OrderRepository)
# ========================================

def create_tool_io_order(order_data: dict) -> dict:
    """
    Create a new tool IO order.

    Args:
        order_data: Order data dictionary

    Returns:
        Result dictionary with success status and order info
    """
    repo = OrderRepository()
    return repo.create_order(order_data)

def submit_tool_io_order(order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
    """
    Submit a tool IO order.

    Args:
        order_no: Order number
        operator_id: Operator ID
        operator_name: Operator name
        operator_role: Operator role

    Returns:
        Result dictionary
    """
    repo = OrderRepository()
    return repo.submit_order(order_no, operator_id, operator_name, operator_role)

def get_tool_io_order(order_no: str) -> dict:
    """
    Get tool IO order by order number.

    Args:
        order_no: Order number

    Returns:
        Order dictionary
    """
    repo = OrderRepository()
    return repo.get_order_by_no(order_no)

def get_tool_io_orders(
    order_type: Optional[str] = None,
    status: Optional[str] = None,
    keeper_id: Optional[str] = None,
    applicant_id: Optional[str] = None,
    keyword: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> dict:
    """
    Get tool IO orders with filters and pagination.

    Args:
        order_type: Order type filter (outbound/inbound)
        status: Status filter
        keeper_id: Keeper ID filter
        applicant_id: Applicant ID filter
        keyword: Search keyword
        date_from: Start date
        date_to: End date
        page: Page number (1-based)
        page_size: Page size

    Returns:
        Dictionary with orders list and pagination info
    """
    repo = OrderRepository()
    return repo.get_orders(
        order_type=order_type,
        order_status=status,
        keeper_id=keeper_id,
        initiator_id=applicant_id,
        keyword=keyword,
        date_from=date_from,
        date_to=date_to,
        page_no=page,
        page_size=page_size
    )

def keeper_confirm_order(order_no: str, keeper_id: str, keeper_name: str, confirmed_items: List[Dict], notes: str = "", operator_id: str = "", operator_name: str = "", operator_role: str = "") -> dict:
    """
    Keeper confirms a tool IO order.

    Args:
        order_no: Order number
        keeper_id: Keeper ID
        keeper_name: Keeper name
        confirmed_items: List of confirmed items
        notes: Optional notes
        operator_id: Operator ID
        operator_name: Operator name
        operator_role: Operator role

    Returns:
        Result dictionary
    """
    repo = OrderRepository()
    confirm_data = {"items": confirmed_items, "keeper_remark": notes}
    return repo.keeper_confirm(order_no, keeper_id, keeper_name, confirm_data, operator_id or keeper_id, operator_name or keeper_name, operator_role or "keeper")

def final_confirm_order(order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
    """
    Final confirmation of a tool IO order.

    Args:
        order_no: Order number
        operator_id: Operator ID
        operator_name: Operator name
        operator_role: Operator role

    Returns:
        Result dictionary
    """
    repo = OrderRepository()
    return repo.final_confirm(order_no, operator_id, operator_name, operator_role)

def reject_tool_io_order(order_no: str, operator_id: str, operator_name: str, operator_role: str, reason: str) -> dict:
    """
    Reject a tool IO order.

    Args:
        order_no: Order number
        operator_id: Operator ID
        operator_name: Operator name
        operator_role: Operator role
        reason: Rejection reason

    Returns:
        Result dictionary
    """
    repo = OrderRepository()
    return repo.reject_order(order_no, reason, operator_id, operator_name, operator_role)

def reset_order_to_draft_order(order_no: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
    """
    Reset a rejected order back to draft status.

    Args:
        order_no: Order number
        operator_id: Operator ID
        operator_name: Operator name
        operator_role: Operator role

    Returns:
        Result dictionary
    """
    repo = OrderRepository()
    return repo.reset_order_to_draft(order_no, operator_id, operator_name, operator_role)

def cancel_tool_io_order(
    order_no: str,
    operator_id: str,
    operator_name: str,
    operator_role: str,
    reason: str = "",
) -> dict:
    """
    Cancel a tool IO order.

    Args:
        order_no: Order number
        operator_id: Operator ID
        operator_name: Operator name
        operator_role: Operator role
        reason: Cancellation reason

    Returns:
        Result dictionary
    """
    repo = OrderRepository()
    return repo.cancel_order(order_no, operator_id, operator_name, operator_role, reason)

def get_pending_keeper_orders(keeper_id: str = None) -> list:
    """
    Get pending keeper orders.

    Args:
        keeper_id: Optional keeper ID filter

    Returns:
        List of pending orders
    """
    repo = OrderRepository()
    return repo.get_pending_keeper_orders(keeper_id)

# ========================================
# 工装搜索相关函数 (委托给 ToolRepository)
# ========================================

def search_tools(
    keyword: str = "",
    status: Optional[str] = None,
    location: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> dict:
    """
    Search tools with filters.

    Args:
        keyword: Search keyword (tool code, name, etc.)
        status: Tool status filter
        location: Location filter (supports LIKE wildcard matching)
        page: Page number
        page_size: Page size

    Returns:
        Dictionary with tools list and pagination info
    """
    repo = ToolRepository()
    return repo.search_tools(keyword, status, location_keyword=location, page_no=page, page_size=page_size)

def check_tools_available(tool_codes: List[str], exclude_order_no: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if tools are available for reservation.

    Args:
        tool_codes: List of tool codes
        exclude_order_no: Order number to exclude from check

    Returns:
        Dictionary with availability status
    """
    repo = ToolRepository()
    return repo.check_tools_available(tool_codes, exclude_order_no)

# ========================================
# 操作日志相关函数
# ========================================

def add_tool_io_log(log_data: dict) -> bool:
    """
    Add operation log for tool IO order.

    Args:
        log_data: Log data dictionary

    Returns:
        True if successful
    """
    repo = OrderRepository()
    return repo.add_tool_io_log(log_data)

def get_tool_io_logs(order_no: str) -> list:
    """
    Get operation logs for an order.

    Args:
        order_no: Order number

    Returns:
        List of log entries
    """
    repo = OrderRepository()
    return repo.get_tool_io_logs(order_no)

# ========================================
# 通知相关函数
# ========================================

def add_tool_io_notification(notify_data: dict) -> int:
    """
    Add notification record.

    Args:
        notify_data: Notification data

    Returns:
        Notification ID if successful, 0 otherwise
    """
    repo = OrderRepository()
    return repo.add_notification(notify_data)

def update_notification_status(
    notify_id: int,
    status: str,
    error_message: str = ""
) -> dict:
    """
    Update notification status.

    Args:
        notify_id: Notification ID
        status: New status
        error_message: Error message if failed

    Returns:
        Result dictionary
    """
    repo = OrderRepository()
    return repo.update_notification_status(notify_id, status, error_message)

# ========================================
# 验收相关函数 (委托给 AcceptanceRepository)
# ========================================

def sync_applications_to_acceptance() -> Dict:
    """Sync applications to acceptance records."""
    repo = AcceptanceRepository()
    return repo.sync_applications_to_acceptance()

def add_acceptance_record(dispatch_no: str, serial_no: str, drawing_no: str,
                          acceptance_status: str = "pending", inspector: str = "") -> Dict:
    """Add acceptance record."""
    repo = AcceptanceRepository()
    return repo.add_acceptance_record(dispatch_no, serial_no, drawing_no, acceptance_status, inspector)

def update_acceptance_status(dispatch_no: str, status: str, **kwargs) -> Dict:
    """Update acceptance status."""
    repo = AcceptanceRepository()
    return repo.update_acceptance_status(dispatch_no, status, **kwargs)

def save_acceptance_account(dispatch_no: str, table_no: str, serial_no: str,
                            account_data: Dict) -> Dict:
    """Save acceptance account data."""
    repo = AcceptanceRepository()
    return repo.save_acceptance_account(dispatch_no, table_no, serial_no, account_data)

def get_inspector_acceptance_tasks(inspector: str = None) -> List[Dict]:
    """Get inspector acceptance tasks."""
    repo = AcceptanceRepository()
    return repo.get_inspector_acceptance_tasks(inspector)

def start_inspection(dispatch_no: str, inspector: str) -> Dict:
    """Start inspection."""
    repo = AcceptanceRepository()
    return repo.start_inspection(dispatch_no, inspector)

def submit_inspection_result(dispatch_no: str, result: str, **kwargs) -> Dict:
    """Submit inspection result."""
    repo = AcceptanceRepository()
    return repo.submit_inspection_result(dispatch_no, result, **kwargs)

# ========================================
# 导出的公共接口
# ========================================

__all__ = [
    # Core
    "ConnectionPool",
    "DatabaseManager",
    "db_manager",
    "QueryExecutor",

    # Schema
    "ensure_tool_io_tables",
    "ensure_schema_alignment",
    "ensure_feedback_table",
    "ensure_feedback_reply_table",
    "ensure_tool_status_change_history_table",
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

    # Backward compatible functions
    "get_db_manager",
    "test_db_connection",
    "get_tpitr_status_detail",
    "get_tpitr_categories",
    "get_expired_tpitr_status",
    "get_overdue_dispatch_status",

    # Order functions
    "create_tool_io_order",
    "submit_tool_io_order",
    "get_tool_io_order",
    "get_tool_io_orders",
    "keeper_confirm_order",
    "final_confirm_order",
    "reject_tool_io_order",
    "cancel_tool_io_order",
    "get_pending_keeper_orders",

    # Tool functions
    "search_tools",
    "check_tools_available",

    # Log functions
    "add_tool_io_log",
    "get_tool_io_logs",

    # Notification functions
    "add_tool_io_notification",
    "update_notification_status",

    # Acceptance functions
    "sync_applications_to_acceptance",
    "add_acceptance_record",
    "update_acceptance_status",
    "save_acceptance_account",
    "get_inspector_acceptance_tasks",
    "start_inspection",
    "submit_inspection_result",

    # Constants
    "ORDER_NO_SEQUENCE_TABLE",
    "ORDER_NO_RETRY_LIMIT",
]
