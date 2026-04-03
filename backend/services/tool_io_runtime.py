"""Runtime-safe Tool IO wrappers for workflow paths."""

from __future__ import annotations

import logging
from typing import Dict, List

from backend.database.schema.column_names import LOG_COLUMNS, NOTIFY_COLUMNS, TABLE_NAMES
from database import (
    DatabaseManager,
    get_pending_keeper_orders,
    get_tool_io_logs,
    get_tool_io_order,
    keeper_confirm_order,
)

logger = logging.getLogger(__name__)


def list_pending_keeper_orders(keeper_id: str | None = None) -> List[Dict]:
    """Return orders waiting for keeper processing."""
    try:
        return get_pending_keeper_orders(keeper_id)
    except Exception as exc:
        logger.error("Failed to load keeper pending orders: %s", exc)
        return []


def get_order_detail_runtime(order_no: str) -> Dict:
    """Return one order with item and notification records."""
    try:
        order = get_tool_io_order(order_no)
        if not order:
            return {}
        order["notification_records"] = []
        return order
    except Exception as exc:
        logger.error("Failed to load order detail for %s: %s", order_no, exc)
        return {}


def get_order_logs_runtime(order_no: str) -> List[Dict]:
    """Return audit logs for one order."""
    try:
        return get_tool_io_logs(order_no)
    except Exception as exc:
        logger.error("Failed to load order logs for %s: %s", order_no, exc)
        return []


def keeper_confirm_runtime(
    order_no: str,
    keeper_id: str,
    keeper_name: str,
    confirm_data: Dict,
    operator_id: str,
    operator_name: str,
    operator_role: str,
) -> Dict:
    """Persist keeper confirmation using the stable database implementation."""
    try:
        confirmed_items = confirm_data.get("items", [])
        notes = confirm_data.get("keeper_remark", "")
        result = keeper_confirm_order(
            order_no,
            keeper_id,
            keeper_name,
            confirmed_items,
            notes,
        )
        if result.get("success"):
            result.setdefault("before_status", "submitted")
            result.setdefault("after_status", result.get("status", ""))
            result.setdefault("keeper_remark", str((confirm_data or {}).get("keeper_remark") or "").strip())
        return result
    except Exception as exc:
        logger.error("Keeper confirmation failed for %s: %s", order_no, exc)
        return {"success": False, "error": str(exc)}


def get_recent_operation_errors(limit: int = 20) -> List[Dict]:
    """Return recent operation errors from audit logs."""
    try:
        db = DatabaseManager()
        return db.execute_query(
            f"""
            SELECT TOP (?) *
            FROM [{TABLE_NAMES['ORDER_LOG']}]
            ORDER BY [{LOG_COLUMNS['operation_time']}] DESC
            """,
            (limit,),
        )
    except Exception as exc:
        logger.error("Failed to query recent errors: %s", exc)
        return []


def get_recent_notification_failures(limit: int = 20) -> List[Dict]:
    """Return recent notification failures."""
    try:
        db = DatabaseManager()
        return db.execute_query(
            f"""
            SELECT TOP (?) *
            FROM [{TABLE_NAMES['ORDER_NOTIFICATION']}]
            ORDER BY [{NOTIFY_COLUMNS['send_time']}] DESC
            """,
            (limit,),
        )
    except Exception as exc:
        logger.error("Failed to query notification failures: %s", exc)
        return []
