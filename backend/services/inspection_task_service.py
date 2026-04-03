# -*- coding: utf-8 -*-
"""Service layer for inspection task workflow."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.repositories.inspection_report_repository import InspectionReportRepository
from backend.database.repositories.inspection_repository_common import decode_base64_payload
from backend.database.repositories.inspection_task_repository import InspectionTaskRepository
from backend.database.repositories.tool_inspection_status_repository import ToolInspectionStatusRepository
from backend.database.schema import (
    INSPECTION_TASK_COLUMNS,
    TABLE_NAMES,
    ensure_inspection_plan_table,
    ensure_inspection_report_table,
    ensure_inspection_task_table,
    ensure_tool_inspection_status_table,
)
from backend.services.inspection_notification_service import InspectionNotificationService
from backend.services.tool_io_service import get_order_detail

ALLOWED_TRANSITIONS = {
    "pending": {"received"},
    "received": {"outbound_created", "in_progress"},
    "outbound_created": {"outbound_completed", "received"},
    "outbound_completed": {"in_progress", "received"},
    "in_progress": {"report_submitted"},
    "report_submitted": {"accepted", "rejected"},
    "rejected": {"report_submitted"},
    "accepted": {"inbound_created"},
    "inbound_created": {"inbound_completed", "accepted"},
    "inbound_completed": {"closed"},
    "closed": set(),
}


def _ensure_inspection_schema() -> None:
    if not ensure_inspection_plan_table():
        raise RuntimeError("inspection plan table is not ready")
    if not ensure_inspection_task_table():
        raise RuntimeError("inspection task table is not ready")
    if not ensure_inspection_report_table():
        raise RuntimeError("inspection report table is not ready")
    if not ensure_tool_inspection_status_table():
        raise RuntimeError("tool inspection status table is not ready")


def _user_id(current_user: Optional[Dict]) -> str:
    return str((current_user or {}).get("user_id") or "").strip()


def _user_name(current_user: Optional[Dict]) -> str:
    return str((current_user or {}).get("display_name") or "").strip() or "system"


def _normalize_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(str(value)).date()


class InspectionTaskService:
    """Handle inspection task state machine and order linkage."""

    def __init__(
        self,
        task_repo: Optional[InspectionTaskRepository] = None,
        report_repo: Optional[InspectionReportRepository] = None,
        status_repo: Optional[ToolInspectionStatusRepository] = None,
        notification_service: Optional[InspectionNotificationService] = None,
    ):
        self._db = DatabaseManager()
        self._task_repo = task_repo or InspectionTaskRepository()
        self._report_repo = report_repo or InspectionReportRepository()
        self._status_repo = status_repo or ToolInspectionStatusRepository()
        self._notification_service = notification_service or InspectionNotificationService()

    def get_task(self, task_no: str, current_user: Optional[Dict]) -> Dict:
        _ = current_user
        _ensure_inspection_schema()
        task = self._task_repo.get_task(task_no)
        if not task:
            return {"success": False, "error": "inspection task not found"}
        task["reports"] = self._report_repo.get_reports_by_task(task_no)
        task["linked_orders"] = self._load_linked_orders(task)
        return {"success": True, "data": task}

    def list_tasks(self, filters: Dict, current_user: Optional[Dict]) -> Dict:
        _ = current_user
        _ensure_inspection_schema()
        try:
            result = self._task_repo.get_tasks(filters or {})
            return {"success": True, **result}
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("list_tasks failed: filters=%s", filters)
            raise

    def receive_task(self, task_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        self._ensure_transition(task, "received")
        updated = self._update_task(
            task_no,
            {
                "task_status": "received",
                "assigned_to_id": _user_id(current_user),
                "assigned_to_name": _user_name(current_user),
                "receive_time": datetime.now(),
                "updated_by": _user_name(current_user),
            },
        )
        self._notification_service.notify_task_received(task_no, _user_name(current_user))
        return {"success": True, "data": updated}

    def start_inspection(self, task_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        current_status = str(task.get("task_status") or "").strip()
        if current_status not in {"received", "outbound_completed"}:
            raise ValueError(f"cannot start inspection from status {current_status or '-'}")
        return {
            "success": True,
            "data": self._update_task(task_no, {"task_status": "in_progress", "updated_by": _user_name(current_user)}),
        }

    def submit_report(self, task_no: str, payload: Dict, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        self._ensure_transition(task, "report_submitted")
        attachment_data = payload.get("attachment_data")
        if attachment_data not in (None, ""):
            decode_base64_payload(str(attachment_data))

        report = self._report_repo.create_report(
            {
                "task_no": task_no,
                "inspector_id": _user_id(current_user),
                "inspector_name": _user_name(current_user),
                "inspection_date": payload.get("inspection_date") or date.today(),
                "inspection_result": str(payload.get("inspection_result") or "pass").strip() or "pass",
                "measurement_data": payload.get("measurement_data"),
                "attachment_data": attachment_data,
                "attachment_name": payload.get("attachment_name"),
                "remark": payload.get("remark"),
                "created_by": _user_name(current_user),
                "updated_by": _user_name(current_user),
            }
        )
        self._notification_service.notify_report_submitted(task_no)
        return {"success": True, "data": report}

    def accept_report(self, task_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        self._ensure_transition(task, "accepted")
        updated = self._update_task(
            task_no,
            {"task_status": "accepted", "reject_reason": None, "updated_by": _user_name(current_user)},
        )
        self._notification_service.notify_report_accepted(task_no)
        return {"success": True, "data": updated}

    def reject_report(self, task_no: str, reject_reason: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        self._ensure_transition(task, "rejected")
        reason = str(reject_reason or "").strip()
        if not reason:
            raise ValueError("reject_reason is required")

        def _tx(conn) -> None:
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
                SET [{INSPECTION_TASK_COLUMNS['task_status']}] = 'rejected',
                    [{INSPECTION_TASK_COLUMNS['reject_reason']}] = ?,
                    [{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{INSPECTION_TASK_COLUMNS['updated_by']}] = ?
                WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
                """,
                (reason, _user_name(current_user), task_no),
                fetch=False,
                conn=conn,
            )
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
                SET [{INSPECTION_TASK_COLUMNS['task_status']}] = 'report_submitted',
                    [{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{INSPECTION_TASK_COLUMNS['updated_by']}] = ?
                WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
                """,
                (_user_name(current_user), task_no),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        self._notification_service.notify_report_rejected(task_no, reason)
        return {"success": True, "data": self._task_repo.get_task(task_no)}

    def create_outbound_link(self, task_no: str, order_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        self._ensure_transition(task, "outbound_created")
        order = self._must_get_order(order_no, expected_type="outbound")
        return {
            "success": True,
            "data": self._update_task(
                task_no,
                {
                    "task_status": "outbound_created",
                    "outbound_order_no": order["order_no"],
                    "updated_by": _user_name(current_user),
                },
            ),
        }

    def create_inbound_link(self, task_no: str, order_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        self._ensure_transition(task, "inbound_created")
        order = self._must_get_order(order_no, expected_type="inbound")
        return {
            "success": True,
            "data": self._update_task(
                task_no,
                {
                    "task_status": "inbound_created",
                    "inbound_order_no": order["order_no"],
                    "updated_by": _user_name(current_user),
                },
            ),
        }

    def advance_from_outbound_completed(self, task_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        if str(task.get("task_status") or "").strip() != "outbound_created":
            raise ValueError("task is not waiting for outbound completion")
        order = self._must_get_order(str(task.get("outbound_order_no") or "").strip(), expected_type="outbound")
        if str(order.get("order_status") or "").strip() != "completed":
            raise ValueError("outbound order is not completed")

        def _tx(conn) -> None:
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
                SET [{INSPECTION_TASK_COLUMNS['task_status']}] = 'outbound_completed',
                    [{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{INSPECTION_TASK_COLUMNS['updated_by']}] = ?
                WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
                """,
                (_user_name(current_user), task_no),
                fetch=False,
                conn=conn,
            )
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
                SET [{INSPECTION_TASK_COLUMNS['task_status']}] = 'in_progress',
                    [{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{INSPECTION_TASK_COLUMNS['updated_by']}] = ?
                WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
                """,
                (_user_name(current_user), task_no),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return {"success": True, "data": self._task_repo.get_task(task_no)}

    def advance_from_inbound_completed(self, task_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        if str(task.get("task_status") or "").strip() != "inbound_created":
            raise ValueError("task is not waiting for inbound completion")
        order = self._must_get_order(str(task.get("inbound_order_no") or "").strip(), expected_type="inbound")
        if str(order.get("order_status") or "").strip() != "completed":
            raise ValueError("inbound order is not completed")
        updated = self._update_task(
            task_no,
            {"task_status": "inbound_completed", "actual_complete_time": datetime.now(), "updated_by": _user_name(current_user)},
        )
        return {"success": True, "data": updated}

    def close_task(self, task_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        self._ensure_transition(task, "closed")
        serial_no = str(task.get("serial_no") or "").strip()
        status_snapshot = self._status_repo.get_status(serial_no)
        cycle_days = int(status_snapshot.get("inspection_cycle_days") or 0)
        last_inspection_date = date.today()
        next_inspection_date = (
            last_inspection_date + timedelta(days=cycle_days)
            if cycle_days > 0
            else _normalize_date(task.get("next_inspection_date")) or last_inspection_date
        )
        updated_by = _user_name(current_user)

        updated = self._update_task(
            task_no,
            {
                "task_status": "closed",
                "actual_complete_time": datetime.now(),
                "next_inspection_date": next_inspection_date,
                "updated_by": updated_by,
            },
        )
        self._status_repo.upsert_status(
            serial_no,
            {
                "tool_name": task.get("tool_name"),
                "drawing_no": task.get("drawing_no"),
                "last_inspection_date": last_inspection_date,
                "next_inspection_date": next_inspection_date,
                "inspection_cycle_days": cycle_days or None,
                "inspection_status": "normal",
                "remark": task.get("remark"),
                "updated_by": updated_by,
            },
        )
        self._notification_service.notify_task_closed(task_no)
        return {"success": True, "data": updated}

    def get_linked_orders(self, task_no: str) -> Dict:
        _ensure_inspection_schema()
        task = self._must_get_task(task_no)
        return {"success": True, "data": self._load_linked_orders(task)}

    def link_order_to_task(self, order_no: str, task_no: str) -> Dict:
        _ensure_inspection_schema()
        order = self._must_get_order(order_no)
        if str(order.get("order_type") or "").strip() == "outbound":
            return self.create_outbound_link(task_no, order_no, None)
        if str(order.get("order_type") or "").strip() == "inbound":
            return self.create_inbound_link(task_no, order_no, None)
        return {"success": False, "error": "unsupported order type"}

    def check_and_advance_by_order_status(self, order_no: str) -> Dict:
        _ensure_inspection_schema()
        order = self._must_get_order(order_no)
        tasks = self._find_tasks_by_order(order_no)
        results: List[Dict] = []
        order_type = str(order.get("order_type") or "").strip()
        order_status = str(order.get("order_status") or "").strip()
        for task in tasks:
            task_no = str(task.get("task_no") or "").strip()
            if order_type == "outbound" and order_status == "completed":
                results.append(self.advance_from_outbound_completed(task_no, None))
                continue
            if order_type == "inbound" and order_status == "completed":
                results.append(self.advance_from_inbound_completed(task_no, None))
                continue
            if order_type == "outbound" and order_status in {"cancelled", "rejected"}:
                results.append(
                    {
                        "success": True,
                        "data": self._update_task(task_no, {"task_status": "received", "outbound_order_no": None, "updated_by": "system"}),
                        "rolled_back": True,
                    }
                )
                continue
            if order_type == "inbound" and order_status in {"cancelled", "rejected"}:
                results.append(
                    {
                        "success": True,
                        "data": self._update_task(task_no, {"task_status": "accepted", "inbound_order_no": None, "updated_by": "system"}),
                        "rolled_back": True,
                    }
                )
        return {"success": True, "data": results}

    def get_overdue_tasks(self) -> Dict:
        _ensure_inspection_schema()
        rows = self._task_repo.get_overdue_tasks()
        return {"success": True, "data": rows, "total": len(rows)}

    def get_status_by_serial_no(self, serial_no: str) -> Dict:
        _ensure_inspection_schema()
        status = self._status_repo.get_status(serial_no)
        if not status:
            return {"success": False, "error": "inspection status not found"}
        return {"success": True, "data": status}

    def reschedule_task(self, task_no: str, new_deadline: str, current_user: Optional[Dict]) -> Dict:
        try:
            _ensure_inspection_schema()
            task = self._must_get_task(task_no)
            current_status = str(task.get("task_status") or "").strip()
            if current_status not in {"pending"}:
                return {"success": False, "error": f"cannot reschedule task in status '{current_status}', only pending tasks can be rescheduled"}
            updated = self._update_task(
                task_no,
                {
                    "deadline": new_deadline,
                    "updated_by": _user_name(current_user),
                },
            )
            return {"success": True, "data": updated}
        except RuntimeError as exc:
            # Schema init failed — this is a system error, not a business logic error
            raise
        except ValueError as exc:
            # Task not found or business rule violation
            raise
        except Exception as exc:
            # Unexpected system error
            raise

    def _must_get_task(self, task_no: str) -> Dict:
        task = self._task_repo.get_task(task_no)
        if not task:
            raise ValueError("inspection task not found")
        return task

    @staticmethod
    def _must_get_order(order_no: str, expected_type: str = "") -> Dict:
        order = get_order_detail(order_no)
        if not order:
            raise ValueError("tool io order not found")
        if expected_type and str(order.get("order_type") or "").strip() != expected_type:
            raise ValueError(f"tool io order must be {expected_type}")
        return order

    @staticmethod
    def _ensure_transition(task: Dict, target_status: str) -> None:
        current_status = str(task.get("task_status") or "").strip()
        if target_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
            raise ValueError(f"invalid state transition: {current_status or '-'} -> {target_status}")

    def _update_task(self, task_no: str, fields: Dict) -> Dict:
        assignments: List[str] = []
        params: List[object] = []
        allowed_fields = {
            "task_status": INSPECTION_TASK_COLUMNS["task_status"],
            "assigned_to_id": INSPECTION_TASK_COLUMNS["assigned_to_id"],
            "assigned_to_name": INSPECTION_TASK_COLUMNS["assigned_to_name"],
            "receive_time": INSPECTION_TASK_COLUMNS["receive_time"],
            "outbound_order_no": INSPECTION_TASK_COLUMNS["outbound_order_no"],
            "inbound_order_no": INSPECTION_TASK_COLUMNS["inbound_order_no"],
            "inspection_result": INSPECTION_TASK_COLUMNS["inspection_result"],
            "reject_reason": INSPECTION_TASK_COLUMNS["reject_reason"],
            "report_no": INSPECTION_TASK_COLUMNS["report_no"],
            "next_inspection_date": INSPECTION_TASK_COLUMNS["next_inspection_date"],
            "actual_complete_time": INSPECTION_TASK_COLUMNS["actual_complete_time"],
            "deadline": INSPECTION_TASK_COLUMNS["deadline"],
            "updated_by": INSPECTION_TASK_COLUMNS["updated_by"],
        }
        for key, column in allowed_fields.items():
            if key in fields:
                assignments.append(f"[{column}] = ?")
                params.append(fields.get(key))
        assignments.append(f"[{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME()")
        params.append(task_no)
        self._db.execute_query(
            f"""
            UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
            SET {", ".join(assignments)}
            WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
            """,
            tuple(params),
            fetch=False,
        )
        return self._task_repo.get_task(task_no)

    def _load_linked_orders(self, task: Dict) -> List[Dict]:
        orders: List[Dict] = []
        for key in ("outbound_order_no", "inbound_order_no"):
            order_no = str(task.get(key) or "").strip()
            if not order_no:
                continue
            order = get_order_detail(order_no)
            if order:
                orders.append(order)
        return orders

    def _find_tasks_by_order(self, order_no: str) -> List[Dict]:
        return self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['INSPECTION_TASK']}]
            WHERE [{INSPECTION_TASK_COLUMNS['outbound_order_no']}] = ?
               OR [{INSPECTION_TASK_COLUMNS['inbound_order_no']}] = ?
            ORDER BY [{INSPECTION_TASK_COLUMNS['updated_at']}] DESC
            """,
            (order_no, order_no),
        )


