# -*- coding: utf-8 -*-
"""Transport issue business service."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from backend.database.repositories.transport_issue_repository import TransportIssueRepository
from backend.database.schema.schema_manager import ensure_transport_issue_table
from backend.services.audit_log_service import write_order_audit_log

logger = logging.getLogger(__name__)

ALLOWED_ISSUE_TYPES = {"tool_damaged", "quantity_mismatch", "location_error", "other"}
MAX_DESCRIPTION_LEN = 500
MAX_HANDLE_REPLY_LEN = 500


def report_transport_issue(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    ensure_transport_issue_table()
    order = _get_order_for_scope(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    issue_type = str(payload.get("issue_type", "")).strip()
    if issue_type not in ALLOWED_ISSUE_TYPES:
        return {"success": False, "error": "issue_type must be one of: tool_damaged, quantity_mismatch, location_error, other"}

    description = str(payload.get("description", "") or "").strip()
    if len(description) > MAX_DESCRIPTION_LEN:
        return {"success": False, "error": f"description length must be <= {MAX_DESCRIPTION_LEN}"}

    image_urls = payload.get("image_urls", [])
    if image_urls is None:
        image_urls = []
    if not isinstance(image_urls, list):
        return {"success": False, "error": "image_urls must be an array"}
    normalized_urls = [str(url).strip() for url in image_urls if str(url).strip()]

    user = current_user or {}
    reporter_id = str(user.get("user_id", "")).strip()
    reporter_name = str(user.get("display_name", "")).strip()
    result = TransportIssueRepository().create_issue(
        order_no=order_no,
        issue_type=issue_type,
        description=description,
        image_urls=normalized_urls,
        reporter_id=reporter_id,
        reporter_name=reporter_name,
    )
    if not result.get("success"):
        return result

    write_order_audit_log(
        order_no=order_no,
        operation_type="transport_issue_report",
        operator_user_id=reporter_id,
        operator_name=reporter_name,
        operator_role="production_prep",
        previous_status="",
        new_status="pending",
        remark=f"report transport issue: type={issue_type}, issue_id={result.get('issue_id', 0)}",
    )
    return {"success": True, "issue_id": result.get("issue_id", 0), "message": "异常已上报"}


def get_transport_issues(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    ensure_transport_issue_table()
    order = _get_order_for_scope(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}
    issues = TransportIssueRepository().get_issues_by_order(order_no)
    return {"success": True, "data": issues}


def resolve_transport_issue(order_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    ensure_transport_issue_table()
    order = _get_order_for_scope(order_no, current_user=current_user)
    if not order:
        return {"success": False, "error": "order not found"}

    issue_id = payload.get("issue_id")
    try:
        normalized_issue_id = int(issue_id)
    except (TypeError, ValueError):
        return {"success": False, "error": "issue_id must be an integer"}
    if normalized_issue_id <= 0:
        return {"success": False, "error": "issue_id must be greater than 0"}

    handle_reply = str(payload.get("handle_reply", "") or "").strip()
    if not handle_reply:
        return {"success": False, "error": "handle_reply is required"}
    if len(handle_reply) > MAX_HANDLE_REPLY_LEN:
        return {"success": False, "error": f"handle_reply length must be <= {MAX_HANDLE_REPLY_LEN}"}

    user = current_user or {}
    handler_id = str(user.get("user_id", "")).strip()
    handler_name = str(user.get("display_name", "")).strip()
    result = TransportIssueRepository().resolve_issue(
        order_no=order_no,
        issue_id=normalized_issue_id,
        handle_reply=handle_reply,
        handler_id=handler_id,
        handler_name=handler_name,
    )
    if not result.get("success"):
        return result

    write_order_audit_log(
        order_no=order_no,
        operation_type="transport_issue_resolve",
        operator_user_id=handler_id,
        operator_name=handler_name,
        operator_role="keeper",
        previous_status="pending",
        new_status="resolved",
        remark=f"resolved transport issue: issue_id={normalized_issue_id}",
    )
    return {"success": True, "message": "异常已处理"}


def _get_order_for_scope(order_no: str, current_user: Optional[Dict] = None) -> Dict:
    from backend.services.tool_io_service import get_order_detail

    return get_order_detail(order_no, current_user=current_user) or {}
