# -*- coding: utf-8 -*-
"""
Dashboard service module.
Handles dashboard statistics and metrics.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from database import DatabaseManager
from backend.services.rbac_data_scope_service import (
    build_order_scope_sql,
    resolve_order_data_scope,
)
from backend.services.tool_io_service import _resolve_scope_context

logger = logging.getLogger(__name__)


def get_dashboard_stats(current_user: Optional[Dict] = None) -> Dict:
    """Get dashboard statistics."""
    db = DatabaseManager()
    scope_context = _resolve_scope_context(current_user)
    role_codes = scope_context.get("role_codes", [])
    user_id = scope_context.get("user_id", "")
    org_ids = scope_context.get("org_ids", [])

    # Build scope conditions
    scope_sql, scope_params = build_order_scope_sql(role_codes, user_id, org_ids)

    try:
        # Get counts by status
        status_counts_sql = """
            SELECT order_status, COUNT(*) as count
            FROM 工装出入库单_主表
            WHERE 1=1
        """
        params = []

        if scope_sql:
            status_counts_sql += f" AND {scope_sql}"
            params.extend(scope_params)

        status_counts_sql += " GROUP BY order_status"

        status_rows = db.execute_query(status_counts_sql, tuple(params) if params else None)

        stats = {
            "draft": 0,
            "submitted": 0,
            "keeper_confirmed": 0,
            "transport_in_progress": 0,
            "transport_completed": 0,
            "completed": 0,
            "rejected": 0,
            "cancelled": 0,
            "total": 0,
        }

        for row in status_rows:
            status = row.get("order_status", "")
            count = row.get("count", 0)
            if status in stats:
                stats[status] = count
            stats["total"] += count

        # Get today's stats
        today_sql = """
            SELECT
                COUNT(CASE WHEN order_type = 'outbound' THEN 1 END) as today_outbound,
                COUNT(CASE WHEN order_type = 'inbound' THEN 1 END) as today_inbound
            FROM 工装出入库单_主表
            WHERE CAST(created_at AS DATE) = CAST(SYSDATETIME() AS DATE)
        """
        if scope_sql:
            today_sql += f" AND {scope_sql}"

        today_row = db.execute_query(today_sql, tuple(params) if params else None)
        if today_row:
            stats["today_outbound"] = today_row[0].get("today_outbound", 0)
            stats["today_inbound"] = today_row[0].get("today_inbound", 0)

        return {"success": True, "stats": stats}

    except Exception as exc:
        logger.error("failed to get dashboard stats: %s", exc)
        return {"success": False, "error": str(exc)}
