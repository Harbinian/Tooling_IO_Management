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

logger = logging.getLogger(__name__)


SUPPORTED_EVENT_TYPES = {
    "KEEPER_CONFIRM_REQUIRED",
    "TRANSPORT_REQUIRED",
    "TRANSPORT_STARTED",
    "TRANSPORT_COMPLETED",
    "ORDER_COMPLETED",
}


def _resolve_webhook_url(notification_type: str) -> str:
    if notification_type == "TRANSPORT_REQUIRED":
        return settings.FEISHU_WEBHOOK_TRANSPORT or settings.FEISHU_WEBHOOK_URL
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


def send_feishu_message(notification_payload: Dict) -> Dict:
    if not settings.FEISHU_NOTIFICATION_ENABLED:
        return {
            "success": False,
            "status": "disabled",
            "response_summary": "Feishu notification delivery is disabled by configuration",
        }

    webhook_url = _resolve_webhook_url(str(notification_payload.get("notification_type") or ""))
    if not webhook_url:
        return {
            "success": False,
            "status": "failed",
            "response_summary": "Feishu webhook URL is not configured",
        }

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
