# -*- coding: utf-8 -*-
"""
Order workflow service module.
Handles state transitions, confirmations, and workflow operations.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from database import (
    DatabaseManager,
    cancel_tool_io_order,
    final_confirm_order,
    reject_tool_io_order,
    submit_tool_io_order,
)
from backend.database.repositories.mpl_repository import MplRepository
from backend.database.repositories.system_config_repository import SystemConfigRepository
from backend.database.schema.column_names import ORDER_COLUMNS
from backend.services.audit_log_service import (
    OPERATION_KEEPER_CONFIRM,
    OPERATION_TRANSPORT_ASSIGN,
    OPERATION_TRANSPORT_COMPLETE,
    OPERATION_TRANSPORT_START,
    write_order_audit_log,
)
from backend.services.notification_service import (
    KEEPER_CONFIRM_REQUIRED,
    ORDER_CANCELLED,
    ORDER_COMPLETED,
    ORDER_REJECTED,
    ORDER_SUBMITTED,
    ORDER_SUBMITTED_TO_SUPPLY_TEAM,
    TRANSPORT_COMPLETED,
    TRANSPORT_REQUIRED,
    TRANSPORT_STARTED,
)
from backend.services.rbac_data_scope_service import (
    build_order_scope_sql,
    load_keeper_ids_for_org_ids,
    order_matches_scope,
    resolve_order_data_scope,
)
from backend.services.tool_io_runtime import (
    get_order_logs_runtime,
    get_order_detail_runtime,
    keeper_confirm_runtime,
    list_pending_keeper_orders,
)

logger = logging.getLogger(__name__)

# Helper functions extracted from tool_io_service.py
# (to be made self-contained; original definitions remain in tool_io_service.py for Unit 2)


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


def submit_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Submit an order for processing."""
    from backend.services.tool_io_service import _build_actor_context, _emit_internal_notification

    # Check order exists first
    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found"}

    actor = _build_actor_context(payload)
    operator_id = payload.get("operator_id", "")
    operator_name = payload.get("operator_name", "")
    operator_role = payload.get("operator_role", "")
    result = submit_tool_io_order(order_no, operator_id, operator_name, operator_role)

    if result.get("success") and not result.get("idempotent"):
        refreshed = get_order_detail_runtime(order_no)
        if refreshed:
            _emit_internal_notification(
                ORDER_SUBMITTED,
                order=refreshed,
                actor=actor,
                target_user_id=refreshed.get("initiator_id", ""),
                target_user_name=refreshed.get("initiator_name", ""),
                target_role="initiator",
                metadata={"trigger": "submit_order"},
            )
            # Department auto-assignment: notify ALL keepers in the order's org
            order_org_id = refreshed.get("org_id", "")
            if order_org_id:
                all_keepers = load_keeper_ids_for_org_ids([order_org_id])
                for keeper_info in all_keepers:
                    _emit_internal_notification(
                        KEEPER_CONFIRM_REQUIRED,
                        order=refreshed,
                        actor=actor,
                        target_user_id=keeper_info.get("user_id", ""),
                        target_user_name=keeper_info.get("display_name", ""),
                        target_role="keeper",
                        metadata={
                            "required_action": "keeper_confirm",
                            "auto_assigned": True,
                            "org_id": order_org_id,
                        },
                    )
            _emit_internal_notification(
                ORDER_SUBMITTED_TO_SUPPLY_TEAM,
                order=refreshed,
                actor=actor,
                metadata={"trigger": "submit_order", "notify_channel": "supply_team"},
            )
            write_order_audit_log(
                order_no=order_no,
                operation_type=OPERATION_KEEPER_CONFIRM,
                operator_user_id=actor.get("user_id", ""),
                operator_name=actor.get("user_name", ""),
                operator_role=actor.get("user_role", ""),
                remark="Order submitted",
            )

    return result


