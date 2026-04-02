# -*- coding: utf-8 -*-
"""
Order query and CRUD service module.
Handles create, read, list, and search operations for orders and tools.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from database import (
    DatabaseManager,
    create_tool_io_order,
    get_tool_io_orders,
    search_tools,
)
from backend.services.rbac_data_scope_service import (
    build_order_scope_sql,
    resolve_order_data_scope,
)
from backend.services.tool_io_service import (
    _extract_item_values,
    _extract_order_values,
    _format_order_datetime,
    _is_order_accessible,
    _normalize_runtime_order,
    _pick_value,
    _resolve_scope_context,
)

logger = logging.getLogger(__name__)


def create_order(payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Create a new tool IO order."""
    from backend.services.tool_io_service import (
        _build_actor_context,
        _emit_internal_notification,
        ORDER_CREATED,
    )

    actor = _build_actor_context(payload)
    result = create_tool_io_order(payload)
    if result.get("success"):
        order = result.get("order", {})
        _emit_internal_notification(
            ORDER_CREATED,
            order=order,
            actor=actor,
            target_role="keeper",
        )
    return result


def list_orders(filters: Dict, current_user: Optional[Dict] = None) -> Dict:
    """List orders with filtering and pagination."""
    scope_context = _resolve_scope_context(current_user)
    filters = dict(filters) if filters else {}

    # Apply data scope filtering
    scope_sql, scope_params = build_order_scope_sql(scope_context)

    if scope_sql:
        filters["scope_sql"] = scope_sql
        filters["scope_params"] = scope_params

    result = get_tool_io_orders(filters)

    # Post-filter for runtime data
    if result.get("success"):
        orders = result.get("orders", [])
        filtered = [
            order for order in orders
            if _is_order_accessible(order, current_user)
        ]
        result["orders"] = filtered
        result["total"] = len(filtered)

    return result


def get_order_detail(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    """Get detailed order information including items."""
    from backend.services.tool_io_runtime import get_order_detail_runtime

    runtime_result = get_order_detail_runtime(order_no, current_user)
    if not runtime_result.get("success"):
        return runtime_result

    order = runtime_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return {
            "success": False,
            "error": "order not found",
        }

    # Enrich with computed fields
    order["items"] = [
        _normalize_runtime_order(item) for item in order.get("items", [])
    ]

    return {
        "success": True,
        "order": order,
    }


def search_tool_inventory(filters: Dict) -> Dict:
    """Search tool inventory."""
    return search_tools(
        keyword=filters.get("keyword"),
        status=filters.get("status"),
        location=filters.get("location"),
        page=filters.get("page_no", 1),
        page_size=filters.get("page_size", 20),
    )


def batch_query_tools(tool_codes: List[str]) -> Dict:
    """Batch query tools by codes."""
    if not tool_codes:
        return {"success": True, "tools": []}

    db = DatabaseManager()
    placeholders = ",".join(["?"] * len(tool_codes))
    sql = f"""
        SELECT
            serial_no,
            tool_name,
            spec,
            unit,
            location,
            quantity as available_quantity,
            status,
            remark
        FROM 工装主数据
        WHERE serial_no IN ({placeholders})
          AND status = 'active'
        ORDER BY serial_no
    """
    try:
        rows = db.execute_query(sql, tuple(tool_codes))
        tools = [_extract_tool_values(row) for row in rows]
        return {"success": True, "tools": tools}
    except Exception as exc:
        logger.error("batch query tools failed: %s", exc)
        return {"success": False, "error": str(exc)}


def _extract_tool_values(record: Dict) -> Dict:
    """Extract tool values from database record."""
    return {
        "serial_no": _pick_value(record, ["serial_no", "tool_code", "ToolCode"], ""),
        "tool_name": _pick_value(record, ["tool_name", "ToolName"], ""),
        "spec": _pick_value(record, ["spec", "Spec"], ""),
        "unit": _pick_value(record, ["unit", "Unit"], ""),
        "location": _pick_value(record, ["location", "Location"], ""),
        "available_quantity": _pick_value(record, ["available_quantity", "AvailableQuantity", "quantity"], 0),
        "status": _pick_value(record, ["status", "Status"], "active"),
        "remark": _pick_value(record, ["remark", "Remark"], ""),
    }
