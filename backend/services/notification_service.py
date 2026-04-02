# -*- coding: utf-8 -*-
"""Unified notification helpers for Tool IO workflow events."""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

from database import DatabaseManager, add_tool_io_notification, ensure_tool_io_tables, update_notification_status

logger = logging.getLogger(__name__)


INTERNAL_CHANNEL = "internal"

STATUS_UNREAD = "unread"
STATUS_READ = "read"
STATUS_PROCESSED = "processed"

ORDER_CREATED = "ORDER_CREATED"
ORDER_SUBMITTED = "ORDER_SUBMITTED"
ORDER_SUBMITTED_TO_SUPPLY_TEAM = "ORDER_SUBMITTED_TO_SUPPLY_TEAM"
KEEPER_CONFIRM_REQUIRED = "KEEPER_CONFIRM_REQUIRED"
TRANSPORT_REQUIRED = "TRANSPORT_REQUIRED"
TRANSPORT_STARTED = "TRANSPORT_STARTED"
TRANSPORT_COMPLETED = "TRANSPORT_COMPLETED"
ORDER_COMPLETED = "ORDER_COMPLETED"
ORDER_CANCELLED = "ORDER_CANCELLED"
ORDER_REJECTED = "ORDER_REJECTED"


_TITLE_TEMPLATES = {
    ORDER_CREATED: "出入库单 {order_no} 已创建",
    ORDER_SUBMITTED: "出入库单 {order_no} 已提交",
    KEEPER_CONFIRM_REQUIRED: "出入库单 {order_no} 需要保管员确认",
    TRANSPORT_REQUIRED: "出入库单 {order_no} 需要运输处理",
    TRANSPORT_STARTED: "出入库单 {order_no} 运输已开始",
    TRANSPORT_COMPLETED: "出入库单 {order_no} 运输已完成",
    ORDER_COMPLETED: "出入库单 {order_no} 已完成",
    ORDER_CANCELLED: "出入库单 {order_no} 已取消",
    ORDER_REJECTED: "出入库单 {order_no} 已驳回",
}

_BODY_TEMPLATES = {
    ORDER_CREATED: "出入库单 {order_no} 已由 {actor_name} 创建为草稿。",
    ORDER_SUBMITTED: "出入库单 {order_no} 已由 {actor_name} 提交。",
    KEEPER_CONFIRM_REQUIRED: "出入库单 {order_no} 已提交，需要保管员确认。",
    TRANSPORT_REQUIRED: "出入库单 {order_no} 已通过保管员确认，需要运输处理。",
    TRANSPORT_STARTED: "出入库单 {order_no} 的运输已开始，工装正在搬运中。",
    TRANSPORT_COMPLETED: "出入库单 {order_no} 的运输已完成，订单可以进行最终确认。",
    ORDER_COMPLETED: "出入库单 {order_no} 已由 {actor_name} 完成。",
    ORDER_CANCELLED: "出入库单 {order_no} 已由 {actor_name} 取消。",
    ORDER_REJECTED: "出入库单 {order_no} 已由 {actor_name} 驳回。",
}


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _format_receiver(target_user_id: str = "", target_user_name: str = "", target_role: str = "") -> str:
    parts: List[str] = []
    if _clean_text(target_user_id):
        parts.append(f"user:{_clean_text(target_user_id)}")
    if _clean_text(target_user_name):
        parts.append(f"name:{_clean_text(target_user_name)}")
    if _clean_text(target_role):
        parts.append(f"role:{_clean_text(target_role)}")
    return "|".join(parts)


