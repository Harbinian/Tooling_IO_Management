# -*- coding: utf-8 -*-
"""
Order workflow service module.
Handles state transitions, confirmations, and workflow operations.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from database import (
    cancel_tool_io_order,
    final_confirm_order,
    reject_tool_io_order,
    submit_tool_io_order,
)
from backend.services.audit_log_service import (
    OPERATION_KEEPER_CONFIRM,
    OPERATION_TRANSPORT_ASSIGN,
    OPERATION_TRANSPORT_COMPLETE,
    OPERATION_TRANSPORT_START,
    write_order_audit_log,
)
from backend.services.tool_io_service import (
    _build_actor_context,
    _emit_internal_notification,
    _evaluate_final_confirm_availability,
    _is_order_accessible,
    _order_not_found_response,
)
from backend.services.tool_io_runtime import (
    get_order_logs_runtime,
    keeper_confirm_runtime,
    list_pending_keeper_orders,
)

logger = logging.getLogger(__name__)


def submit_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Submit an order for processing."""
    from backend.services.tool_io_service import ORDER_SUBMITTED

    actor = _build_actor_context(payload)
    result = submit_tool_io_order(order_no, payload)

    if result.get("success"):
        order = result.get("order", {})
        _emit_internal_notification(
            ORDER_SUBMITTED,
            order=order,
            actor=actor,
            target_role="keeper",
        )
        write_order_audit_log(
            order_no=order_no,
            operation=OPERATION_KEEPER_CONFIRM,
            operator_id=actor.get("user_id", ""),
            operator_name=actor.get("user_name", ""),
            operator_role=actor.get("user_role", ""),
            detail="Order submitted",
        )

    return result


def keeper_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Keeper confirms an order."""
    from backend.services.tool_io_service import (
        KEEPER_CONFIRM_REQUIRED,
        ORDER_SUBMITTED,
    )

    actor = _build_actor_context(payload)

    # Get current order state
    from backend.services.tool_io_runtime import get_order_detail_runtime
    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return _order_not_found_response()

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return _order_not_found_response()

    # Perform keeper confirmation
    result = keeper_confirm_runtime(order_no, actor)

    if result.get("success"):
        _emit_internal_notification(
            KEEPER_CONFIRM_REQUIRED,
            order=order,
            actor=actor,
            target_role="team_leader",
        )
        write_order_audit_log(
            order_no=order_no,
            operation=OPERATION_KEEPER_CONFIRM,
            operator_id=actor.get("user_id", ""),
            operator_name=actor.get("user_name", ""),
            operator_role=actor.get("user_role", ""),
            detail="Order confirmed by keeper",
        )

    return result


def final_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Perform final confirmation on an order."""
    from backend.services.tool_io_service import ORDER_COMPLETED

    actor = _build_actor_context(payload)

    # Get current order state
    from backend.services.tool_io_runtime import get_order_detail_runtime
    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return _order_not_found_response()

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return _order_not_found_response()

    # Perform final confirmation
    result = final_confirm_order(
        order_no,
        actor.get("user_id", ""),
        actor.get("user_name", ""),
        actor.get("user_role", ""),
    )

    if result.get("success"):
        _emit_internal_notification(
            ORDER_COMPLETED,
            order=order,
            actor=actor,
        )
        write_order_audit_log(
            order_no=order_no,
            operation=OPERATION_TRANSPORT_COMPLETE,
            operator_id=actor.get("user_id", ""),
            operator_name=actor.get("user_name", ""),
            operator_role=actor.get("user_role", ""),
            detail="Order completed via final confirmation",
        )

    return result


