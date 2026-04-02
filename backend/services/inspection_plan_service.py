# -*- coding: utf-8 -*-
"""Service layer for inspection plan workflow."""

from __future__ import annotations

import calendar
from datetime import date, datetime
from typing import Dict, Optional

from backend.database.repositories.inspection_plan_repository import InspectionPlanRepository
from backend.database.repositories.inspection_task_repository import InspectionTaskRepository
from backend.database.repositories.tool_inspection_status_repository import ToolInspectionStatusRepository
from backend.database.schema import (
    ensure_inspection_plan_table,
    ensure_inspection_report_table,
    ensure_inspection_task_table,
    ensure_tool_inspection_status_table,
)
from backend.services.inspection_notification_service import InspectionNotificationService


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


class InspectionPlanService:
    """Handle inspection plan business rules."""

    def __init__(
        self,
        plan_repo: Optional[InspectionPlanRepository] = None,
        task_repo: Optional[InspectionTaskRepository] = None,
        status_repo: Optional[ToolInspectionStatusRepository] = None,
        notification_service: Optional[InspectionNotificationService] = None,
    ):
        self._plan_repo = plan_repo or InspectionPlanRepository()
        self._task_repo = task_repo or InspectionTaskRepository()
        self._status_repo = status_repo or ToolInspectionStatusRepository()
        self._notification_service = notification_service or InspectionNotificationService()

    def create_plan(self, payload: Dict, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        normalized = self._validate_plan_payload(payload, require_name=True)
        normalized["creator_id"] = _user_id(current_user)
        normalized["creator_name"] = _user_name(current_user)
        normalized["created_by"] = _user_name(current_user)
        normalized["updated_by"] = _user_name(current_user)
        return {"success": True, "data": self._plan_repo.create_plan(normalized)}

    def get_plan(self, plan_no: str, current_user: Optional[Dict]) -> Dict:
        _ = current_user
        _ensure_inspection_schema()
        plan = self._plan_repo.get_plan(plan_no)
        if not plan:
            return {"success": False, "error": "inspection plan not found"}
        return {"success": True, "data": plan}

    def list_plans(self, filters: Dict, current_user: Optional[Dict]) -> Dict:
        _ = current_user
        _ensure_inspection_schema()
        return {"success": True, **self._plan_repo.get_plans(filters or {})}

    def update_plan(self, plan_no: str, payload: Dict, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        existing = self._plan_repo.get_plan(plan_no)
        if not existing:
            return {"success": False, "error": "inspection plan not found"}
        if str(existing.get("status") or "").strip() != "draft":
            return {"success": False, "error": "only draft plan can be updated"}

        normalized = self._validate_plan_payload(payload, require_name=False)
        normalized["updated_by"] = _user_name(current_user)
        return {"success": True, "data": self._plan_repo.update_plan(plan_no, normalized)}

    def publish_plan(self, plan_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        existing = self._plan_repo.get_plan(plan_no)
        if not existing:
            return {"success": False, "error": "inspection plan not found"}
        if str(existing.get("status") or "").strip() != "draft":
            return {"success": False, "error": "only draft plan can be published"}

        result = self._plan_repo.publish_plan(plan_no)
        if not result.get("success"):
            return result
        self._notification_service.notify_plan_published(plan_no, int(result.get("generated_task_count", 0)))
        return {"success": True, "data": result}

    def preview_tasks(self, plan_no: str, current_user: Optional[Dict]) -> Dict:
        _ = current_user
        _ensure_inspection_schema()
        plan = self._plan_repo.get_plan(plan_no)
        if not plan:
            return {"success": False, "error": "inspection plan not found"}

        plan_deadline = self._plan_deadline(plan)
        today = date.today()
        days_before = max((plan_deadline.date() - today).days, 1)
        expiring_tools = self._status_repo.get_expiring_tools(days_before=days_before)
        overdue_tools = self._status_repo.get_overdue_tools()

        merged = {}
        for row in expiring_tools + overdue_tools:
            serial_no = str(row.get("serial_no") or "").strip()
            next_date = row.get("next_inspection_date")
            if not serial_no:
                continue
            if next_date and hasattr(next_date, "date"):
                next_date = next_date.date()
            if next_date and next_date > plan_deadline.date():
                continue
            merged[serial_no] = row

        data = sorted(
            merged.values(),
            key=lambda item: (
                item.get("next_inspection_date") or date.max,
                str(item.get("serial_no") or ""),
            ),
        )
        return {"success": True, "data": data, "total": len(data)}

    def close_plan(self, plan_no: str, current_user: Optional[Dict]) -> Dict:
        _ensure_inspection_schema()
        existing = self._plan_repo.get_plan(plan_no)
        if not existing:
            return {"success": False, "error": "inspection plan not found"}
        if str(existing.get("status") or "").strip() == "closed":
            return {"success": True, "data": existing}

        task_rows = self._task_repo.get_tasks({"plan_no": plan_no, "page_no": 1, "page_size": 1000}).get("data", [])
        if any(str(row.get("task_status") or "").strip() != "closed" for row in task_rows):
            return {"success": False, "error": "inspection plan still has open tasks"}

        updated = self._plan_repo.update_plan(plan_no, {"status": "closed", "updated_by": _user_name(current_user)})
        return {"success": True, "data": updated}

    @staticmethod
    def _plan_deadline(plan: Dict) -> datetime:
        year = int(plan.get("plan_year") or datetime.now().year)
        month = int(plan.get("plan_month") or datetime.now().month)
        last_day = calendar.monthrange(year, month)[1]
        return datetime(year, month, last_day, 23, 59, 59)

    @staticmethod
    def _validate_plan_payload(payload: Dict, *, require_name: bool) -> Dict:
        plan_name = str(payload.get("plan_name") or "").strip()
        if require_name and not plan_name:
            raise ValueError("plan_name is required")
        plan_year = int(payload.get("plan_year") or datetime.now().year)
        plan_month = int(payload.get("plan_month") or datetime.now().month)
        if plan_month < 1 or plan_month > 12:
            raise ValueError("plan_month must be between 1 and 12")
        normalized = {
            "plan_name": plan_name,
            "plan_year": plan_year,
            "plan_month": plan_month,
            "inspection_type": str(payload.get("inspection_type") or "regular").strip() or "regular",
            "status": str(payload.get("status") or "draft").strip() or "draft",
            "remark": payload.get("remark"),
        }
        return {key: value for key, value in normalized.items() if value not in ("", None)}


_PLAN_SERVICE = InspectionPlanService()


def create_plan(payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    return _PLAN_SERVICE.create_plan(payload, current_user)


def get_plan(plan_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _PLAN_SERVICE.get_plan(plan_no, current_user)


def list_plans(filters: Dict, current_user: Optional[Dict] = None) -> Dict:
    return _PLAN_SERVICE.list_plans(filters, current_user)


def update_plan(plan_no: str, payload: Dict, current_user: Optional[Dict] = None) -> Dict:
    return _PLAN_SERVICE.update_plan(plan_no, payload, current_user)


def publish_plan(plan_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _PLAN_SERVICE.publish_plan(plan_no, current_user)


def preview_tasks(plan_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _PLAN_SERVICE.preview_tasks(plan_no, current_user)


def close_plan(plan_no: str, current_user: Optional[Dict] = None) -> Dict:
    return _PLAN_SERVICE.close_plan(plan_no, current_user)
