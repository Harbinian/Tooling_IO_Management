# -*- coding: utf-8 -*-
"""
Service wrappers for Tool IO backend flows.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from datetime import datetime

from backend.database.repositories.mpl_repository import MplRepository
from backend.database.repositories.system_config_repository import SystemConfigRepository
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
    ORDER_SUBMITTED_TO_SUPPLY_TEAM,
    TRANSPORT_COMPLETED,
    TRANSPORT_REQUIRED,
    TRANSPORT_STARTED,
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
from backend.services.order_workflow_service import (
    assign_transport as _assign_transport,
    cancel_order as _cancel_order,
    complete_transport as _complete_transport,
    final_confirm as _final_confirm,
    get_final_confirm_availability as _get_final_confirm_availability,
    get_order_logs as _get_order_logs,
    get_pending_keeper_list as _get_pending_keeper_list,
    keeper_confirm as _keeper_confirm,
    reject_order as _reject_order,
    start_transport as _start_transport,
    submit_order as _submit_order,
)

logger = logging.getLogger(__name__)
ALLOWED_BATCH_TOOL_STATUSES = {"in_storage", "outbounded", "maintain", "scrapped"}
MPL_MAX_PHOTO_BYTES = 2 * 1024 * 1024


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
    # Internal notifications disabled — normal workflow events are already tracked in operation logs.
    # Only external notifications (Feishu/WeChat) are recorded.
    return
    delivery_result = auto_deliver_notification(
        {
            "notification_id": result.get("notification_id", 0),
            "order_no": order.get("order_no", ""),
            "order": order,  # 传递完整订单对象，用于 Markdown 消息构建
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


def _normalize_bool_text(value: Optional[str], default: str = "false") -> str:
    normalized = str(value if value is not None else default).strip().lower()
    return "true" if normalized in {"1", "true", "yes", "on"} else "false"


def _build_mpl_validation_message(drawing_no: str, revision: str) -> str:
    return f"工装 {drawing_no or '-'} (版次 {revision or '-'}) 缺少可拆卸件清单"


def _resolve_item_revision(item: Dict) -> str:
    return str(
        item.get("current_version")
        or item.get("currentVersion")
        or item.get("tool_revision")
        or item.get("toolRevision")
        or item.get("version")
        or ""
    ).strip()


def check_order_mpl_violations(order: Dict, mpl_repo: Optional[MplRepository] = None) -> List[str]:
    """Check whether each tool item in the order has a matching MPL group."""
    repo = mpl_repo or MplRepository()
    violations: List[str] = []
    seen_pairs = set()
    for item in order.get("items", []) or []:
        drawing_no = str(item.get("drawing_no") or item.get("drawingNo") or "").strip()
        revision = _resolve_item_revision(item)
        if not drawing_no:
            continue
        key = (drawing_no, revision)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        if not repo.mpl_exists(drawing_no, revision):
            violations.append(_build_mpl_validation_message(drawing_no, revision))
    return violations


def _validate_mpl_component(item: Dict) -> Dict:
    component_no = str(item.get("component_no", "")).strip()
    component_name = str(item.get("component_name", "")).strip()
    if not component_no:
        raise ValueError("component_no is required")
    if not component_name:
        raise ValueError("component_name is required")
    try:
        quantity = int(item.get("quantity", 1) or 1)
    except (TypeError, ValueError) as exc:
        raise ValueError("quantity must be an integer") from exc
    if quantity <= 0:
        raise ValueError("quantity must be greater than 0")
    photo_data = item.get("photo_data")
    if photo_data and len(str(photo_data).encode("utf-8")) > MPL_MAX_PHOTO_BYTES * 2:
        raise ValueError("photo_data exceeds supported size limit")
    return {
        "component_no": component_no,
        "component_name": component_name,
        "quantity": quantity,
        "photo_data": photo_data or None,
    }


def _validate_mpl_payload(payload: Dict, *, fallback_user: str = "") -> Dict:
    tool_drawing_no = str(payload.get("tool_drawing_no", "")).strip()
    tool_revision = str(payload.get("tool_revision", "")).strip()
    if not tool_drawing_no:
        raise ValueError("tool_drawing_no is required")
    if not tool_revision:
        raise ValueError("tool_revision is required")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("items must contain at least one component")

    normalized_items: List[Dict] = []
    seen_component_nos = set()
    for item in items:
        normalized = _validate_mpl_component(item or {})
        component_no = normalized["component_no"]
        if component_no in seen_component_nos:
            raise ValueError(f"duplicate component_no: {component_no}")
        seen_component_nos.add(component_no)
        normalized_items.append(normalized)

    updated_by = str(payload.get("updated_by") or payload.get("created_by") or fallback_user or "").strip() or "system"
    return {
        "tool_drawing_no": tool_drawing_no,
        "tool_revision": tool_revision,
        "items": normalized_items,
        "created_by": updated_by,
        "updated_by": updated_by,
    }


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


def _ensure_system_config_ready() -> None:
    from backend.database.schema.schema_manager import ensure_system_config_table

    if not ensure_system_config_table():
        raise RuntimeError("sys_system_config is not ready")


def list_system_configs() -> Dict:
    _ensure_system_config_ready()
    repo = SystemConfigRepository()
    return {"success": True, "data": repo.list_configs()}


def get_system_config(config_key: str) -> Dict:
    _ensure_system_config_ready()
    repo = SystemConfigRepository()
    value = repo.get_config(config_key)
    if value is None:
        return {"success": False, "error": "config not found"}
    rows = [row for row in repo.list_configs() if row.get("config_key") == config_key]
    return {"success": True, "data": rows[0] if rows else {"config_key": config_key, "config_value": value}}


def update_system_config(config_key: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    _ensure_system_config_ready()
    if "config_value" not in payload:
        raise ValueError("config_value is required")
    normalized_value = _normalize_bool_text(payload.get("config_value")) if config_key in {"mpl_enabled", "mpl_strict_mode"} else str(payload.get("config_value", ""))
    repo = SystemConfigRepository()
    repo.set_config(
        config_key,
        normalized_value,
        updated_by=str((current_user or {}).get("display_name") or payload.get("operator_name") or "system"),
        description=payload.get("description"),
    )
    return get_system_config(config_key)


def list_mpl_groups(filters: Dict, current_user: Optional[Dict] = None) -> Dict:
    _ = current_user
    ensure_tool_io_tables()
    repo = MplRepository()
    result = repo.list_all(
        page=filters.get("page_no", 1),
        page_size=filters.get("page_size", 20),
        drawing_no=filters.get("drawing_no", ""),
        keyword=filters.get("keyword", ""),
    )
    return {"success": True, **result}


def get_mpl_group(mpl_no: str, current_user: Optional[Dict] = None) -> Dict:
    _ = current_user
    ensure_tool_io_tables()
    repo = MplRepository()
    group = repo.get_group(mpl_no)
    if not group:
        return {"success": False, "error": "mpl not found"}
    return {"success": True, "data": group}


def get_mpl_by_tool(tool_drawing_no: str, tool_revision: str, current_user: Optional[Dict] = None) -> Dict:
    _ = current_user
    ensure_tool_io_tables()
    repo = MplRepository()
    group = repo.get_group(repo.build_mpl_no(tool_drawing_no, tool_revision))
    if not group:
        return {"success": False, "error": "mpl not found"}
    return {"success": True, "data": group}


def create_mpl_group(payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    ensure_tool_io_tables()
    repo = MplRepository()
    validated = _validate_mpl_payload(payload, fallback_user=str((current_user or {}).get("display_name", "")))
    return {"success": True, "data": repo.create_mpl(validated)}


def update_mpl_group(mpl_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    ensure_tool_io_tables()
    repo = MplRepository()
    validated = _validate_mpl_payload(payload, fallback_user=str((current_user or {}).get("display_name", "")))
    return {"success": True, "data": repo.update_mpl(mpl_no, validated)}


def delete_mpl_group(mpl_no: str, current_user: Optional[Dict] = None) -> Dict:
    _ = current_user
    ensure_tool_io_tables()
    repo = MplRepository()
    if not repo.get_group(mpl_no):
        return {"success": False, "error": "mpl not found"}
    repo.delete_mpl(mpl_no)
    return {"success": True}


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
    """Delegate to order_workflow_service.submit_order."""
    return _submit_order(order_no, payload, current_user)


def keeper_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Delegate to order_workflow_service.keeper_confirm."""
    return _keeper_confirm(order_no, payload, current_user)


