# -*- coding: utf-8 -*-
"""
Service wrappers for Tool IO backend flows.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from database import (
    DatabaseManager,
    cancel_tool_io_order,
    create_tool_io_order,
    ensure_tool_io_tables,
    final_confirm_order,
    get_tool_io_orders,
    reject_tool_io_order,
    search_tools,
    submit_tool_io_order,
)
from backend.services.audit_log_service import (
    OPERATION_KEEPER_CONFIRM,
    OPERATION_TRANSPORT_ASSIGN,
    OPERATION_TRANSPORT_COMPLETE,
    OPERATION_TRANSPORT_START,
    OPERATION_TRANSPORT_NOTIFY,
    write_order_audit_log,
)
from backend.services.feishu_notification_adapter import auto_deliver_notification, deliver_notification_to_feishu
from backend.services.notification_service import (
    KEEPER_CONFIRM_REQUIRED,
    ORDER_CANCELLED,
    ORDER_COMPLETED,
    ORDER_CREATED,
    ORDER_REJECTED,
    ORDER_SUBMITTED,
    TRANSPORT_COMPLETED,
    TRANSPORT_REQUIRED,
    TRANSPORT_STARTED,
    create_internal_order_notification,
    create_notification_record,
    list_notifications_by_order,
    list_notifications_for_user,
    mark_notification_as_read,
)
from backend.services.rbac_data_scope_service import (
    build_order_scope_sql,
    order_matches_scope,
    resolve_order_data_scope,
)
from backend.services.tool_location_service import apply_order_location_updates
from backend.services.tool_io_runtime import (
    get_order_detail_runtime,
    get_order_logs_runtime,
    keeper_confirm_runtime,
    list_pending_keeper_orders,
)

logger = logging.getLogger(__name__)


def _build_actor_context(
    payload: Dict,
    *,
    actor_id_key: str = "operator_id",
    actor_name_key: str = "operator_name",
    actor_role_key: str = "operator_role",
) -> Dict:
    return {
        "user_id": payload.get(actor_id_key, ""),
        "user_name": payload.get(actor_name_key, ""),
        "user_role": payload.get(actor_role_key, ""),
    }


def _emit_internal_notification(
    notification_type: str,
    *,
    order: Dict,
    actor: Optional[Dict] = None,
    target_user_id: str = "",
    target_user_name: str = "",
    target_role: str = "",
    metadata: Optional[Dict] = None,
) -> None:
    result = create_internal_order_notification(
        notification_type,
        order=order,
        target_user_id=target_user_id,
        target_user_name=target_user_name,
        target_role=target_role,
        actor=actor,
        metadata=metadata,
    )
    if not result.get("success"):
        logger.warning(
            "failed to create internal notification for %s (%s): %s",
            order.get("order_no", ""),
            notification_type,
            result.get("error", "unknown notification error"),
        )
        return
    delivery_result = auto_deliver_notification(
        {
            "notification_id": result.get("notification_id", 0),
            "order_no": order.get("order_no", ""),
            "notification_type": notification_type,
            "receiver": result.get("receiver", ""),
            "title": result.get("title", ""),
            "body": result.get("body", ""),
            "copy_text": result.get("copy_text", ""),
        }
    )
    if delivery_result.get("send_status") in {"failed", "disabled"}:
        logger.warning(
            "Feishu auto delivery did not complete for %s (%s): %s",
            order.get("order_no", ""),
            notification_type,
            delivery_result.get("send_result") or delivery_result.get("response_summary", ""),
        )


def create_order(payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    ensure_tool_io_tables()
    current_org = (current_user or {}).get("current_org") or {}
    default_org = (current_user or {}).get("default_org") or {}
    current_org_id = str(current_org.get("org_id", "")).strip()
    default_org_id = str(default_org.get("org_id", "") or (current_user or {}).get("default_org_id", "")).strip()
    payload = {**payload}
    payload["org_id"] = payload.get("org_id") or current_org_id or default_org_id
    result = create_tool_io_order(payload)
    if result.get("success"):
        order_no = result.get("order_no", "")
        actor = _build_actor_context(payload, actor_id_key="initiator_id", actor_name_key="initiator_name", actor_role_key="initiator_role")
        order = get_order_detail(order_no, current_user=current_user) if order_no else {}
        if order:
            _emit_internal_notification(
                ORDER_CREATED,
                order=order,
                actor=actor,
                target_user_id=payload.get("initiator_id", ""),
                target_user_name=payload.get("initiator_name", ""),
                target_role=payload.get("initiator_role", "initiator"),
                metadata={"trigger": "create_order"},
            )
    return result


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


def _order_not_found_response() -> Dict:
    return {"success": False, "error": "order not found"}


def _is_order_accessible(order: Dict, current_user: Optional[Dict]) -> bool:
    if not current_user:
        return True
    return order_matches_scope(order, _resolve_scope_context(current_user))


def list_orders(filters: Dict, current_user: Optional[Dict] = None) -> Dict:
    raw_result = get_tool_io_orders(
        order_type=filters.get("order_type"),
        status=filters.get("order_status"),
        applicant_id=filters.get("initiator_id"),
        keeper_id=filters.get("keeper_id"),
        keyword=filters.get("keyword"),
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
        page=1,
        page_size=5000,
    )
    if not raw_result.get("success", True):
        return raw_result

    scoped_orders = [
        order for order in (raw_result.get("data") or []) if _is_order_accessible(order, current_user)
    ]
    page_no = int(filters.get("page_no", 1) or 1)
    page_size = int(filters.get("page_size", 20) or 20)
    start = max(page_no - 1, 0) * page_size
    end = start + page_size
    return {
        "success": True,
        "data": scoped_orders[start:end],
        "total": len(scoped_orders),
        "page_no": page_no,
        "page_size": page_size,
    }


def get_dashboard_stats(current_user: Optional[Dict] = None) -> Dict:
    """Return dashboard metrics without depending on a missing database export."""
    all_orders_result = get_tool_io_orders(page=1, page_size=5000)
    scoped_orders = [
        order for order in (all_orders_result.get("data") or []) if _is_order_accessible(order, current_user)
    ]

    def _count(*, order_status: str = "") -> int:
        return sum(1 for order in scoped_orders if (order.get("order_status") or "") == order_status)

    data = {
        "today_outbound_orders": 0,
        "today_inbound_orders": 0,
        "orders_pending_keeper_confirmation": _count(order_status="submitted") + _count(order_status="partially_confirmed"),
        "orders_in_transport": _count(order_status="transport_notified") + _count(order_status="transport_in_progress"),
        "orders_pending_final_confirmation": _count(order_status="transport_completed") + _count(order_status="final_confirmation_pending"),
        "active_orders_total": (
            _count(order_status="draft")
            + _count(order_status="submitted")
            + _count(order_status="keeper_confirmed")
            + _count(order_status="partially_confirmed")
            + _count(order_status="transport_notified")
            + _count(order_status="transport_in_progress")
            + _count(order_status="transport_completed")
            + _count(order_status="final_confirmation_pending")
        ),
    }
    return {"success": True, "data": data}


def get_order_detail(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    order = _normalize_runtime_order(get_order_detail_runtime(order_no))
    if not order or not _is_order_accessible(order, current_user):
        return {}
    return order


def submit_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()
    result = submit_tool_io_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )
    if result.get("success"):
        actor = _build_actor_context(payload)
        order = get_order_detail(order_no, current_user=current_user)
        if order:
            _emit_internal_notification(
                ORDER_SUBMITTED,
                order=order,
                actor=actor,
                target_user_id=order.get("initiator_id", ""),
                target_user_name=order.get("initiator_name", ""),
                target_role="initiator",
                metadata={"trigger": "submit_order"},
            )
            _emit_internal_notification(
                KEEPER_CONFIRM_REQUIRED,
                order=order,
                actor=actor,
                target_user_id=order.get("keeper_id", ""),
                target_user_name=order.get("keeper_name", ""),
                target_role="keeper",
                metadata={"required_action": "keeper_confirm"},
            )
    return result


def keeper_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()
    confirm_data = {
        "transport_type": payload.get("transport_type"),
        "transport_assignee_id": payload.get("transport_assignee_id"),
        "transport_assignee_name": payload.get("transport_assignee_name"),
        "keeper_remark": payload.get("keeper_remark"),
        "items": payload.get("items"),
    }
    result = keeper_confirm_runtime(
        order_no=order_no,
        keeper_id=payload.get("keeper_id", ""),
        keeper_name=payload.get("keeper_name", ""),
        confirm_data=confirm_data,
        operator_id=payload.get("operator_id", payload.get("keeper_id", "")),
        operator_name=payload.get("operator_name", payload.get("keeper_name", "")),
        operator_role=payload.get("operator_role", "keeper"),
    )
    if result.get("success"):
        approved_count = result.get("approved_count", 0)
        total_count = len(confirm_data.get("items") or [])
        keeper_remark = result.get("keeper_remark") or payload.get("keeper_remark", "")
        actor = _build_actor_context(payload)
        remark = f"keeper confirmed {approved_count}/{total_count} items"
        if keeper_remark:
            remark = f"{remark}; remark: {keeper_remark}"
        write_order_audit_log(
            order_no=order_no,
            operation_type=OPERATION_KEEPER_CONFIRM,
            operator_user_id=actor["user_id"],
            operator_name=actor["user_name"],
            operator_role=actor["user_role"],
            previous_status=result.get("before_status", ""),
            new_status=result.get("after_status", result.get("status", "")),
            remark=remark,
        )
        order = get_order_detail(order_no, current_user=current_user)
        if order:
            _emit_internal_notification(
                TRANSPORT_REQUIRED,
                order=order,
                actor=actor,
                target_user_id=order.get("transport_assignee_id", ""),
                target_user_name=order.get("transport_assignee_name", ""),
                target_role="transport_operator",
                metadata={"required_action": "transport"},
            )
    return result


def final_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    availability = get_final_confirm_availability(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_role", ""),
        current_user=current_user,
    )
    if not availability.get("success"):
        return availability
    if not availability.get("available"):
        return {"success": False, "error": availability.get("reason") or "final confirmation is not available"}

    result = final_confirm_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )
    if not result.get("success"):
        return result

    detail = get_order_detail(order_no, current_user=current_user)
    actor = _build_actor_context(payload)
    if detail:
        apply_order_location_updates(
            order=detail,
            milestone="final_confirm",
            operator_user_id=actor["user_id"],
            operator_name=actor["user_name"],
            operator_role=actor["user_role"],
        )
        target_user_id = detail.get("initiator_id", "") if availability.get("order_type") == "outbound" else detail.get("keeper_id", "")
        target_user_name = detail.get("initiator_name", "") if availability.get("order_type") == "outbound" else detail.get("keeper_name", "")
        target_role = "initiator" if availability.get("order_type") == "outbound" else "keeper"
        _emit_internal_notification(
            ORDER_COMPLETED,
            order=detail,
            actor=actor,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            target_role=target_role,
            metadata={"trigger": "final_confirm"},
        )
    return {
        **result,
        "available": False,
        "data": detail,
        "order_type": availability.get("order_type"),
        "before_status": availability.get("current_status"),
        "after_status": "completed",
    }


def get_final_confirm_availability(
    order_no: str,
    operator_id: str = "",
    operator_role: str = "",
    current_user: Optional[Dict] = None,
) -> Dict:
    order = _get_runtime_order_summary(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found", "available": False}

    availability = _evaluate_final_confirm_availability(order, operator_id, operator_role)
    return {"success": True, **availability}


def assign_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return _order_not_found_response()

    current_status = _pick_value(order, ["order_status"], "")
    if current_status not in {"keeper_confirmed", "partially_confirmed", "transport_notified", "transport_in_progress"}:
        return {"success": False, "error": f"current status does not allow transport assignment: {current_status}"}

    transport_assignee_id = payload.get("transport_assignee_id", "")
    transport_assignee_name = payload.get("transport_assignee_name", "")
    if not transport_assignee_id and not transport_assignee_name:
        return {"success": False, "error": "transport assignee is required"}

    DatabaseManager().execute_query(
        """
        UPDATE 工装出入库单_主表
        SET 运输人ID = ?,
            运输人姓名 = ?,
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """,
        (transport_assignee_id, transport_assignee_name, order_no),
        fetch=False,
    )
    actor = _build_actor_context(payload)
    write_order_audit_log(
        order_no=order_no,
        operation_type=OPERATION_TRANSPORT_ASSIGN,
        operator_user_id=actor["user_id"],
        operator_name=actor["user_name"],
        operator_role=actor["user_role"],
        previous_status=current_status,
        new_status=current_status,
        remark=f"transport assigned to {transport_assignee_name or transport_assignee_id}",
    )
    updated_order = get_order_detail_runtime(order_no)
    if updated_order:
        _emit_internal_notification(
            TRANSPORT_REQUIRED,
            order=updated_order,
            actor=actor,
            target_user_id=transport_assignee_id,
            target_user_name=transport_assignee_name,
            target_role="transport_operator",
            metadata={"required_action": "transport", "trigger": "assign_transport"},
        )
    return {"success": True, "data": updated_order}


def start_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return _order_not_found_response()

    current_status = _pick_value(order, ["order_status"], "")
    if current_status not in {"keeper_confirmed", "partially_confirmed", "transport_notified"}:
        return {"success": False, "error": f"current status does not allow transport start: {current_status}"}

    actor = _build_actor_context(payload)
    DatabaseManager().execute_query(
        """
        UPDATE 工装出入库单_主表
        SET 单据状态 = 'transport_in_progress',
            运输人ID = COALESCE(NULLIF(?, ''), 运输人ID),
            运输人姓名 = COALESCE(NULLIF(?, ''), 运输人姓名),
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """,
        (payload.get("operator_id", ""), payload.get("operator_name", ""), order_no),
        fetch=False,
    )
    write_order_audit_log(
        order_no=order_no,
        operation_type=OPERATION_TRANSPORT_START,
        operator_user_id=actor["user_id"],
        operator_name=actor["user_name"],
        operator_role=actor["user_role"],
        previous_status=current_status,
        new_status="transport_in_progress",
        remark="transport started",
    )
    updated_order = get_order_detail_runtime(order_no)
    if updated_order:
        target_user_id = updated_order.get("initiator_id", "") if updated_order.get("order_type") == "outbound" else updated_order.get("keeper_id", "")
        target_user_name = updated_order.get("initiator_name", "") if updated_order.get("order_type") == "outbound" else updated_order.get("keeper_name", "")
        target_role = "initiator" if updated_order.get("order_type") == "outbound" else "keeper"
        _emit_internal_notification(
            TRANSPORT_STARTED,
            order=updated_order,
            actor=actor,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            target_role=target_role,
            metadata={"trigger": "start_transport"},
        )
    return {"success": True, "data": updated_order, "before_status": current_status, "after_status": "transport_in_progress"}


def complete_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return _order_not_found_response()

    current_status = _pick_value(order, ["order_status"], "")
    if current_status not in {"transport_in_progress", "transport_notified"}:
        return {"success": False, "error": f"current status does not allow transport completion: {current_status}"}

    actor = _build_actor_context(payload)
    DatabaseManager().execute_query(
        """
        UPDATE 工装出入库单_主表
        SET 单据状态 = 'transport_completed',
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """,
        (order_no,),
        fetch=False,
    )
    write_order_audit_log(
        order_no=order_no,
        operation_type=OPERATION_TRANSPORT_COMPLETE,
        operator_user_id=actor["user_id"],
        operator_name=actor["user_name"],
        operator_role=actor["user_role"],
        previous_status=current_status,
        new_status="transport_completed",
        remark="transport completed",
    )
    updated_order = get_order_detail_runtime(order_no)
    if updated_order:
        apply_order_location_updates(
            order=updated_order,
            milestone="transport_complete",
            operator_user_id=actor["user_id"],
            operator_name=actor["user_name"],
            operator_role=actor["user_role"],
        )
        target_user_id = updated_order.get("initiator_id", "") if updated_order.get("order_type") == "outbound" else updated_order.get("keeper_id", "")
        target_user_name = updated_order.get("initiator_name", "") if updated_order.get("order_type") == "outbound" else updated_order.get("keeper_name", "")
        target_role = "initiator" if updated_order.get("order_type") == "outbound" else "keeper"
        _emit_internal_notification(
            TRANSPORT_COMPLETED,
            order=updated_order,
            actor=actor,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            target_role=target_role,
            metadata={"trigger": "complete_transport", "next_action": "final_confirm"},
        )
    return {"success": True, "data": updated_order, "before_status": current_status, "after_status": "transport_completed"}


def reject_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()
    result = reject_tool_io_order(
        order_no,
        payload.get("reject_reason", ""),
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )
    if result.get("success"):
        actor = _build_actor_context(payload)
        order = get_order_detail_runtime(order_no)
        if order:
            _emit_internal_notification(
                ORDER_REJECTED,
                order=order,
                actor=actor,
                target_user_id=order.get("initiator_id", ""),
                target_user_name=order.get("initiator_name", ""),
                target_role="initiator",
                metadata={"reject_reason": payload.get("reject_reason", "")},
            )
    return result


def cancel_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()
    result = cancel_tool_io_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )
    if result.get("success"):
        actor = _build_actor_context(payload)
        order = get_order_detail_runtime(order_no)
        if order:
            _emit_internal_notification(
                ORDER_CANCELLED,
                order=order,
                actor=actor,
                target_user_id=order.get("initiator_id", ""),
                target_user_name=order.get("initiator_name", ""),
                target_role="initiator",
                metadata={"trigger": "cancel_order"},
            )
    return result


def get_order_logs(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()
    return {"success": True, "data": get_order_logs_runtime(order_no)}


def get_pending_keeper_list(keeper_id: str = None, current_user: Optional[Dict] = None) -> List[Dict]:
    scope_context = _resolve_scope_context(current_user)
    return [order for order in list_pending_keeper_orders(keeper_id) if order_matches_scope(order, scope_context)]


def get_notification_records(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found", "data": []}
    return list_notifications_by_order(order_no)


def get_current_user_notifications(filters: Dict, current_user: Optional[Dict] = None) -> Dict:
    if not current_user:
        return {"success": False, "error": "authentication required", "data": []}
    return list_notifications_for_user(
        current_user,
        page_no=filters.get("page_no", 1),
        page_size=filters.get("page_size", 20),
        status=filters.get("status", ""),
    )


def mark_current_user_notification_read(notification_id: int, current_user: Optional[Dict] = None) -> Dict:
    if not current_user:
        return {"success": False, "error": "authentication required"}
    return mark_notification_as_read(notification_id, current_user)


def _pick_value(record: Dict, keys: List[str], default: Optional[str] = ""):
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default


def _normalize_runtime_order(order: Dict) -> Dict:
    if not order:
        return {}

    normalized_items = []
    for item in order.get("items", []) or []:
        normalized_items.append(
            {
                **item,
                "tool_code": _pick_value(item, ["tool_code", "序列号", "工装编码"], ""),
                "tool_name": _pick_value(item, ["tool_name", "工装名称"], ""),
                "drawing_no": _pick_value(item, ["drawing_no", "工装图号"], ""),
                "spec_model": _pick_value(item, ["spec_model", "机型", "规格型号"], ""),
                "location_text": _pick_value(item, ["location_text", "保管员确认位置文本", "工装快照位置文本"], ""),
                "apply_qty": _pick_value(item, ["apply_qty", "申请数量"], 1),
                "approved_qty": _pick_value(item, ["approved_qty", "确认数量"], 0),
                "item_status": _pick_value(item, ["item_status", "status", "明细状态"], ""),
            }
        )

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
        "transport_assignee_id": _pick_value(order, ["transport_assignee_id", "运输人ID"], ""),
        "transport_assignee_name": _pick_value(order, ["transport_assignee_name", "运输人姓名"], ""),
        "department": _pick_value(order, ["department", "部门"], ""),
        "remark": _pick_value(order, ["remark", "备注"], ""),
        "target_location_text": _pick_value(order, ["target_location_text", "目标位置文本"], ""),
        "created_at": _pick_value(order, ["created_at", "创建时间"]),
        "submitted_at": _pick_value(order, ["submit_time", "submitted_at", "提交时间"]),
        "items": normalized_items,
        "notification_records": order.get("notification_records", []) or [],
    }


def _get_runtime_order_summary(order_no: str, current_user: Optional[Dict] = None) -> Optional[Dict]:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return None

    return {
        "order_no": _pick_value(order, ["order_no", "é—å‘ŠåžµéŽ¼î‚¦å´£é¡æ¨»å„Ÿé–¹æƒ§å•¿ç»€å¬®æŸ›?"], order_no),
        "order_type": _pick_value(order, ["order_type", "é—å‘Šîš†å¨²æ¨ºç•µæµ£è™¹å°µé å›ªå°™éˆ§?"]),
        "order_status": _pick_value(order, ["order_status", "é—å‘Šîš†å¨²æ¨ºç•µæ¸šâ‚¬éŽ®â•…æ‡œçº°æ¨ºäº¾?"]),
        "initiator_id": _pick_value(order, ["initiator_id", "é—å‘Šç‘¦é¨å¥¸å¹‘é”å—™î›²ç¼â„ƒå¢¬"]),
        "keeper_id": _pick_value(order, ["keeper_id", "æ¿žï½…æ´¦ç»»å‹¯î”˜éŽ¼ä½¸å·æ¿¡ã‚‡æ‹"]),
        "transport_assignee_id": _pick_value(order, ["transport_assignee_id", "杩愯緭浜篒D"]),
        "approved_count": _pick_value(order, ["approved_count", "éŽè§„ç“•çæ¬“åž¾å¦¯å…¼åª¼é–µå æ£™å¨ˆå •æ¢º?"], 0),
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


def _create_notification_record(
    *,
    order_no: str,
    notify_type: str,
    notify_channel: str,
    receiver: str,
    title: str,
    content: str,
    copy_text: str = "",
) -> int:
    if not content:
        return 0
    status = "pending" if notify_channel != "internal" else "unread"
    result = create_notification_record(
        order_no=order_no,
        notification_type=notify_type,
        notify_channel=notify_channel,
        receiver=receiver,
        title=title,
        body=content,
        copy_text=copy_text,
        status=status,
    )
    return int(result.get("notification_id", 0)) if result.get("success") else 0


def search_tool_inventory(filters: Dict) -> Dict:
    return search_tools(
        keyword=filters.get("keyword"),
        status=filters.get("status"),
        location_id=filters.get("location") or filters.get("location_id"),
        page_no=filters.get("page_no", 1),
        page_size=filters.get("page_size", 20),
    )


def batch_query_tools(tool_codes: List[str]) -> Dict:
    cleaned_codes = [code.strip() for code in tool_codes if isinstance(code, str) and code.strip()]
    if not cleaned_codes:
        return {"success": False, "error": "tool_codes must contain at least one code", "data": []}

    placeholders = ",".join(["?"] * len(cleaned_codes))
    sql = f"""
    SELECT
        [æ´å¿“åžªé™ç©„] as tool_code,
        [æ´å¿“åžªé™ç©„] as tool_id,
        [å®¸ãƒ¨î—Šé¥æƒ§å½¿] as drawing_no,
        [å®¸ãƒ¨î—Šéšå¶‡Ðž] as tool_name,
        [éˆå“„ç€·] as spec_model,
        [è¤°æ’³å¢ é—å Ÿî‚¼] as current_version,
        [æ´æ’²ç¶…] as current_location_text,
        [æ´æ—‚æ•¤é˜å——å½¶] as application_history,
        [é™îˆœæ•¤é˜èˆµâ‚¬ä¹š] as available_status,
        [å®¸ãƒ¨î—Šéˆå¤‹æ™¥é˜èˆµâ‚¬ä¹š] as valid_status,
        [é‘å“„å†æ´æ’¶å§¸éŽ¬ä¹š] as io_status,
        COALESCE(
            [é‘å“„å†æ´æ’¶å§¸éŽ¬ä¹š],
            [é™îˆœæ•¤é˜èˆµâ‚¬ä¹š],
            [å®¸ãƒ¨î—Šéˆå¤‹æ™¥é˜èˆµâ‚¬ä¹š],
            ''
        ) as status_text
    FROM [å®¸ãƒ¨î—ŠéŸ¬î‚¡å”¤é—î“¥æ¶“æ˜ã€ƒ]
    WHERE [æ´å¿“åžªé™ç©„] IN ({placeholders})
    ORDER BY [æ´å¿“åžªé™ç©„]
    """
    rows = DatabaseManager().execute_query(sql, tuple(cleaned_codes))
    return {"success": True, "data": rows}


def _format_order_datetime(value) -> str:
    if value is None:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _extract_order_values(record: Dict) -> Dict:
    return {
        "order_no": _pick_value(record, ["order_no", "é‘å“„å†æ´æ’³å´Ÿé™?"], ""),
        "order_type": _pick_value(record, ["order_type", "é—å‘Šîš†å¨²æ¨ºç•µæµ£è™¹å°µé å›ªå°™éˆ§?"], ""),
        "order_status": _pick_value(record, ["order_status", "é—æ›Ÿåµé˜èˆµâ‚¬?"], ""),
        "initiator_name": _pick_value(record, ["initiator_name", "é™æˆ£æ£æµœå“„î˜éš?"], ""),
        "initiator_id": _pick_value(record, ["initiator_id", "é—å‘Šç‘¦é¨å¥¸å¹‘é”å—™î›²ç¼â„ƒå¢¬"], ""),
        "department": _pick_value(record, ["department", "é–®ã„©æ£¬"], ""),
        "required_by": _pick_value(record, ["required_by", "æ¤¤åœ­æ´°æµ ï½…å½¿"], ""),
        "remark": _pick_value(record, ["remark", "é¢ã„©â‚¬?"], ""),
        "created_at": _pick_value(record, ["created_at", "ç’â€³åžæµ£è·¨æ•¤éƒå •æ£¿"]),
        "submitted_at": _pick_value(record, ["submit_time", "ç’â€³åžè¤°æŽ•ç¹•éƒå •æ£¿"]),
        "transport_type": _pick_value(record, ["transport_type", "æ©æ„¯ç·­ç»«è¯²ç€·"], ""),
        "transport_assignee_name": _pick_value(record, ["transport_assignee_name", "é©î†½çˆ£æµ£å¶‡ç–†é‚å›¨æ¹°"], ""),
        "keeper_name": _pick_value(record, ["keeper_name", "æ·‡æ¿ˆî…¸é›æ¨ºî˜éš?"], ""),
        "transport_receiver": _pick_value(record, ["receiver", "æ©æ„¯ç·­æµœå“„î˜éš?"], ""),
    }


def _extract_item_values(item: Dict) -> Dict:
    return {
        "tool_code": _pick_value(item, ["tool_code", "å®¸ãƒ¨î—Šç¼‚æ «çˆœ"], ""),
        "tool_name": _pick_value(item, ["tool_name", "å®¸ãƒ¨î—Šéšå¶‡Ðž"], ""),
        "drawing_no": _pick_value(item, ["drawing_no", "å®¸ãƒ¨î—Šé¥æƒ§å½¿"], ""),
        "location_text": _pick_value(item, ["location_text", "æ·‡æ¿ˆî…¸é›æ¨¼â€˜ç’ã‚„ç¶…ç¼ƒî†½æžƒéˆ?"], ""),
        "apply_qty": _pick_value(item, ["apply_qty", "é¢å® î‡¬éä¼´å™º"], 1),
        "approved_qty": _pick_value(item, ["approved_qty", "çº­î†¿î…»éä¼´å™º"], 0),
        "item_status": _pick_value(item, ["item_status", "status", "é„åº£ç²é˜èˆµâ‚¬?"], ""),
    }


def generate_keeper_text(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    summary = _extract_order_values(order)
    items = [_extract_item_values(item) for item in order.get("items", [])]
    order_label = "Outbound" if summary["order_type"] == "outbound" else "Inbound"
    items_text = "\n".join(
        [
            f"{idx + 1}. {item['tool_code']} / {item['tool_name'] or '-'} / drawing {item['drawing_no'] or '-'} / qty {item['apply_qty'] or 1}"
            for idx, item in enumerate(items)
        ]
    ) or "- No items"

    text = (
        f"Keeper request for {order_label} order\n"
        f"Order No: {summary['order_no'] or order_no}\n"
        f"Initiator: {summary['initiator_name'] or '-'} ({summary['initiator_id'] or '-'})\n"
        f"Department: {summary['department'] or '-'}\n"
        f"Required By: {summary['required_by'] or '-'}\n"
        f"Remark: {summary['remark'] or '-'}\n"
        f"Created At: {_format_order_datetime(summary['created_at'])}\n"
        f"Submitted At: {_format_order_datetime(summary['submitted_at'])}\n\n"
        f"Requested Items:\n{items_text}\n\n"
        "Please review the order and complete keeper confirmation."
    )
    DatabaseManager().execute_query(
        """
        UPDATE 工装出入库单_主表
        SET 保管员需求文本 = ?,
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """,
        (text, order_no),
        fetch=False,
    )
    _create_notification_record(
        order_no=order_no,
        notify_type="keeper_request",
        notify_channel="internal",
        receiver="",
        title="Keeper request message",
        content=text,
    )
    return {"success": True, "text": text}


def generate_transport_text(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    approved_items = [
        _extract_item_values(item)
        for item in order.get("items", [])
        if _pick_value(item, ["item_status", "status", "é„åº£ç²é˜èˆµâ‚¬?"], "") == "approved"
    ]
    if not approved_items:
        return {"success": False, "error": "no approved items are available for transport preparation"}

    summary = _extract_order_values(order)
    items_text = "\n".join(
        [
            f"{idx + 1}. {item['location_text'] or '-'} / {item['tool_name'] or '-'} / {item['tool_code']} / qty {item['approved_qty'] or 1}"
            for idx, item in enumerate(approved_items)
        ]
    )
    transport_type = summary["transport_type"] or "-"
    text = (
        f"Transport preparation notice\n"
        f"Order No: {summary['order_no'] or order_no}\n"
        f"Transport Type: {transport_type}\n"
        f"Initiator: {summary['initiator_name'] or '-'}\n"
        f"Transport Assignee: {summary['transport_assignee_name'] or '-'}\n\n"
        f"Approved Items:\n{items_text}\n\n"
        "Please arrange transport based on the confirmed tool list."
    )
    wechat_text = (
        f"Tool transport notice\n"
        f"Order No: {summary['order_no'] or order_no}\n"
        f"Transport Type: {transport_type}\n\n"
        f"Pickup Location: {approved_items[0]['location_text'] or '-'}\n"
        f"Receiver: {summary['transport_assignee_name'] or '-'}\n\n"
        + "\n".join([f"- {item['tool_code']} ({item['tool_name'] or '-'})" for item in approved_items])
        + f"\n\nRequested By: {summary['initiator_name'] or '-'} / {summary['keeper_name'] or '-'}"
    )
    DatabaseManager().execute_query(
        """
        UPDATE 工装出入库单_主表
        SET 运输通知文本 = ?,
            微信复制文本 = ?,
            修改时间 = GETDATE()
        WHERE 出入库单号 = ?
        """,
        (text, wechat_text, order_no),
        fetch=False,
    )
    _create_notification_record(
        order_no=order_no,
        notify_type="transport_preview",
        notify_channel="internal",
        receiver="",
        title="Transport preview message",
        content=text,
        copy_text=wechat_text,
    )
    return {"success": True, "text": text, "wechat_text": wechat_text}


def notify_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    current_status = _pick_value(order, ["order_status", "é—æ›Ÿåµé˜èˆµâ‚¬?"], "")
    if current_status not in {"keeper_confirmed", "partially_confirmed", "transport_notified"}:
        return {
            "success": False,
            "error": f"current status does not allow transport notification: {current_status}",
        }

    generated = generate_transport_text(order_no, current_user=current_user)
    if not generated.get("success"):
        return generated

    summary = _extract_order_values(order)
    notify_type = payload.get("notify_type", "transport_notice")
    notify_channel = payload.get("notify_channel", "feishu")
    receiver = payload.get("receiver") or summary["transport_receiver"]
    title = payload.get("title") or "Transport notification"
    content = payload.get("content") or generated["text"]
    copy_text = payload.get("copy_text") or generated["wechat_text"]

    delivery_result = deliver_notification_to_feishu(
        {
            "order_no": order_no,
            "notification_type": notify_type,
            "receiver": receiver,
            "title": title,
            "body": content,
            "copy_text": copy_text,
        }
    )
    notify_id = int(delivery_result.get("notification_id", 0))
    if not notify_id:
        return {"success": False, "error": "failed to create notification record"}

    feishu_sent = bool(delivery_result.get("success"))
    final_status = delivery_result.get("send_status", "failed")
    send_result = delivery_result.get("send_result", "")

    if not feishu_sent:
        write_order_audit_log(
            order_no=order_no,
            operation_type=OPERATION_TRANSPORT_NOTIFY,
            operator_user_id=payload.get("operator_id", ""),
            operator_name=payload.get("operator_name", summary["keeper_name"]),
            operator_role=payload.get("operator_role", "keeper"),
            previous_status=current_status,
            new_status=current_status,
            remark=f"transport notification failed, channel: {notify_channel}, status: {final_status}",
        )
        return {
            "success": False,
            "error": send_result,
            "notify_id": notify_id,
            "send_status": final_status,
            "send_result": send_result,
            "wechat_text": copy_text,
        }

    DatabaseManager().execute_query(
        """
        UPDATE å®¸ãƒ¨î—Šé‘å“„å†æ´æ’³å´Ÿ_æ¶“æ˜ã€ƒ
        SET é—æ›Ÿåµé˜èˆµâ‚¬? = 'transport_notified',
            æ©æ„¯ç·­é–«æ°±ç…¡éƒå •æ£¿ = GETDATE(),
            æ©æ„¯ç·­é–«æ°±ç…¡é‚å›¨æ¹° = ?,
            å¯°î†»ä¿Šæ¾¶å¶…åŸ—é‚å›¨æ¹° = ?,
            æ·‡î†½æ•¼éƒå •æ£¿ = GETDATE()
        WHERE é‘å“„å†æ´æ’³å´Ÿé™? = ?
        """,
        (content, copy_text, order_no),
        fetch=False,
    )
    write_order_audit_log(
        order_no=order_no,
        operation_type=OPERATION_TRANSPORT_NOTIFY,
        operator_user_id=payload.get("operator_id", ""),
        operator_name=payload.get("operator_name", summary["keeper_name"]),
        operator_role=payload.get("operator_role", "keeper"),
        previous_status=current_status,
        new_status="transport_notified",
        remark=f"transport notification sent, channel: {notify_channel}, status: {final_status}",
    )
    return {
        "success": True,
        "notify_id": notify_id,
        "send_status": final_status,
        "send_result": send_result,
        "wechat_text": copy_text,
    }


def notify_keeper(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Send keeper request notification via Feishu."""
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    current_status = _pick_value(order, ["order_status", "é æŸ ¬é ˜èˆ¢?"], "")
    if current_status not in {"submitted", "keeper_confirmed"}:
        return {
            "success": False,
            "error": f"current status does not allow keeper notification: {current_status}",
        }

    generated = generate_keeper_text(order_no, current_user=current_user)
    if not generated.get("success"):
        return generated

    summary = _extract_order_values(order)
    notify_type = payload.get("notify_type", "keeper_request")
    notify_channel = payload.get("notify_channel", "feishu")
    keeper_id = payload.get("keeper_id") or summary.get("keeper_id")
    keeper_name = summary.get("keeper_name", "")
    receiver = payload.get("receiver") or keeper_name
    title = payload.get("title") or "Keeper request notification"
    content = payload.get("content") or generated["text"]

    # Get the notification record that was just created by generate_keeper_text
    # We need to query for the most recent keeper_request notification for this order
    delivery_result = deliver_notification_to_feishu(
        {
            "order_no": order_no,
            "notification_type": notify_type,
            "receiver": receiver,
            "title": title,
            "body": content,
            "copy_text": "",
        }
    )
    notify_id = int(delivery_result.get("notification_id", 0))
    if not notify_id:
        return {"success": False, "error": "failed to create notification record"}
    final_status = delivery_result.get("send_status", "failed")
    send_result = delivery_result.get("send_result", "")

    write_order_audit_log(
        order_no=order_no,
        operation_type="keeper_notify",
        operator_user_id=payload.get("operator_id", ""),
        operator_name=payload.get("operator_name", summary["initiator_name"]),
        operator_role=payload.get("operator_role", "initiator"),
        previous_status=current_status,
        new_status=current_status,
        remark=f"keeper notification sent via {notify_channel}, status: {final_status}",
    )
    return {
        "success": True,
        "notify_id": notify_id,
        "send_status": final_status,
        "send_result": send_result,
    }