def get_final_confirm_availability(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    """Check if final confirmation is available for an order."""
    from backend.services.tool_io_runtime import get_order_detail_runtime

    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return {
            "success": False,
            "error": "order not found",
            "available": False,
        }

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return {
            "success": False,
            "error": "order not found",
            "available": False,
        }

    actor = current_user or {}
    availability = _evaluate_final_confirm_availability(
        order,
        actor.get("user_id", ""),
        actor.get("user_role", ""),
    )

    return {
        "success": True,
        "available": availability.get("available", False),
        "reasons": availability.get("reasons", []),
    }


def assign_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Assign transport operator to an order."""
    from backend.services.tool_io_service import TRANSPORT_REQUIRED

    actor = _build_actor_context(payload)

    # Get current order state
    from backend.services.tool_io_runtime import get_order_detail_runtime
    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return _order_not_found_response()

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return _order_not_found_response()

    # Update order with transport info
    db = DatabaseManager()
    try:
        transport_operator = payload.get("transport_operator", "")
        transport_operator_name = payload.get("transport_operator_name", "")
        transport_contact = payload.get("transport_contact", "")

        update_sql = """
            UPDATE 工装出入库单_主表
            SET transport_operator = ?,
                transport_operator_name = ?,
                transport_contact = ?,
                updated_at = SYSDATETIME()
            WHERE order_no = ?
        """
        db.execute_query(
            update_sql,
            (transport_operator, transport_operator_name, transport_contact, order_no),
            fetch=False,
        )
    except Exception as exc:
        logger.error("failed to assign transport for %s: %s", order_no, exc)
        return {"success": False, "error": str(exc)}

    # Emit notification
    _emit_internal_notification(
        TRANSPORT_REQUIRED,
        order=order,
        actor=actor,
        target_role="keeper",
    )

    write_order_audit_log(
        order_no=order_no,
        operation=OPERATION_TRANSPORT_ASSIGN,
        operator_id=actor.get("user_id", ""),
        operator_name=actor.get("user_name", ""),
        operator_role=actor.get("user_role", ""),
        detail=f"Transport assigned: {transport_operator}",
    )

    return {"success": True, "order_no": order_no}


def start_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Start transport for an order."""
    from backend.services.tool_io_service import TRANSPORT_STARTED

    actor = _build_actor_context(payload)

    # Get current order state
    from backend.services.tool_io_runtime import get_order_detail_runtime
    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return _order_not_found_response()

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return _order_not_found_response()

    # Update order status to transport_in_progress
    db = DatabaseManager()
    try:
        update_sql = """
            UPDATE 工装出入库单_主表
            SET order_status = 'transport_in_progress',
                updated_at = SYSDATETIME()
            WHERE order_no = ?
        """
        db.execute_query(update_sql, (order_no,), fetch=False)
    except Exception as exc:
        logger.error("failed to start transport for %s: %s", order_no, exc)
        return {"success": False, "error": str(exc)}

    _emit_internal_notification(
        TRANSPORT_STARTED,
        order=order,
        actor=actor,
    )

    write_order_audit_log(
        order_no=order_no,
        operation=OPERATION_TRANSPORT_START,
        operator_id=actor.get("user_id", ""),
        operator_name=actor.get("user_name", ""),
        operator_role=actor.get("user_role", ""),
        detail="Transport started",
    )

    return {"success": True, "order_no": order_no}


def complete_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Complete transport for an order."""
    from backend.services.tool_io_service import TRANSPORT_COMPLETED

    actor = _build_actor_context(payload)

    # Get current order state
    from backend.services.tool_io_runtime import get_order_detail_runtime
    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return _order_not_found_response()

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return _order_not_found_response()

    # Update order status to transport_completed
    db = DatabaseManager()
    try:
        update_sql = """
            UPDATE 工装出入库单_主表
            SET order_status = 'transport_completed',
                updated_at = SYSDATETIME()
            WHERE order_no = ?
        """
        db.execute_query(update_sql, (order_no,), fetch=False)
    except Exception as exc:
        logger.error("failed to complete transport for %s: %s", order_no, exc)
        return {"success": False, "error": str(exc)}

    _emit_internal_notification(
        TRANSPORT_COMPLETED,
        order=order,
        actor=actor,
    )

    write_order_audit_log(
        order_no=order_no,
        operation=OPERATION_TRANSPORT_COMPLETE,
        operator_id=actor.get("user_id", ""),
        operator_name=actor.get("user_name", ""),
        operator_role=actor.get("user_role", ""),
        detail="Transport completed",
    )

    return {"success": True, "order_no": order_no}


def reject_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Reject an order."""
    from backend.services.tool_io_service import ORDER_REJECTED

    actor = _build_actor_context(payload)
    reject_reason = payload.get("reject_reason", "")

    # Get current order state
    from backend.services.tool_io_runtime import get_order_detail_runtime
    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return _order_not_found_response()

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return _order_not_found_response()

    result = reject_tool_io_order(
        order_no,
        actor.get("user_id", ""),
        actor.get("user_name", ""),
        actor.get("user_role", ""),
        reject_reason,
    )

    if result.get("success"):
        _emit_internal_notification(
            ORDER_REJECTED,
            order=order,
            actor=actor,
            target_role="team_leader",
        )

    return result


def cancel_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Cancel an order."""
    from backend.services.tool_io_service import ORDER_CANCELLED

    actor = _build_actor_context(payload)

    # Get current order state
    from backend.services.tool_io_runtime import get_order_detail_runtime
    detail_result = get_order_detail_runtime(order_no, current_user)
    if not detail_result.get("success"):
        return _order_not_found_response()

    order = detail_result.get("order", {})
    if not _is_order_accessible(order, current_user):
        return _order_not_found_response()

    result = cancel_tool_io_order(
        order_no,
        actor.get("user_id", ""),
        actor.get("user_name", ""),
        actor.get("user_role", ""),
    )

    if result.get("success"):
        _emit_internal_notification(
            ORDER_CANCELLED,
            order=order,
            actor=actor,
        )

    return result


def get_order_logs(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    """Get order operation logs."""
    return get_order_logs_runtime(order_no, current_user)


def get_pending_keeper_list(keeper_id: str = None, current_user: Optional[Dict] = None) -> List[Dict]:
    """Get list of orders pending keeper confirmation."""
    return list_pending_keeper_orders(keeper_id, current_user)
