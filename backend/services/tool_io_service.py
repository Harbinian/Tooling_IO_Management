# -*- coding: utf-8 -*-
"""
Service wrappers for Tool IO backend flows.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from backend.database.repositories.tool_repository import ToolRepository
from backend.database.schema.column_names import ORDER_COLUMNS, ITEM_COLUMNS, TABLE_NAMES
from database import (
    DatabaseManager,
    cancel_tool_io_order,
    create_tool_io_order,
    ensure_schema_alignment,
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
ALLOWED_BATCH_TOOL_STATUSES = {"in_storage", "outbounded", "maintain", "scrapped"}


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
    ensure_schema_alignment()
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


def update_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Update order content when order is in draft status.

    Allows updating order items and remark. After update, order remains in draft status
    and can be resubmitted.

    Args:
        order_no: Order number
        payload: Update payload with items and/or remark
        current_user: Current authenticated user

    Returns:
        Result dictionary with success status
    """
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()

    # Check if order is in draft status
    from backend.services.order_query_service import get_order_detail as get_order_detail_runtime
    order = get_order_detail_runtime(order_no)
    if not order:
        return _order_not_found_response()

    current_status = order.get("order_status", "")
    if current_status != "draft":
        return {"success": False, "error": f"只有草稿状态的订单可以编辑，当前状态：{current_status}"}

    # Build actor context for audit
    actor = _build_actor_context(payload)

    # Delegate to repository layer
    from backend.database.repositories.order_repository import OrderRepository
    from backend.database.db_pool import get_db_connection

    db = get_db_connection()
    try:
        repo = OrderRepository(db)
        result = repo.update_order(order_no, payload, operator_id=actor["user_id"], operator_name=actor["user_name"], operator_role=actor["user_role"])
    finally:
        db.close()

    if result.get("success"):
        # Log the update
        from backend.database.repositories.order_repository import ToolIOAction
        logger.info(f"Order {order_no} updated by {actor['user_name']}")
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
    scope_context = _resolve_scope_context(current_user)
    if not order_matches_scope(order, scope_context):
        return False

    # Restrict "all-access" users (for example admins) from viewing draft orders.
    if scope_context.get("all_access"):
        return (order.get("order_status") or "").strip().lower() != "draft"
    return True


