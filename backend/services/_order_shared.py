# -*- coding: utf-8 -*-
"""
Order-related shared functions.
Imported by order_workflow_service, order_query_service, dashboard_service, and tool_io_service.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from backend.database.schema.column_names import ORDER_COLUMNS, ITEM_COLUMNS
from backend.services.rbac_data_scope_service import (
    order_matches_scope,
    resolve_order_data_scope,
)

from backend.services._shared_utils import _pick_value


def _resolve_scope_context(current_user: Optional[Dict]) -> Dict:
    if not current_user:
        return {
            "scope_types": ["ALL"],
            "all_access": True,
            "org_ids": [],
            "org_user_ids": [],
            "self_user_ids": [],
            "assigned_user_ids": [],
            "current_user_id": "",
        }
    return resolve_order_data_scope(current_user or {})


def _is_order_accessible(order: Dict, current_user: Optional[Dict]) -> bool:
    if not current_user:
        return True
    scope_context = _resolve_scope_context(current_user)
    if not order_matches_scope(order, scope_context):
        return False
    if scope_context.get("all_access"):
        return (order.get("order_status") or "").strip().lower() != "draft"
    return True


def _normalize_runtime_order(order: Dict) -> Dict:
    if not order:
        return {}
    normalized_items = []
    approved_count_from_items = 0
    for item in order.get("items", []) or []:
        item_status = _pick_value(item, ["item_status", "status"], "")
        normalized_items.append(
            {
                **item,
                "serial_no": _pick_value(item, ["serial_no", "tool_code"], ""),
                "tool_name": _pick_value(item, ["tool_name", "工装名称"], ""),
                "drawing_no": _pick_value(item, ["drawing_no", "工装图号"], ""),
                "spec_model": _pick_value(item, ["spec_model", "机型", "规格型号"], ""),
                "location_text": _pick_value(item, ["location_text"], ""),
                "apply_qty": _pick_value(item, ["apply_qty", "申请数量"], 1),
                "approved_qty": _pick_value(item, ["approved_qty", "确认数量"], 0),
                "item_status": item_status,
            }
        )
        if item_status == "approved":
            approved_count_from_items += 1
    tool_count = len(normalized_items)
    approved_count = _pick_value(order, ["approved_count"], approved_count_from_items)
    try:
        approved_count = int(approved_count or 0)
    except (TypeError, ValueError):
        approved_count = 0
    return {
        **order,
        "order_no": _pick_value(order, ["order_no", "出入库单号"], ""),
        "order_type": _pick_value(order, ["order_type", "单据类型"], ""),
        "order_status": _pick_value(order, ["order_status", "单据状态"], ""),
        "initiator_id": _pick_value(order, ["initiator_id", "发起人ID"], ""),
        "initiator_name": _pick_value(order, ["initiator_name", "发起人姓名"], ""),
        "keeper_id": _pick_value(order, ["keeper_id", "保管员ID"], ""),
        "keeper_name": _pick_value(order, ["keeper_name", "保管员姓名"], ""),
        "transport_type": _pick_value(order, ["transport_type", "运输类型"], ""),
        "transport_assignee_id": _pick_value(order, ["transport_assignee_id", "运输AssigneeID", "运输人ID"], ""),
        "transport_assignee_name": _pick_value(order, ["transport_assignee_name", "运输AssigneeName", "运输人姓名"], ""),
        "department": _pick_value(order, ["department", "部门"], ""),
        "remark": _pick_value(order, ["remark", "备注"], ""),
        "target_location_text": _pick_value(order, ["target_location_text", "目标位置文本"], ""),
        "created_at": _pick_value(order, ["created_at", "创建时间"]),
        "submitted_at": _pick_value(order, ["submit_time", "submitted_at", "提交时间"]),
        "tool_count": tool_count,
        "approved_count": approved_count,
        "items": normalized_items,
        "notification_records": order.get("notification_records", []) or [],
    }


def _extract_order_values(record: Dict) -> Dict:
    return {
        "order_no": _pick_value(record, [ORDER_COLUMNS["order_no"], "order_no"], ""),
        "order_type": _pick_value(record, [ORDER_COLUMNS["order_type"], "order_type"], ""),
        "order_status": _pick_value(record, [ORDER_COLUMNS["order_status"], "order_status"], ""),
        "initiator_name": _pick_value(record, [ORDER_COLUMNS["initiator_name"], "initiator_name"], ""),
        "initiator_id": _pick_value(record, [ORDER_COLUMNS["initiator_id"], "initiator_id"], ""),
        "department": _pick_value(record, [ORDER_COLUMNS["department"], "department"], ""),
        "required_by": _pick_value(
            record,
            ["required_by", ORDER_COLUMNS["planned_use_time"], ORDER_COLUMNS["planned_return_time"]],
            "",
        ),
        "remark": _pick_value(record, [ORDER_COLUMNS["remark"], "remark"], ""),
        "created_at": _pick_value(record, [ORDER_COLUMNS["created_at"], "created_at"]),
        "submitted_at": _pick_value(record, ["submit_time", "submitted_at"]),
        "transport_type": _pick_value(record, [ORDER_COLUMNS["transport_type"], "transport_type"], ""),
        "transport_assignee_name": _pick_value(
            record,
            [ORDER_COLUMNS["transport_assignee_name"], "transport_assignee_name", "receiver"],
            "",
        ),
        "keeper_name": _pick_value(record, [ORDER_COLUMNS["keeper_name"], "keeper_name"], ""),
        "transport_receiver": _pick_value(
            record,
            ["receiver", ORDER_COLUMNS["transport_assignee_name"], "transport_assignee_name"],
            "",
        ),
    }


def _evaluate_final_confirm_availability(order: Dict, operator_id: str, operator_role: str) -> Dict:
    current_status = order.get("order_status") or ""
    order_type = order.get("order_type") or ""
    allowed_statuses = {"transport_notified", "transport_completed", "final_confirmation_pending"}

    if current_status == "completed":
        return {
            "available": False,
            "reason": "order is already completed",
            "order_type": order_type,
            "current_status": current_status,
            "expected_role": "initiator" if order_type == "outbound" else "keeper",
        }

    if current_status not in allowed_statuses:
        return {
            "available": False,
            "reason": f"current status does not allow final confirmation: {current_status}",
            "order_type": order_type,
            "current_status": current_status,
            "expected_role": "initiator" if order_type == "outbound" else "keeper",
        }

    expected_role = "initiator" if order_type == "outbound" else "keeper" if order_type == "inbound" else ""
    if not expected_role:
        return {
            "available": False,
            "reason": f"unsupported order type: {order_type or '-'}",
            "order_type": order_type,
            "current_status": current_status,
            "expected_role": "",
        }

    if operator_role and operator_role != expected_role:
        return {
            "available": False,
            "reason": f"final confirmation requires role {expected_role}",
            "order_type": order_type,
            "current_status": current_status,
            "expected_role": expected_role,
        }

    if operator_id:
        owner_key = "initiator_id" if order_type == "outbound" else "keeper_id"
        owner_value = order.get(owner_key)
        if owner_value and owner_value != operator_id:
            return {
                "available": False,
                "reason": f"operator does not match the assigned {expected_role}",
                "order_type": order_type,
                "current_status": current_status,
                "expected_role": expected_role,
            }

    return {
        "available": True,
        "reason": "",
        "order_type": order_type,
        "current_status": current_status,
        "expected_role": expected_role,
    }


def _extract_item_values(item: Dict) -> Dict:
    return {
        "serial_no": _pick_value(item, [ITEM_COLUMNS["serial_no"], "serial_no", "tool_code"], ""),
        "tool_name": _pick_value(item, [ITEM_COLUMNS["tool_name"], "tool_name"], ""),
        "drawing_no": _pick_value(item, [ITEM_COLUMNS["drawing_no"], "drawing_no"], ""),
        "location_text": _pick_value(
            item,
            ["location_text", ITEM_COLUMNS["keeper_confirm_location_text"], ITEM_COLUMNS["tool_snapshot_location_text"]],
            "",
        ),
        "apply_qty": _pick_value(item, [ITEM_COLUMNS["apply_qty"], "apply_qty"], 1),
        "approved_qty": _pick_value(item, ["approved_qty", ITEM_COLUMNS["confirmed_qty"], "confirmed_qty"], 0),
        "split_quantity": _pick_value(item, ["split_quantity"], 0),
        "item_status": _pick_value(item, [ITEM_COLUMNS["item_status"], "item_status", "status"], ""),
    }