def _json_payload(payload: Dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _parse_json_payload(value: object) -> Dict:
    raw_text = _clean_text(value)
    if not raw_text:
        return {}
    try:
        parsed = json.loads(raw_text)
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _normalize_notification_row(row: Dict) -> Dict:
    metadata_payload = _parse_json_payload(row.get("copy_text") or row.get("复制文本"))
    metadata = metadata_payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    return {
        "notification_id": row.get("notification_id", row.get("id", 0)),
        "order_id": row.get("order_id") or row.get("order_no") or row.get("出入库单号") or "",
        "notification_type": row.get("notification_type") or row.get("通知类型") or "",
        "notify_channel": row.get("notify_channel") or row.get("通知渠道") or "",
        "receiver": row.get("receiver") or row.get("接收人") or "",
        "message_title": row.get("message_title") or row.get("通知标题") or "",
        "message_body": row.get("message_body") or row.get("通知内容") or "",
        "status": row.get("status") or row.get("发送状态") or "",
        "created_time": row.get("created_time") or row.get("创建时间"),
        "updated_time": row.get("updated_time") or row.get("发送时间"),
        "send_result": row.get("send_result") or row.get("发送结果") or "",
        "copy_text": row.get("copy_text") or row.get("复制文本") or "",
        "metadata": metadata,
        "target_user_id": metadata_payload.get("target_user_id", ""),
        "target_user_name": metadata_payload.get("target_user_name", ""),
        "target_role": metadata_payload.get("target_role", ""),
    }


def build_notification_message(
    notification_type: str,
    *,
    order: Dict,
    actor: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
) -> Dict:
    order_no = _clean_text(order.get("order_no"))
    context = {
        "order_no": order_no or "-",
        "order_type": _clean_text(order.get("order_type")),
        "order_status": _clean_text(order.get("order_status")),
        "actor_name": _clean_text((actor or {}).get("user_name") or (actor or {}).get("operator_name")) or "system",
        "actor_role": _clean_text((actor or {}).get("user_role") or (actor or {}).get("operator_role")),
        "initiator_name": _clean_text(order.get("initiator_name")),
        "keeper_name": _clean_text(order.get("keeper_name")),
        "transport_assignee_name": _clean_text(order.get("transport_assignee_name")),
    }
    context.update(metadata or {})

    title_template = _TITLE_TEMPLATES.get(notification_type, "出入库单 {order_no} 通知")
    body_template = _BODY_TEMPLATES.get(notification_type, "出入库单 {order_no} 产生了一条新通知。")
    return {
        "title": title_template.format(**context),
        "body": body_template.format(**context),
    }


def create_notification_record(
    *,
    order_no: str,
    notification_type: str,
    notify_channel: str,
    receiver: str,
    title: str,
    body: str,
    status: str = STATUS_UNREAD,
    copy_text: str = "",
    metadata: Optional[Dict] = None,
) -> Dict:
    if not _clean_text(order_no) or not _clean_text(notification_type) or not _clean_text(body):
        return {"success": False, "error": "order_no, notification_type, and body are required"}

    try:
        ensure_tool_io_tables()
        payload_copy_text = copy_text
        if not payload_copy_text and metadata:
            payload_copy_text = _json_payload(metadata)

        notify_id = add_tool_io_notification(
            {
                "order_no": order_no,
                "notify_type": notification_type,
                "notify_channel": notify_channel,
                "receiver": receiver,
                "title": title,
                "content": body,
                "copy_text": payload_copy_text,
            }
        )
        if not notify_id:
            return {"success": False, "error": "failed to create notification record"}

        update_notification_status(notify_id, status, f"{notify_channel} notification created")
        return {
            "success": True,
            "notification_id": notify_id,
            "status": status,
            "order_no": order_no,
            "notification_type": notification_type,
            "notify_channel": notify_channel,
            "receiver": receiver,
            "title": title,
            "body": body,
            "copy_text": payload_copy_text,
        }
    except Exception as exc:
        logger.error("failed to create notification record for %s: %s", order_no, exc)
        return {"success": False, "error": str(exc)}


def create_internal_order_notification(
    notification_type: str,
    *,
    order: Dict,
    target_user_id: str = "",
    target_user_name: str = "",
    target_role: str = "",
    actor: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
) -> Dict:
    message = build_notification_message(notification_type, order=order, actor=actor, metadata=metadata)
    structured_payload = {
        "notification_type": notification_type,
        "order_id": _clean_text(order.get("order_no")),
        "target_user_id": _clean_text(target_user_id),
        "target_user_name": _clean_text(target_user_name),
        "target_role": _clean_text(target_role),
        "message_title": message["title"],
        "message_body": message["body"],
        "status": STATUS_UNREAD,
        "metadata": metadata or {},
    }
    return create_notification_record(
        order_no=_clean_text(order.get("order_no")),
        notification_type=notification_type,
        notify_channel=INTERNAL_CHANNEL,
        receiver=_format_receiver(target_user_id, target_user_name, target_role),
        title=message["title"],
        body=message["body"],
        status=STATUS_UNREAD,
        metadata=structured_payload,
    )


def _build_user_receiver_filters(current_user: Dict) -> tuple[str, List[str]]:
    conditions: List[str] = []
    params: List[str] = []

    user_id = _clean_text(current_user.get("user_id"))
    display_name = _clean_text(current_user.get("display_name"))
    role_codes = [
        _clean_text(role_code)
        for role_code in (current_user.get("role_codes") or [role.get("role_code", "") for role in current_user.get("roles", [])])
        if _clean_text(role_code)
    ]

    if user_id:
        conditions.append("接收人 LIKE ?")
        params.append(f"%user:{user_id}%")
    if display_name:
        conditions.append("接收人 LIKE ?")
        params.append(f"%name:{display_name}%")
    for role_code in role_codes:
        conditions.append("接收人 LIKE ?")
        params.append(f"%role:{role_code}%")

    if not conditions:
        conditions.append("1 = 0")

    return "(" + " OR ".join(conditions) + ")", params


def list_notifications_for_user(
    current_user: Dict,
    *,
    page_no: int = 1,
    page_size: int = 20,
    status: str = "",
) -> Dict:
    ensure_tool_io_tables()
    receiver_sql, receiver_params = _build_user_receiver_filters(current_user)
    where_clauses = ["notify_channel = ?", receiver_sql]
    params: List[object] = [INTERNAL_CHANNEL, *receiver_params]
    if _clean_text(status):
        where_clauses.append("send_status = ?")
        params.append(_clean_text(status))

    where_sql = " AND ".join(where_clauses)
    offset = max(page_no - 1, 0) * page_size
    db = DatabaseManager()

    count_sql = f"SELECT COUNT(*) AS total_count FROM tool_io_notification WHERE {where_sql}"
    total_count = int((db.execute_query(count_sql, tuple(params)) or [{"total_count": 0}])[0].get("total_count", 0))

    list_sql = f"""
    SELECT
        id AS notification_id,
        order_no AS order_id,
        notify_type AS notification_type,
        notify_channel AS notify_channel,
        receiver AS receiver,
        notify_title AS message_title,
        notify_content AS message_body,
        send_status AS status,
        send_result AS send_result,
        copy_text AS copy_text,
        created_at AS created_time,
        send_time AS updated_time
    FROM tool_io_notification
    WHERE {where_sql}
    ORDER BY created_at DESC, id DESC
    OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
    """
    rows = db.execute_query(list_sql, tuple(params))
    return {
        "success": True,
        "data": [_normalize_notification_row(row) for row in rows],
        "pagination": {
            "page_no": page_no,
            "page_size": page_size,
            "total_count": total_count,
        },
    }


def list_notifications_by_order(order_no: str) -> Dict:
    ensure_tool_io_tables()
    db = DatabaseManager()
    rows = db.execute_query(
        """
        SELECT
            id AS notification_id,
            order_no AS order_id,
            notify_type AS notification_type,
            notify_channel AS notify_channel,
            receiver AS receiver,
            notify_title AS message_title,
            notify_content AS message_body,
            send_status AS status,
            send_result AS send_result,
            copy_text AS copy_text,
            created_at AS created_time,
            send_time AS updated_time
        FROM tool_io_notification
        WHERE order_no = ?
        ORDER BY created_at DESC, id DESC
        """,
        (_clean_text(order_no),),
    )
    return {"success": True, "data": [_normalize_notification_row(row) for row in rows]}


def mark_notification_as_read(notification_id: int, current_user: Dict) -> Dict:
    ensure_tool_io_tables()
    receiver_sql, receiver_params = _build_user_receiver_filters(current_user)
    params: List[object] = [int(notification_id), INTERNAL_CHANNEL, *receiver_params]
    db = DatabaseManager()

    rows = db.execute_query(
        f"""
        SELECT
            id AS notification_id,
            order_no AS order_id,
            notify_type AS notification_type,
            notify_channel AS notify_channel,
            receiver AS receiver,
            notify_title AS message_title,
            notify_content AS message_body,
            send_status AS status,
            send_result AS send_result,
            copy_text AS copy_text,
            created_at AS created_time,
            send_time AS updated_time
        FROM tool_io_notification
        WHERE id = ?
          AND notify_channel = ?
          AND {receiver_sql}
        """,
        tuple(params),
    )
    if not rows:
        return {"success": False, "error": "notification not found"}

    update_notification_status(
        int(notification_id),
        STATUS_READ,
        f"marked as read by {_clean_text(current_user.get('user_id')) or _clean_text(current_user.get('display_name'))}",
    )
    updated_row = {**rows[0], "status": STATUS_READ}
    return {"success": True, "data": _normalize_notification_row(updated_row)}