def keeper_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Keeper confirms an order."""
    # Deferred imports to avoid circular dependency
    from backend.services.tool_io_service import (
        _build_actor_context,
        _emit_internal_notification,
        _is_order_accessible,
        _normalize_bool_text,
        check_order_mpl_violations,
    )

    # Get current order state
    order = get_order_detail_runtime(order_no)
    if not order or not _is_order_accessible(order, current_user):
        return {"success": False, "error": "order not found"}

    # MPL checking (from tool_io_service.py)
    system_config_repo = SystemConfigRepository()
    mpl_repo = MplRepository()
    mpl_enabled = _normalize_bool_text(system_config_repo.get_config("mpl_enabled"))
    if mpl_enabled == "true":
        mpl_strict_mode = _normalize_bool_text(system_config_repo.get_config("mpl_strict_mode"))
        violations = check_order_mpl_violations(order, mpl_repo)
        if violations:
            if mpl_strict_mode == "true":
                return {"success": False, "error": violations[0], "mpl_missing": True, "mpl_warnings": violations}
            payload["mpl_warnings"] = violations

    # Build confirm_data
    confirm_data = {
        "transport_type": payload.get("transport_type"),
        "transport_assignee_id": payload.get("transport_assignee_id"),
        "transport_assignee_name": payload.get("transport_assignee_name"),
        "keeper_remark": payload.get("keeper_remark"),
        "items": payload.get("items"),
    }

    actor = _build_actor_context(payload)
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
        # Re-fetch order for notification
        refreshed = get_order_detail_runtime(order_no)
        if refreshed:
            _emit_internal_notification(
                KEEPER_CONFIRM_REQUIRED,
                order=refreshed,
                actor=actor,
                target_role="team_leader",
            )

    if payload.get("mpl_warnings"):
        result["mpl_warnings"] = payload["mpl_warnings"]
    return result


def final_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Perform final confirmation on an order."""
    from backend.services.tool_io_service import _build_actor_context, _emit_internal_notification, apply_order_location_updates

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

    actor = _build_actor_context(payload)
    result = final_confirm_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )
    if not result.get("success"):
        return result

    # Apply location updates
    refreshed = get_order_detail_runtime(order_no)
    if refreshed:
        apply_order_location_updates(
            order=refreshed,
            milestone="final_confirm",
            operator_user_id=actor["user_id"],
            operator_name=actor["user_name"],
            operator_role=actor["user_role"],
        )
        target_user_id = refreshed.get("initiator_id", "") if availability.get("order_type") == "outbound" else refreshed.get("keeper_id", "")
        target_user_name = refreshed.get("initiator_name", "") if availability.get("order_type") == "outbound" else refreshed.get("keeper_name", "")
        target_role = "initiator" if availability.get("order_type") == "outbound" else "keeper"
        _emit_internal_notification(
            ORDER_COMPLETED,
            order=refreshed,
            actor=actor,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            target_role=target_role,
            metadata={"trigger": "final_confirm"},
        )
    return {
        **result,
        "available": False,
        "data": refreshed,
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
    """Check if final confirmation is available for an order."""
    from backend.services.tool_io_service import _evaluate_final_confirm_availability, _is_order_accessible

    order = get_order_detail_runtime(order_no)
    if not order or not _is_order_accessible(order, current_user):
        return {
            "success": False,
            "error": "order not found",
            "available": False,
        }

    availability = _evaluate_final_confirm_availability(
        order,
        operator_id,
        operator_role,
    )

    return {"success": True, **availability}


def assign_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Assign transport operator to an order."""
    from backend.services.tool_io_service import _build_actor_context, _emit_internal_notification, _pick_value

    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found"}

    current_status = _pick_value(order, ["order_status"], "")
    if current_status not in {"keeper_confirmed", "partially_confirmed", "transport_notified", "transport_in_progress"}:
        return {"success": False, "error": f"current status does not allow transport assignment: {current_status}"}

    transport_assignee_id = payload.get("transport_assignee_id", "")
    transport_assignee_name = payload.get("transport_assignee_name", "")
    transport_type = payload.get("transport_type", "")
    if not transport_assignee_id and not transport_assignee_name:
        return {"success": False, "error": "transport assignee is required"}

    actor = _build_actor_context(payload)
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
    refreshed = get_order_detail_runtime(order_no)
    if refreshed:
        _emit_internal_notification(
            TRANSPORT_REQUIRED,
            order=refreshed,
            actor=actor,
            target_user_id=transport_assignee_id,
            target_user_name=transport_assignee_name,
            target_role="transport_operator",
            metadata={"required_action": "transport", "trigger": "assign_transport"},
        )
    return {"success": True, "data": refreshed}


def start_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Start transport for an order."""
    from backend.services.tool_io_service import _build_actor_context, _emit_internal_notification, _pick_value

    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found"}

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
    refreshed = get_order_detail_runtime(order_no)
    if refreshed:
        target_user_id = refreshed.get("initiator_id", "") if refreshed.get("order_type") == "outbound" else refreshed.get("keeper_id", "")
        target_user_name = refreshed.get("initiator_name", "") if refreshed.get("order_type") == "outbound" else refreshed.get("keeper_name", "")
        target_role = "initiator" if refreshed.get("order_type") == "outbound" else "keeper"
        _emit_internal_notification(
            TRANSPORT_STARTED,
            order=refreshed,
            actor=actor,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            target_role=target_role,
            metadata={"trigger": "start_transport"},
        )
    return {"success": True, "data": refreshed, "before_status": current_status, "after_status": "transport_in_progress"}


def complete_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Complete transport for an order."""
    from backend.services.tool_io_service import _build_actor_context, _emit_internal_notification, _pick_value, apply_order_location_updates

    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found"}

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
    refreshed = get_order_detail_runtime(order_no)
    if refreshed:
        apply_order_location_updates(
            order=refreshed,
            milestone="transport_complete",
            operator_user_id=actor["user_id"],
            operator_name=actor["user_name"],
            operator_role=actor["user_role"],
        )
        target_user_id = refreshed.get("initiator_id", "") if refreshed.get("order_type") == "outbound" else refreshed.get("keeper_id", "")
        target_user_name = refreshed.get("initiator_name", "") if refreshed.get("order_type") == "outbound" else refreshed.get("keeper_name", "")
        target_role = "initiator" if refreshed.get("order_type") == "outbound" else "keeper"
        _emit_internal_notification(
            TRANSPORT_COMPLETED,
            order=refreshed,
            actor=actor,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            target_role=target_role,
            metadata={"trigger": "complete_transport", "next_action": "final_confirm"},
        )
    return {"success": True, "data": refreshed, "before_status": current_status, "after_status": "transport_completed"}


def reject_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Reject an order."""
    from backend.services.tool_io_service import _build_actor_context, _emit_internal_notification, _is_order_accessible

    order = get_order_detail_runtime(order_no)
    if not order or not _is_order_accessible(order, current_user):
        return {"success": False, "error": "order not found"}

    actor = _build_actor_context(payload)
    result = reject_tool_io_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
        payload.get("reject_reason", ""),
    )
    if result.get("success"):
        refreshed = get_order_detail_runtime(order_no)
        if refreshed:
            _emit_internal_notification(
                ORDER_REJECTED,
                order=refreshed,
                actor=actor,
                target_user_id=refreshed.get("initiator_id", ""),
                target_user_name=refreshed.get("initiator_name", ""),
                target_role="initiator",
                metadata={"reject_reason": payload.get("reject_reason", "")},
            )
    return result


