# -*- coding: utf-8 -*-
"""
Service wrappers for Tool IO backend flows.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from database import (
    DatabaseManager,
    ToolIOAction,
    add_tool_io_log,
    add_tool_io_notification,
    cancel_tool_io_order,
    create_tool_io_order,
    ensure_tool_io_tables,
    final_confirm_order,
    get_tool_io_orders,
    reject_tool_io_order,
    search_tools,
    submit_tool_io_order,
    update_notification_status,
)
from backend.services.tool_io_runtime import (
    get_order_detail_runtime,
    get_order_logs_runtime,
    keeper_confirm_runtime,
    list_pending_keeper_orders,
)
from utils.feishu_api import FeishuBase


def create_order(payload: Dict) -> Dict:
    ensure_tool_io_tables()
    return create_tool_io_order(payload)


def list_orders(filters: Dict) -> Dict:
    return get_tool_io_orders(
        order_type=filters.get("order_type"),
        order_status=filters.get("order_status"),
        initiator_id=filters.get("initiator_id"),
        keeper_id=filters.get("keeper_id"),
        keyword=filters.get("keyword"),
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
        page_no=filters.get("page_no", 1),
        page_size=filters.get("page_size", 20),
    )


def get_order_detail(order_no: str) -> Dict:
    return get_order_detail_runtime(order_no)


def submit_order(order_no: str, payload: Dict) -> Dict:
    return submit_tool_io_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )


def keeper_confirm(order_no: str, payload: Dict) -> Dict:
    confirm_data = {
        "transport_type": payload.get("transport_type"),
        "transport_assignee_id": payload.get("transport_assignee_id"),
        "transport_assignee_name": payload.get("transport_assignee_name"),
        "keeper_remark": payload.get("keeper_remark"),
        "items": payload.get("items"),
    }
    return keeper_confirm_runtime(
        order_no=order_no,
        keeper_id=payload.get("keeper_id", ""),
        keeper_name=payload.get("keeper_name", ""),
        confirm_data=confirm_data,
        operator_id=payload.get("operator_id", payload.get("keeper_id", "")),
        operator_name=payload.get("operator_name", payload.get("keeper_name", "")),
        operator_role=payload.get("operator_role", "keeper"),
    )


def final_confirm(order_no: str, payload: Dict) -> Dict:
    availability = get_final_confirm_availability(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_role", ""),
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

    detail = get_order_detail_runtime(order_no)
    return {
        **result,
        "available": False,
        "data": detail,
        "order_type": availability.get("order_type"),
        "before_status": availability.get("current_status"),
        "after_status": "completed",
    }


def get_final_confirm_availability(order_no: str, operator_id: str = "", operator_role: str = "") -> Dict:
    order = _get_runtime_order_summary(order_no)
    if not order:
        return {"success": False, "error": "order not found", "available": False}

    availability = _evaluate_final_confirm_availability(order, operator_id, operator_role)
    return {"success": True, **availability}


def reject_order(order_no: str, payload: Dict) -> Dict:
    return reject_tool_io_order(
        order_no,
        payload.get("reject_reason", ""),
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )


def cancel_order(order_no: str, payload: Dict) -> Dict:
    return cancel_tool_io_order(
        order_no,
        payload.get("operator_id", ""),
        payload.get("operator_name", ""),
        payload.get("operator_role", ""),
    )


def get_order_logs(order_no: str) -> List[Dict]:
    return get_order_logs_runtime(order_no)


def get_pending_keeper_list(keeper_id: str = None) -> List[Dict]:
    return list_pending_keeper_orders(keeper_id)


def get_notification_records(order_no: str) -> Dict:
    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found", "data": []}
    return {"success": True, "data": order.get("notification_records", [])}


def _pick_value(record: Dict, keys: List[str], default: Optional[str] = ""):
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default


def _get_runtime_order_summary(order_no: str) -> Optional[Dict]:
    order = get_order_detail_runtime(order_no)
    if not order:
        return None

    return {
        "order_no": _pick_value(order, ["order_no", "é—å‘ŠåžµéŽ¼î‚¦å´£é¡æ¨»å„Ÿé–¹æƒ§å•¿ç»€å¬®æŸ›?"], order_no),
        "order_type": _pick_value(order, ["order_type", "é—å‘Šîš†å¨²æ¨ºç•µæµ£è™¹å°µé å›ªå°™éˆ§?"]),
        "order_status": _pick_value(order, ["order_status", "é—å‘Šîš†å¨²æ¨ºç•µæ¸šâ‚¬éŽ®â•…æ‡œçº°æ¨ºäº¾?"]),
        "initiator_id": _pick_value(order, ["initiator_id", "é—å‘Šç‘¦é¨å¥¸å¹‘é”å—™î›²ç¼â„ƒå¢¬"]),
        "keeper_id": _pick_value(order, ["keeper_id", "æ¿žï½…æ´¦ç»»å‹¯î”˜éŽ¼ä½¸å·æ¿¡ã‚‡æ‹"]),
        "approved_count": _pick_value(order, ["approved_count", "éŽè§„ç“•çæ¬“åž¾å¦¯å…¼åª¼é–µå æ£™å¨ˆå •æ¢º?"], 0),
    }


def _evaluate_final_confirm_availability(order: Dict, operator_id: str, operator_role: str) -> Dict:
    current_status = order.get("order_status") or ""
    order_type = order.get("order_type") or ""
    allowed_statuses = {"transport_notified", "final_confirmation_pending"}

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
    return add_tool_io_notification(
        {
            "order_no": order_no,
            "notify_type": notify_type,
            "notify_channel": notify_channel,
            "receiver": receiver,
            "title": title,
            "content": content,
            "copy_text": copy_text,
        }
    )


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


def generate_keeper_text(order_no: str) -> Dict:
    order = get_order_detail_runtime(order_no)
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
        "UPDATE å®¸ãƒ¨î—Šé‘å“„å†æ´æ’³å´Ÿ_æ¶“æ˜ã€ƒ SET æ·‡æ¿ˆî…¸é›æ©€æ¸¶å§¹å‚›æžƒéˆ? = ?, æ·‡î†½æ•¼éƒå •æ£¿ = GETDATE() WHERE é‘å“„å†æ´æ’³å´Ÿé™? = ?",
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


def generate_transport_text(order_no: str) -> Dict:
    order = get_order_detail_runtime(order_no)
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
        UPDATE å®¸ãƒ¨î—Šé‘å“„å†æ´æ’³å´Ÿ_æ¶“æ˜ã€ƒ
        SET æ©æ„¯ç·­é–«æ°±ç…¡é‚å›¨æ¹° = ?, å¯°î†»ä¿Šæ¾¶å¶…åŸ—é‚å›¨æ¹° = ?, æ·‡î†½æ•¼éƒå •æ£¿ = GETDATE()
        WHERE é‘å“„å†æ´æ’³å´Ÿé™? = ?
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


def notify_transport(order_no: str, payload: Dict) -> Dict:
    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found"}

    current_status = _pick_value(order, ["order_status", "é—æ›Ÿåµé˜èˆµâ‚¬?"], "")
    if current_status not in {"keeper_confirmed", "partially_confirmed", "transport_notified"}:
        return {
            "success": False,
            "error": f"current status does not allow transport notification: {current_status}",
        }

    generated = generate_transport_text(order_no)
    if not generated.get("success"):
        return generated

    summary = _extract_order_values(order)
    notify_type = payload.get("notify_type", "transport_notice")
    notify_channel = payload.get("notify_channel", "feishu")
    receiver = payload.get("receiver") or summary["transport_receiver"]
    title = payload.get("title") or "Transport notification"
    content = payload.get("content") or generated["text"]
    copy_text = payload.get("copy_text") or generated["wechat_text"]

    notify_id = add_tool_io_notification(
        {
            "order_no": order_no,
            "notify_type": notify_type,
            "notify_channel": notify_channel,
            "receiver": receiver,
            "title": title,
            "content": content,
            "copy_text": copy_text,
        }
    )
    if not notify_id:
        return {"success": False, "error": "failed to create notification record"}

    # Try to send via Feishu
    feishu_sent = False
    feishu_error = None
    webhook_url = os.getenv("FEISHU_WEBHOOK_TRANSPORT") or os.getenv("FEISHU_WEBHOOK_URL")

    if webhook_url:
        try:
            feishu = FeishuBase()
            feishu_sent = feishu.send_webhook_message(webhook_url, content, "text")
            if not feishu_sent:
                feishu_error = "Feishu webhook returned non-zero code"
        except Exception as e:
            feishu_error = str(e)
    else:
        feishu_error = "Feishu webhook URL not configured"

    # Update notification record with send result
    if feishu_sent:
        final_status = "sent"
        send_result = "Feishu notification sent successfully"
    else:
        final_status = "failed"
        send_result = f"Feishu send failed: {feishu_error or 'unknown error'}"

    update_notification_status(notify_id, final_status, send_result)

    if not feishu_sent:
        add_tool_io_log(
            {
                "order_no": order_no,
                "action_type": ToolIOAction.NOTIFY,
                "operator_id": payload.get("operator_id", ""),
                "operator_name": payload.get("operator_name", summary["keeper_name"]),
                "operator_role": payload.get("operator_role", "keeper"),
                "before_status": current_status,
                "after_status": current_status,
                "content": f"Transport notification failed, channel: {notify_channel}, status: {final_status}",
            }
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
    add_tool_io_log(
        {
            "order_no": order_no,
            "action_type": ToolIOAction.NOTIFY,
            "operator_id": payload.get("operator_id", ""),
            "operator_name": payload.get("operator_name", summary["keeper_name"]),
            "operator_role": payload.get("operator_role", "keeper"),
            "before_status": current_status,
            "after_status": "transport_notified",
            "content": f"Transport notification sent, channel: {notify_channel}, status: {final_status}",
        }
    )
    return {
        "success": True,
        "notify_id": notify_id,
        "send_status": final_status,
        "send_result": send_result,
        "wechat_text": copy_text,
    }


def notify_keeper(order_no: str, payload: Dict) -> Dict:
    """Send keeper request notification via Feishu."""
    order = get_order_detail_runtime(order_no)
    if not order:
        return {"success": False, "error": "order not found"}

    current_status = _pick_value(order, ["order_status", "é æŸ ¬é ˜èˆ¢?"], "")
    if current_status not in {"submitted", "keeper_confirmed"}:
        return {
            "success": False,
            "error": f"current status does not allow keeper notification: {current_status}",
        }

    generated = generate_keeper_text(order_no)
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
    try:
        db = DatabaseManager()
        result = db.execute_query(
            """
            SELECT id FROM 工装出入库单_通知记录
            WHERE 出入库单号 = ? AND 通知类型 = 'keeper_request'
            ORDER BY 创建时间 DESC
            """,
            (order_no,),
        )
        notify_id = result[0][0] if result else 0
    except Exception:
        notify_id = 0

    if not notify_id:
        # Create a new notification record if none exists
        notify_id = add_tool_io_notification(
            {
                "order_no": order_no,
                "notify_type": notify_type,
                "notify_channel": notify_channel,
                "receiver": receiver,
                "title": title,
                "content": content,
                "copy_text": "",
            }
        )

    if not notify_id:
        return {"success": False, "error": "failed to create notification record"}

    # Try to send via Feishu
    feishu_sent = False
    feishu_error = None
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")

    if webhook_url:
        try:
            feishu = FeishuBase()
            feishu_sent = feishu.send_webhook_message(webhook_url, content, "text")
            if not feishu_sent:
                feishu_error = "Feishu webhook returned non-zero code"
        except Exception as e:
            feishu_error = str(e)
    else:
        feishu_error = "Feishu webhook URL not configured"

    # Update notification record with send result
    if feishu_sent:
        final_status = "sent"
        send_result = "Feishu notification sent successfully"
    else:
        final_status = "failed"
        send_result = f"Feishu send failed: {feishu_error or 'unknown error'}"

    update_notification_status(notify_id, final_status, send_result)

    add_tool_io_log(
        {
            "order_no": order_no,
            "action_type": ToolIOAction.NOTIFY,
            "operator_id": payload.get("operator_id", ""),
            "operator_name": payload.get("operator_name", summary["initiator_name"]),
            "operator_role": payload.get("operator_role", "initiator"),
            "before_status": current_status,
            "after_status": current_status,
            "content": f"Keeper notification sent via {notify_channel}, status: {final_status}",
        }
    )
    return {
        "success": True,
        "notify_id": notify_id,
        "send_status": final_status,
        "send_result": send_result,
    }
