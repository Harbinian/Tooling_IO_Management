# -*- coding: utf-8 -*-
"""Feishu delivery adapter for notification records."""

from __future__ import annotations

import logging
import json
from typing import Dict, Optional

from urllib import error, request

from config.settings import settings
from database import DatabaseManager, update_notification_status
from backend.services.notification_service import create_notification_record
from backend.services.feature_flag_service import get_feature_flag_service

logger = logging.getLogger(__name__)

FEISHU_NOTIFICATION_FLAG_KEY = "feishu_notification_enabled"
FEISHU_WEBHOOK_KEYS = {
    "ORDER_SUBMITTED_TO_SUPPLY_TEAM": "feishu_webhook_supply_team",
    "TRANSPORT_REQUIRED": "feishu_webhook_transport",
}


def _is_feishu_notification_enabled() -> bool:
    """Check if Feishu notification is enabled via feature flag or settings fallback."""
    flag_service = get_feature_flag_service()
    db_value = flag_service.get_flag_value(FEISHU_NOTIFICATION_FLAG_KEY)
    if db_value is not None:
        return db_value.lower() in ("true", "1", "yes")
    return settings.FEISHU_NOTIFICATION_ENABLED


def _get_db_webhook_url(config_key: str) -> Optional[str]:
    """从数据库读取 Webhook URL，失败返回 None."""
    try:
        flag_service = get_feature_flag_service()
        value = flag_service.get_flag_value(config_key)
        if value and value.strip():
            return value.strip()
    except Exception as exc:
        logger.warning("failed to read webhook from db (%s): %s", config_key, exc)
    return None


SUPPORTED_EVENT_TYPES = {
    "KEEPER_CONFIRM_REQUIRED",
    "TRANSPORT_REQUIRED",
    "TRANSPORT_STARTED",
    "TRANSPORT_COMPLETED",
    "ORDER_COMPLETED",
    "ORDER_SUBMITTED_TO_SUPPLY_TEAM",
}


def _resolve_webhook_url(notification_type: str) -> str:
    """Resolve webhook URL for notification type. Priority: database > environment variable."""
    # Try database config first
    config_key = FEISHU_WEBHOOK_KEYS.get(notification_type)
    if config_key:
        db_url = _get_db_webhook_url(config_key)
        if db_url:
            return db_url

    # Fallback to environment variable
    if notification_type == "TRANSPORT_REQUIRED":
        return settings.FEISHU_WEBHOOK_TRANSPORT or settings.FEISHU_WEBHOOK_URL
    if notification_type == "ORDER_SUBMITTED_TO_SUPPLY_TEAM":
        return settings.FEISHU_WEBHOOK_SUPPLY_TEAM or settings.FEISHU_WEBHOOK_URL
    return settings.FEISHU_WEBHOOK_URL


def _build_message_text(notification_payload: Dict) -> str:
    order_no = str(notification_payload.get("order_no") or notification_payload.get("order_id") or "").strip()
    title = str(notification_payload.get("title") or notification_payload.get("message_title") or "Tool IO notification").strip()
    body = str(notification_payload.get("body") or notification_payload.get("message_body") or "").strip()
    notification_type = str(notification_payload.get("notification_type") or "").strip()
    receiver = str(notification_payload.get("receiver") or "").strip()
    lines = [title]
    if order_no:
        lines.append(f"Order No: {order_no}")
    if notification_type:
        lines.append(f"Notification Type: {notification_type}")
    if receiver:
        lines.append(f"Receiver: {receiver}")
    if body:
        lines.append("")
        lines.append(body)
    return "\n".join(lines)


def _build_tool_list_markdown(notification_payload: Dict) -> str:
    """构建工装需求 Markdown 卡片消息（发送给物资保障部群）"""
    order = notification_payload.get("order", {})

    order_no = str(order.get("order_no") or "").strip()
    order_type = str(order.get("order_type") or "").strip()
    order_type_text = "出库" if order_type == "outbound" else "入库" if order_type == "inbound" else order_type
    initiator_name = str(order.get("initiator_name") or "").strip()
    department = str(order.get("department") or "").strip()
    usage_purpose = str(order.get("usage_purpose") or "").strip()
    target_location = str(order.get("target_location_text") or "").strip()
    planned_time = str(order.get("planned_use_time") or order.get("planned_return_time") or "").strip()
    remark = str(order.get("remark") or "").strip()
    created_at = str(order.get("created_at") or "").strip()

    # 构建表头
    lines = [
        "## 工装需求通知",
        "",
        f"**单号**: {order_no}",
        f"**类型**: {order_type_text}",
        f"**申请人**: {initiator_name}",
        f"**部门**: {department}",
        "",
    ]

    # 出库时显示用途和目标位置
    if order_type == "outbound":
        if usage_purpose:
            lines.append(f"**用途**: {usage_purpose}")
        if target_location:
            lines.append(f"**目标位置**: {target_location}")
    if planned_time:
        time_label = "计划使用时间" if order_type == "outbound" else "计划归还时间"
        lines.append(f"**{time_label}**: {planned_time}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**工装明细**:")
    lines.append("")
    lines.append("| 序号 | 序列号 | 名称 | 图号/机型 | 分体数量 |")
    lines.append("|------|--------|------|-----------|----------|")

    items = order.get("items") or []
    for idx, item in enumerate(items, start=1):
        serial_no = str(item.get("serial_no") or item.get("tool_code") or "-").strip()
        tool_name = str(item.get("tool_name") or "-").strip()
        drawing_no = str(item.get("drawing_no") or "-").strip()
        spec_model = str(item.get("spec_model") or "-").strip()
        split_qty = str(item.get("split_quantity") or item.get("split_qty") or "-").strip()
        lines.append(f"| {idx} | {serial_no} | {tool_name} | {drawing_no} / {spec_model} | {split_qty} |")

    lines.append("")
    lines.append("---")

    if remark:
        lines.append("")
        lines.append(f"**备注**: {remark}")

    if created_at:
        lines.append(f"**时间**: {created_at}")

    return "\n".join(lines)


