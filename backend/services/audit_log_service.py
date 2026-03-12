"""Unified audit logging helpers for Tool IO workflow actions."""

from __future__ import annotations

import logging
from typing import Optional

from database import add_tool_io_log

logger = logging.getLogger(__name__)


OPERATION_CREATE = "create"
OPERATION_SUBMIT = "submit"
OPERATION_KEEPER_CONFIRM = "keeper_confirm"
OPERATION_TRANSPORT_ASSIGN = "transport_assign"
OPERATION_TRANSPORT_START = "transport_start"
OPERATION_TRANSPORT_COMPLETE = "transport_complete"
OPERATION_TRANSPORT_NOTIFY = "transport_notify"
OPERATION_LOCATION_UPDATE = "location_update"
OPERATION_FINAL_CONFIRM = "final_confirm"
OPERATION_CANCEL = "cancel"
OPERATION_REJECT = "reject"
OPERATION_SYSTEM_CORRECTION = "system_correction"


def write_order_audit_log(
    *,
    order_no: str,
    operation_type: str,
    operator_user_id: str = "",
    operator_name: str = "",
    operator_role: str = "",
    previous_status: str = "",
    new_status: str = "",
    remark: str = "",
    item_id: Optional[int] = None,
) -> bool:
    """Persist one audit log row.

    This wrapper intentionally swallows all exceptions so audit failures never
    break the main business flow.
    """
    if not order_no or not operation_type:
        logger.warning(
            "skip audit log because order_no or operation_type is missing: order_no=%s operation_type=%s",
            order_no,
            operation_type,
        )
        return False

    try:
        return bool(
            add_tool_io_log(
                {
                    "order_no": order_no,
                    "item_id": item_id,
                    "action_type": operation_type,
                    "operator_id": operator_user_id,
                    "operator_name": operator_name,
                    "operator_role": operator_role,
                    "before_status": previous_status,
                    "after_status": new_status,
                    "content": remark,
                }
            )
        )
    except Exception as exc:
        logger.error("failed to write audit log for %s: %s", order_no, exc)
        return False