def list_orders(filters: Dict, current_user: Optional[Dict] = None) -> Dict:
    raw_result = get_tool_io_orders(
        order_type=filters.get("order_type"),
        status=filters.get("order_status"),
        applicant_id=filters.get("initiator_id"),
        keeper_id=filters.get("keeper_id"),
        keyword=filters.get("keyword"),
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
        page=filters.get("page_no", 1),
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
            # Notify initiator about submission
            _emit_internal_notification(
                ORDER_SUBMITTED,
                order=order,
                actor=actor,
                target_user_id=order.get("initiator_id", ""),
                target_user_name=order.get("initiator_name", ""),
                target_role="initiator",
                metadata={"trigger": "submit_order"},
            )

            # Department auto-assignment: notify ALL keepers in the order's org
            from backend.services.rbac_data_scope_service import load_keeper_ids_for_org_ids
            order_org_id = order.get("org_id", "")
            if order_org_id:
                all_keepers = load_keeper_ids_for_org_ids([order_org_id])
                for keeper_info in all_keepers:
                    _emit_internal_notification(
                        KEEPER_CONFIRM_REQUIRED,
                        order=order,
                        actor=actor,
                        target_user_id=keeper_info.get("user_id", ""),
                        target_user_name=keeper_info.get("display_name", ""),
                        target_role="keeper",
                        metadata={
                            "required_action": "keeper_confirm",
                            "auto_assigned": True,  # Mark as auto-assigned by department
                            "org_id": order_org_id,
                        },
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
    transport_type = payload.get("transport_type", "")
    if not transport_assignee_id and not transport_assignee_name:
        return {"success": False, "error": "transport assignee is required"}

    DatabaseManager().execute_query(
        f"""
        UPDATE tool_io_order
        SET {ORDER_COLUMNS['transport_assignee_id']} = ?,
            {ORDER_COLUMNS['transport_assignee_name']} = ?,
            {ORDER_COLUMNS['transport_type']} = ?,
            {ORDER_COLUMNS['updated_at']} = GETDATE()
        WHERE {ORDER_COLUMNS['order_no']} = ?
        """,
        (transport_assignee_id, transport_assignee_name, transport_type, order_no),
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
        f"""
        UPDATE tool_io_order
        SET {ORDER_COLUMNS['order_status']} = 'transport_in_progress',
            {ORDER_COLUMNS['transport_operator_id']} = COALESCE(NULLIF(?, ''), {ORDER_COLUMNS['transport_operator_id']}),
            {ORDER_COLUMNS['transport_operator_name']} = COALESCE(NULLIF(?, ''), {ORDER_COLUMNS['transport_operator_name']}),
            {ORDER_COLUMNS['updated_at']} = GETDATE()
        WHERE {ORDER_COLUMNS['order_no']} = ?
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
        f"""
        UPDATE tool_io_order
        SET {ORDER_COLUMNS['order_status']} = 'transport_completed',
            {ORDER_COLUMNS['updated_at']} = GETDATE()
        WHERE {ORDER_COLUMNS['order_no']} = ?
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
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
        payload.get("reject_reason", ""),
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


def reset_order_to_draft(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()
    result = reset_order_to_draft_order(
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
                ORDER_SUBMITTED,
                order=order,
                actor=actor,
                target_user_id=order.get("initiator_id", ""),
                target_user_name=order.get("initiator_name", ""),
                target_role="initiator",
                metadata={"trigger": "reset_order_to_draft"},
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
        payload.get("cancel_reason", ""),
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


def delete_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Delete an order through the admin cascade cleanup path."""
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()

    from backend.database.repositories.order_repository import OrderRepository
    repo = OrderRepository()

    result = repo.delete_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )
    return result


def get_order_logs(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    if not get_order_detail(order_no, current_user=current_user):
        return _order_not_found_response()
    return {"success": True, "data": get_order_logs_runtime(order_no)}


def get_pending_keeper_list(keeper_id: str = None, current_user: Optional[Dict] = None) -> List[Dict]:
    scope_context = _resolve_scope_context(current_user)
    return [order for order in list_pending_keeper_orders(keeper_id) if order_matches_scope(order, scope_context)]


def get_pre_transport_orders(current_user: Optional[Dict] = None) -> Dict:
    """Get pre-transport visibility list for transport executors."""
    if not current_user:
        return {"success": False, "error": "authentication required", "orders": []}

    from backend.database.repositories.order_repository import OrderRepository

    scope_context = _resolve_scope_context(current_user)
    org_ids = [str(org_id).strip() for org_id in (scope_context.get("org_ids") or []) if str(org_id).strip()]
    if not org_ids and not scope_context.get("all_access"):
        current_org = current_user.get("current_org") or {}
        default_org = current_user.get("default_org") or {}
        fallback_org_id = str(
            current_org.get("org_id")
            or default_org.get("org_id")
            or current_user.get("default_org_id", "")
        ).strip()
        if fallback_org_id:
            org_ids = [fallback_org_id]

    rows = OrderRepository().get_pre_transport_orders(
        user_id=str(current_user.get("user_id", "")).strip(),
        org_ids=org_ids,
        all_access=bool(scope_context.get("all_access")),
    )
    return {
        "success": True,
        "orders": [_format_pre_transport_order(row) for row in rows],
    }


def get_notification_records(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    if not current_user:
        return {"success": False, "error": "authentication required", "data": []}

    order = _load_order_scope_projection(order_no)
    if not order or not _is_order_accessible(order, current_user):
        return {"success": False, "error": "order not found", "data": []}

    try:
        return list_notifications_by_order(order_no)
    except Exception as exc:
        logger.error("failed to load notification records for %s: %s", order_no, exc)
        return {"success": False, "error": str(exc), "data": []}


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


def _load_order_scope_projection(order_no: str) -> Dict:
    rows = DatabaseManager().execute_query(
        f"""
        SELECT
            [{ORDER_COLUMNS['order_no']}] AS [{ORDER_COLUMNS['order_no']}],
            [{ORDER_COLUMNS['order_status']}] AS [{ORDER_COLUMNS['order_status']}],
            [{ORDER_COLUMNS['org_id']}] AS [{ORDER_COLUMNS['org_id']}],
            [{ORDER_COLUMNS['initiator_id']}] AS [{ORDER_COLUMNS['initiator_id']}],
            [{ORDER_COLUMNS['keeper_id']}] AS [{ORDER_COLUMNS['keeper_id']}],
            [{ORDER_COLUMNS['transport_assignee_id']}] AS [{ORDER_COLUMNS['transport_assignee_id']}]
        FROM [{TABLE_NAMES['ORDER']}]
        WHERE [{ORDER_COLUMNS['order_no']}] = ?
          AND [{ORDER_COLUMNS['is_deleted']}] = 0
        """,
        (order_no,),
    )
    if not rows:
        return {}
    return rows[0]


def _to_iso8601(value) -> Optional[str]:
    if value in (None, ""):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _format_pre_transport_order(row: Dict) -> Dict:
    status = str(row.get("status", "")).strip()
    status_text = str(row.get("status_text", "")).strip()
    if not status_text:
        status_text = {
            "submitted": "已提交",
            "keeper_confirmed": "保管员已确认",
            "transport_notified": "运输已通知",
        }.get(status, status)

    expected_tools_raw = row.get("expected_tools", 0)
    try:
        expected_tools = int(expected_tools_raw or 0)
    except (TypeError, ValueError):
        expected_tools = 0

    return {
        "order_no": str(row.get("order_no", "")).strip(),
        "order_type": str(row.get("order_type", "")).strip(),
        "destination": str(row.get("destination", "")).strip(),
        "status": status,
        "status_text": status_text,
        "expected_tools": expected_tools,
        "submit_time": _to_iso8601(row.get("submit_time")),
        "submitter_name": str(row.get("submitter_name", "")).strip(),
        "estimated_transport_time": _to_iso8601(row.get("estimated_transport_time")),
        "keeper_confirmed_time": _to_iso8601(row.get("keeper_confirmed_time")),
    }


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
                "tool_code": _pick_value(item, ["tool_code"], ""),
                "tool_name": _pick_value(item, ["tool_name", "宸ヨ鍚嶇О"], ""),
                "drawing_no": _pick_value(item, ["drawing_no", "宸ヨ鍥惧彿"], ""),
                "spec_model": _pick_value(item, ["spec_model", "鏈哄瀷", "瑙勬牸鍨嬪彿"], ""),
                "location_text": _pick_value(item, ["location_text"], ""),
                "apply_qty": _pick_value(item, ["apply_qty", "鐢宠鏁伴噺"], 1),
                "approved_qty": _pick_value(item, ["approved_qty", "纭鏁伴噺"], 0),
                "item_status": item_status,
            }
        )
        if item_status == "approved":
            approved_count_from_items += 1

    # Tool count is always derived from items.length (tools are identified by serial number, not quantity)
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


def _get_runtime_order_summary(order_no: str, current_user: Optional[Dict] = None) -> Optional[Dict]:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return None

    return {
        "order_no": _pick_value(order, ["order_no"], order_no),
        "order_type": _pick_value(order, ["order_type"]),
        "order_status": _pick_value(order, ["order_status"]),
        "initiator_id": _pick_value(order, ["initiator_id"]),
        "keeper_id": _pick_value(order, ["keeper_id"]),
        "transport_assignee_id": _pick_value(order, ["transport_assignee_id"]),
        "approved_count": _pick_value(order, ["approved_count"], 0),
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
    result = search_tools(
        keyword=filters.get("keyword"),
        status=filters.get("status"),
        location=filters.get("location") or filters.get("location_id"),
        page=filters.get("page_no", 1),
        page_size=filters.get("page_size", 20),
    )
    if not result.get("success"):
        return result

    normalized_rows = []
    for row in result.get("data") or []:
        normalized = dict(row or {})
        reason_raw = normalized.get("disabled_reason")
        reason = str(reason_raw).strip() if reason_raw is not None else ""
        normalized_reason = reason or None

        disabled_raw = normalized.get("disabled")
        if isinstance(disabled_raw, bool):
            normalized_disabled = disabled_raw
        elif isinstance(disabled_raw, (int, float)):
            normalized_disabled = disabled_raw != 0
        elif isinstance(disabled_raw, str):
            normalized_disabled = disabled_raw.strip().lower() in {"1", "true", "yes", "y"}
        else:
            normalized_disabled = False

        normalized["disabled"] = normalized_disabled or (normalized_reason is not None)
        normalized["disabled_reason"] = normalized_reason if normalized["disabled"] else None
        normalized_rows.append(normalized)

    return {**result, "data": normalized_rows}


def batch_update_tool_status(
    tool_codes: List[str],
    new_status: str,
    remark: str,
    operator: Dict,
    client_ip: str = "",
) -> Dict:
    """Batch update tool status and write status change history."""
    cleaned_codes: List[str] = []
    seen_codes = set()
    for code in tool_codes or []:
        normalized_code = str(code).strip()
        if not normalized_code or normalized_code in seen_codes:
            continue
        seen_codes.add(normalized_code)
        cleaned_codes.append(normalized_code)

    if not cleaned_codes:
        return {"success": False, "error": "tool_codes must contain at least one code"}

    normalized_status = str(new_status or "").strip().lower()
    if normalized_status not in ALLOWED_BATCH_TOOL_STATUSES:
        return {
            "success": False,
            "error": "new_status must be one of: in_storage, outbounded, maintain, scrapped",
        }

    repo = ToolRepository()
    return repo.update_tool_status_batch(
        tool_codes=cleaned_codes,
        new_status=normalized_status,
        operator=operator or {},
        remark=str(remark or "").strip() or None,
        client_ip=str(client_ip or "").strip() or None,
    )


def get_tool_status_history(tool_code: str, page_no: int = 1, page_size: int = 20) -> Dict:
    """Get one tool status history with pagination."""
    normalized_code = str(tool_code or "").strip()
    if not normalized_code:
        return {"success": False, "error": "tool_code is required"}
    repo = ToolRepository()
    return repo.get_tool_status_history(normalized_code, page_no=page_no, page_size=page_size)


def batch_query_tools(tool_codes: List[str]) -> Dict:
    cleaned_codes = [code.strip() for code in tool_codes if isinstance(code, str) and code.strip()]
    if not cleaned_codes:
        return {"success": False, "error": "tool_codes must contain at least one code", "data": []}

    rows = list(ToolRepository().load_tool_master_map(cleaned_codes).values())
    return {"success": True, "data": rows}


def _format_order_datetime(value) -> str:
    if value is None:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _extract_order_values(record: Dict) -> Dict:
    return {
        "order_no": _pick_value(record, ["order_no"], ""),
        "order_type": _pick_value(record, ["order_type"], ""),
        "order_status": _pick_value(record, ["order_status"], ""),
        "initiator_name": _pick_value(record, ["initiator_name"], ""),
        "initiator_id": _pick_value(record, ["initiator_id"], ""),
        "department": _pick_value(record, ["department"], ""),
        "required_by": _pick_value(record, ["required_by"], ""),
        "remark": _pick_value(record, ["remark"], ""),
        "created_at": _pick_value(record, ["created_at"]),
        "submitted_at": _pick_value(record, ["submit_time", "submitted_at"]),
        "transport_type": _pick_value(record, ["transport_type"], ""),
        "transport_assignee_name": _pick_value(record, ["transport_assignee_name"], ""),
        "keeper_name": _pick_value(record, ["keeper_name"], ""),
        "transport_receiver": _pick_value(record, ["receiver"], ""),
    }


def _extract_item_values(item: Dict) -> Dict:
    return {
        "tool_code": _pick_value(item, ["tool_code"], ""),
        "tool_name": _pick_value(item, ["tool_name"], ""),
        "drawing_no": _pick_value(item, ["drawing_no"], ""),
        "location_text": _pick_value(item, ["location_text"], ""),
        "apply_qty": _pick_value(item, ["apply_qty"], 1),
        "approved_qty": _pick_value(item, ["approved_qty"], 0),
        "item_status": _pick_value(item, ["item_status", "status"], ""),
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
        if _pick_value(item, [ITEM_COLUMNS['item_status'], "item_status", "status"], "") == "approved"
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

    current_status = _pick_value(order, ["order_status", "茅聧鈥斆︹€号该ヂ德伱┞愃溍ㄋ喡得⑩€毬?"], "")
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
        f"""
        UPDATE [{TABLE_NAMES['ORDER']}]
        SET {ORDER_COLUMNS['order_status']} = 'transport_notified',
            {ORDER_COLUMNS['updated_at']} = GETDATE()
        WHERE {ORDER_COLUMNS['order_no']} = ?
        """,
        (order_no,),
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

    current_status = _pick_value(order, ["order_status", "茅 聧忙鸥 卢茅 聬藴猫藛垄?"], "")
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

