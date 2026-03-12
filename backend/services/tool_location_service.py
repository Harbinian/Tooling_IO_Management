# -*- coding: utf-8 -*-
"""Tool location resolution and workflow-driven location updates."""

from __future__ import annotations

import logging
from typing import Dict, List

from database import DatabaseManager
from backend.services.audit_log_service import OPERATION_LOCATION_UPDATE, write_order_audit_log

logger = logging.getLogger(__name__)


def resolve_tool_master_location(tool_code: str) -> Dict:
    rows = DatabaseManager().execute_query(
        """
        SELECT
            [序列号] AS tool_code,
            [库位] AS current_location_text,
            [应用历史] AS location_history_text
        FROM [工装身份卡_主表]
        WHERE [序列号] = ?
        """,
        (str(tool_code or "").strip(),),
    )
    if not rows:
        return {"success": False, "error": "tool not found", "data": {}}
    row = rows[0]
    return {
        "success": True,
        "data": {
            "tool_code": row.get("tool_code", ""),
            "current_location_text": row.get("current_location_text", ""),
            "location_history_text": row.get("location_history_text", ""),
            "authoritative_source": "tool_master",
        },
    }


def resolve_order_item_location(order: Dict, item: Dict) -> Dict:
    master_location = resolve_tool_master_location(item.get("tool_code", ""))
    order_status = str(order.get("order_status") or "").strip()
    current_location_text = (
        item.get("current_location_text")
        or item.get("keeper_confirm_location_text")
        or (master_location.get("data") or {}).get("current_location_text", "")
    )
    authoritative_source = "tool_master"

    if order_status == "transport_in_progress":
        current_location_text = item.get("keeper_confirm_location_text") or current_location_text
        authoritative_source = "transport_in_progress"
    elif order_status in {"transport_completed", "completed"} and str(order.get("order_type") or "") == "outbound":
        current_location_text = order.get("target_location_text") or current_location_text
        authoritative_source = "workflow_target_location"
    elif order_status in {"transport_completed", "completed"} and str(order.get("order_type") or "") == "inbound":
        current_location_text = item.get("keeper_confirm_location_text") or current_location_text
        authoritative_source = "workflow_storage_location"

    return {
        "tool_code": item.get("tool_code", ""),
        "current_location_text": current_location_text,
        "authoritative_source": authoritative_source,
        "tool_master_location": (master_location.get("data") or {}).get("current_location_text", ""),
    }


def _determine_target_location(order: Dict, item: Dict, milestone: str) -> str:
    order_type = str(order.get("order_type") or "").strip()
    target_location_text = str(order.get("target_location_text") or "").strip()
    keeper_location_text = str(item.get("keeper_confirm_location_text") or item.get("location_text") or "").strip()

    if milestone in {"transport_complete", "final_confirm"}:
        if order_type == "outbound":
            return target_location_text or keeper_location_text
        return keeper_location_text or target_location_text
    return ""


def update_tool_location(
    *,
    tool_code: str,
    new_location_text: str,
    order_no: str = "",
    operator_user_id: str = "",
    operator_name: str = "",
    operator_role: str = "",
    remark: str = "",
) -> Dict:
    current = resolve_tool_master_location(tool_code)
    if not current.get("success"):
        return current

    previous_location = str((current.get("data") or {}).get("current_location_text") or "").strip()
    next_location = str(new_location_text or "").strip()
    if not next_location or next_location == previous_location:
        return {
            "success": True,
            "tool_code": tool_code,
            "previous_location": previous_location,
            "new_location": previous_location,
            "changed": False,
        }

    DatabaseManager().execute_query(
        """
        UPDATE [工装身份卡_主表]
        SET [库位] = ?
        WHERE [序列号] = ?
        """,
        (next_location, tool_code),
        fetch=False,
    )
    write_order_audit_log(
        order_no=order_no,
        operation_type=OPERATION_LOCATION_UPDATE,
        operator_user_id=operator_user_id,
        operator_name=operator_name,
        operator_role=operator_role,
        previous_status=previous_location,
        new_status=next_location,
        remark=remark or f"tool {tool_code} location updated",
    )
    return {
        "success": True,
        "tool_code": tool_code,
        "previous_location": previous_location,
        "new_location": next_location,
        "changed": True,
    }


def apply_order_location_updates(
    *,
    order: Dict,
    milestone: str,
    operator_user_id: str = "",
    operator_name: str = "",
    operator_role: str = "",
) -> Dict:
    if not order:
        return {"success": False, "error": "order is required", "data": []}

    results: List[Dict] = []
    for item in order.get("items", []) or []:
        tool_code = str(item.get("tool_code") or "").strip()
        if not tool_code:
            continue
        next_location = _determine_target_location(order, item, milestone)
        if not next_location:
            continue
        result = update_tool_location(
            tool_code=tool_code,
            new_location_text=next_location,
            order_no=str(order.get("order_no") or "").strip(),
            operator_user_id=operator_user_id,
            operator_name=operator_name,
            operator_role=operator_role,
            remark=f"{milestone} location update for {tool_code}: {next_location}",
        )
        results.append(result)

    return {"success": True, "data": results}