def cancel_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Cancel an order."""
    from backend.services.tool_io_service import _build_actor_context, _emit_internal_notification, _is_order_accessible

    order = get_order_detail_runtime(order_no)
    if not order or not _is_order_accessible(order, current_user):
        return {"success": False, "error": "order not found"}

    actor = _build_actor_context(payload)
    result = cancel_tool_io_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
        payload.get("cancel_reason", ""),
    )
    if not result.get("success") and order.get("order_status") in {
        "keeper_confirmed",
        "partially_confirmed",
        "transport_notified",
        "transport_in_progress",
        "transport_completed",
        "final_confirmation_pending",
        "completed",
        "rejected",
        "cancelled",
    }:
        result.setdefault("error_code", "ORDER_STATUS_CONFLICT")
        result.setdefault("current_status", order.get("order_status"))
    if result.get("success"):
        refreshed = get_order_detail_runtime(order_no)
        if refreshed:
            _emit_internal_notification(
                ORDER_CANCELLED,
                order=refreshed,
                actor=actor,
                target_user_id=refreshed.get("initiator_id", ""),
                target_user_name=refreshed.get("initiator_name", ""),
                target_role="initiator",
                metadata={"trigger": "cancel_order"},
            )
    return result


def get_order_logs(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    """Get order operation logs."""
    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found"}
    return {"success": True, "data": get_order_logs_runtime(order_no)}


def get_pending_keeper_list(keeper_id: str = None, current_user: Optional[Dict] = None) -> List[Dict]:
    """Get list of orders pending keeper confirmation."""
    from backend.services.tool_io_service import _resolve_scope_context

    scope_context = _resolve_scope_context(current_user)
    return [order for order in list_pending_keeper_orders(keeper_id) if order_matches_scope(order, scope_context)]