def send_feishu_message(notification_payload: Dict) -> Dict:
    if not _is_feishu_notification_enabled():
        return {
            "success": False,
            "status": "disabled",
            "response_summary": "Feishu notification delivery is disabled by configuration",
        }

    notification_type = str(notification_payload.get("notification_type") or "")
    webhook_url = _resolve_webhook_url(notification_type)
    if not webhook_url:
        return {
            "success": False,
            "status": "failed",
            "response_summary": "Feishu webhook URL is not configured",
        }

    # ORDER_SUBMITTED_TO_SUPPLY_TEAM 使用 Markdown 卡片格式
    if notification_type == "ORDER_SUBMITTED_TO_SUPPLY_TEAM":
        markdown_content = _build_tool_list_markdown(notification_payload)
        payload = {
            "msg_type": "text",
            "content": {
                "text": markdown_content,
            },
        }
    else:
        payload = {
            "msg_type": "text",
            "content": {
                "text": _build_message_text(notification_payload),
            },
        }
    try:
        req = request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with request.urlopen(req, timeout=settings.FEISHU_NOTIFICATION_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            response_status = response.status
        response_text = response_body[:500] if response_body else ""
        if response_status != 200:
            return {
                "success": False,
                "status": "failed",
                "response_summary": f"HTTP {response_status}: {response_text or 'empty response'}",
            }
        body = json.loads(response_body) if response_body else {}
        if body.get("code") != 0:
            return {
                "success": False,
                "status": "failed",
                "response_summary": f"Feishu error {body.get('code')}: {body.get('msg', 'unknown error')}",
            }
        return {
            "success": True,
            "status": "sent",
            "response_summary": "Feishu notification sent successfully",
        }
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return {
            "success": False,
            "status": "failed",
            "response_summary": f"HTTP {exc.code}: {(body or exc.reason)[:500]}",
        }
    except TimeoutError:
        return {
            "success": False,
            "status": "failed",
            "response_summary": "Feishu notification timed out",
        }
    except Exception as exc:
        logger.error("failed to send Feishu notification: %s", exc)
        return {
            "success": False,
            "status": "failed",
            "response_summary": str(exc),
        }


def create_feishu_delivery_record(notification_payload: Dict) -> Dict:
    return create_notification_record(
        order_no=str(notification_payload.get("order_no") or notification_payload.get("order_id") or "").strip(),
        notification_type=str(notification_payload.get("notification_type") or "").strip(),
        notify_channel="feishu",
        receiver=str(notification_payload.get("receiver") or "").strip(),
        title=str(notification_payload.get("title") or notification_payload.get("message_title") or "").strip(),
        body=str(notification_payload.get("body") or notification_payload.get("message_body") or "").strip(),
        copy_text=str(notification_payload.get("copy_text") or "").strip(),
        status="pending",
    )


def deliver_notification_to_feishu(notification_payload: Dict) -> Dict:
    delivery_record = create_feishu_delivery_record(notification_payload)
    if not delivery_record.get("success"):
        return delivery_record

    send_result = send_feishu_message(notification_payload)
    notify_id = int(delivery_record.get("notification_id", 0))
    if notify_id:
        update_notification_status(
            notify_id,
            send_result.get("status", "failed"),
            send_result.get("response_summary", ""),
        )

    return {
        "success": bool(send_result.get("success")),
        "notification_id": notify_id,
        "send_status": send_result.get("status", "failed"),
        "send_result": send_result.get("response_summary", ""),
    }


def auto_deliver_notification(notification_payload: Dict) -> Dict:
    notification_type = str(notification_payload.get("notification_type") or "").strip()
    if notification_type not in SUPPORTED_EVENT_TYPES:
        return {
            "success": False,
            "status": "skipped",
            "response_summary": f"notification type {notification_type or '-'} is not configured for Feishu auto delivery",
        }
    return deliver_notification_to_feishu(notification_payload)


def retry_feishu_delivery(notification_id: int) -> Dict:
    rows = DatabaseManager().execute_query(
        """
        SELECT
            id AS notification_id,
            order_no AS order_no,
            notify_type AS notification_type,
            notify_channel AS notify_channel,
            receiver AS receiver,
            notify_title AS title,
            notify_content AS body,
            copy_text AS copy_text
        FROM tool_io_notification
        WHERE id = ? AND notify_channel = 'feishu'
        """,
        (notification_id,),
    )
    if not rows:
        return {"success": False, "error": "notification not found"}
    return deliver_notification_to_feishu(rows[0])