_TASK_SERVICE = InspectionTaskService()


def get_task(task_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.get_task(task_no, current_user)


def list_tasks(filters: Dict, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.list_tasks(filters, current_user)


def receive_task(task_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.receive_task(task_no, current_user)


def start_inspection(task_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.start_inspection(task_no, current_user)


def submit_report(task_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.submit_report(task_no, payload, current_user)


def accept_report(task_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.accept_report(task_no, current_user)


def reject_report(task_no: str, reject_reason: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.reject_report(task_no, reject_reason, current_user)


def create_outbound_link(task_no: str, order_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.create_outbound_link(task_no, order_no, current_user)


def create_inbound_link(task_no: str, order_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.create_inbound_link(task_no, order_no, current_user)


def advance_from_outbound_completed(task_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.advance_from_outbound_completed(task_no, current_user)


def advance_from_inbound_completed(task_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.advance_from_inbound_completed(task_no, current_user)


def close_task(task_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.close_task(task_no, current_user)


def get_linked_orders(task_no: str) -> Dict:
    return _TASK_SERVICE.get_linked_orders(task_no)


def link_order_to_task(order_no: str, task_no: str) -> Dict:
    return _TASK_SERVICE.link_order_to_task(order_no, task_no)


def check_and_advance_by_order_status(order_no: str) -> Dict:
    return _TASK_SERVICE.check_and_advance_by_order_status(order_no)


def get_overdue_tasks() -> Dict:
    return _TASK_SERVICE.get_overdue_tasks()


def get_status_by_serial_no(serial_no: str) -> Dict:
    return _TASK_SERVICE.get_status_by_serial_no(serial_no)


def reschedule_task(task_no: str, new_deadline: str, current_user: Optional[Dict] = None) -> Dict:
    return _TASK_SERVICE.reschedule_task(task_no, new_deadline, current_user)