def final_confirm(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Delegate to order_workflow_service.final_confirm."""
    return _final_confirm(order_no, payload, current_user)


def get_final_confirm_availability(
    order_no: str,
    operator_id: str = "",
    operator_role: str = "",
    current_user: Optional[Dict] = None,
) -> Dict:
    """Delegate to order_workflow_service.get_final_confirm_availability."""
    return _get_final_confirm_availability(order_no, operator_id, operator_role, current_user)


def assign_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Delegate to order_workflow_service.assign_transport."""
    return _assign_transport(order_no, payload, current_user)


def start_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Delegate to order_workflow_service.start_transport."""
    return _start_transport(order_no, payload, current_user)


def complete_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Delegate to order_workflow_service.complete_transport."""
    return _complete_transport(order_no, payload, current_user)


def reject_order(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    """Delegate to order_workflow_service.reject_order."""
    return _reject_order(order_no, payload, current_user)


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
    """Delegate to order_workflow_service.cancel_order."""
    return _cancel_order(order_no, payload, current_user)


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
    """Delegate to order_workflow_service.get_order_logs."""
    return _get_order_logs(order_no, current_user)


def get_pending_keeper_list(keeper_id: str = None, current_user: Optional[Dict] = None) -> List[Dict]:
    """Delegate to order_workflow_service.get_pending_keeper_list."""
    return _get_pending_keeper_list(keeper_id, current_user)


MATERIAL_SUPPORT_ORG_ID = "ORG_DEPT_001"


def get_pre_transport_orders(current_user: Optional[Dict] = None) -> Dict:
    """Get pre-transport visibility list for transport executors.

    Only PRODUCTION_PREP role in Material Support Department (物资保障部) can access.
    """
    if not current_user:
        return {"success": False, "error": "authentication required", "orders": []}

    # Verify user is PRODUCTION_PREP role
    role_codes = current_user.get("role_codes", [])
    if not role_codes:
        role_codes = [r.get("role_code") for r in current_user.get("roles", []) if r.get("role_code")]
    # role_codes comes from RBAC role_code and must be compared case-insensitively.
    if not any(str(role_code).strip().lower() == "production_prep_worker" for role_code in role_codes):
        return {"success": False, "error": "permission denied", "orders": []}

    # Verify user belongs to Material Support Department (物资保障部)
    current_org = current_user.get("current_org") or {}
    default_org = current_user.get("default_org") or {}
    user_org_id = str(
        current_org.get("org_id")
        or default_org.get("org_id")
        or current_user.get("default_org_id", "")
    ).strip()
    if user_org_id != MATERIAL_SUPPORT_ORG_ID:
        return {"success": False, "error": "permission denied", "orders": []}

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


def get_tool_status_history(serial_no: str, page_no: int = 1, page_size: int = 20) -> Dict:
    """Get one tool status history with pagination."""
    normalized_code = str(serial_no or "").strip()
    if not normalized_code:
        return {"success": False, "error": "serial_no is required"}
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


def _build_keeper_text(summary: Dict, items: List[Dict], order_no: str) -> str:
    _ = items
    return f"【工装管理系统】您有待处理订单，单号 {summary['order_no'] or order_no}，请登录系统查看。"


def _build_preview_order_no(order_type: str) -> str:
    prefix = "TO-OUT" if order_type == "outbound" else "TO-IN"
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-PREVIEW"


def preview_keeper_text(payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    _ = current_user
    items_payload = payload.get("items")
    if not isinstance(items_payload, list) or not items_payload:
        return {"success": False, "error": "请至少选择一项工装"}

    order_type = str(payload.get("order_type") or "").strip()
    if order_type not in {"outbound", "inbound"}:
        return {"success": False, "error": "单据类型不正确"}

    order_no = _build_preview_order_no(order_type)
    text = f"【工装管理系统】您有待处理订单，单号 {order_no}，请登录系统查看。"
    return {"success": True, "text": text}


def generate_keeper_text(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    summary = _extract_order_values(order)
    items = [_extract_item_values(item) for item in order.get("items", [])]
    text = _build_keeper_text(summary, items, order_no)
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
    required_by = summary.get("required_by") or "-"
    pickup_locations = sorted({(item.get("location_text") or "-").strip() or "-" for item in approved_items})
    location_text = "；".join(pickup_locations) if pickup_locations else "-"
    detail_lines = "\n".join(
        [
            (
                f"{idx + 1}. {item['serial_no'] or '-'} / {item['tool_name'] or '-'} / "
                f"图号 {item['drawing_no'] or '-'} / 数量 {item['split_quantity'] or item['approved_qty'] or 1} / "
                f"库位 {item['location_text'] or '-'}"
            )
            for idx, item in enumerate(approved_items)
        ]
    )
    transport_type = summary["transport_type"] or "-"
    receiver = summary["transport_assignee_name"] or summary["transport_receiver"] or "-"
    applicant = summary["initiator_name"] or "-"
    keeper_name = summary["keeper_name"] or "-"
    text = (
        f"【运输准备通知】\n"
        f"单号：{summary['order_no'] or order_no}\n"
        f"运输类型：{transport_type}\n"
        f"需求日期：{required_by}\n"
        f"取货地点：{location_text}\n"
        f"接收人：{receiver}\n"
        f"申请人：{applicant}\n"
        f"保管员：{keeper_name}\n\n"
        f"工装明细：\n{detail_lines}\n\n"
        "请根据确认的工装清单安排运输。"
    )
    wechat_text = text
    return {"success": True, "text": text, "wechat_text": wechat_text}


def notify_transport(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    order = get_order_detail(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    current_status = _pick_value(order, ["order_status", "单据状态"], "")
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
    title = payload.get("title") or "运输通知"
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

    current_status = _pick_value(order, ["order_status", "单据状态"], "")
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
    title = payload.get("title") or "保管员确认请求"
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

