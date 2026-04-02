# -*- coding: utf-8 -*-
"""Notification helpers for inspection workflow events."""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Optional

from backend.database.repositories.inspection_task_repository import InspectionTaskRepository
from backend.services.feishu_notification_adapter import deliver_notification_to_feishu
from backend.services.notification_service import STATUS_UNREAD, create_notification_record

logger = logging.getLogger(__name__)

INSPECTION_TASK_RECEIVED = "INSPECTION_TASK_RECEIVED"
INSPECTION_REPORT_SUBMITTED = "INSPECTION_REPORT_SUBMITTED"
INSPECTION_REPORT_ACCEPTED = "INSPECTION_REPORT_ACCEPTED"
INSPECTION_REPORT_REJECTED = "INSPECTION_REPORT_REJECTED"
INSPECTION_TASK_CLOSED = "INSPECTION_TASK_CLOSED"
INSPECTION_TASK_OVERDUE = "INSPECTION_TASK_OVERDUE"
INSPECTION_PLAN_PUBLISHED = "INSPECTION_PLAN_PUBLISHED"


class InspectionNotificationService:
    """Send inspection notifications to internal records and Feishu."""

    def __init__(self, task_repo: Optional[InspectionTaskRepository] = None):
        self._task_repo = task_repo or InspectionTaskRepository()

    def notify_task_received(self, task_no: str, user_name: str) -> Dict:
        task = self._task_repo.get_task(task_no)
        if not task:
            return {"success": False, "error": "inspection task not found"}
        return self._notify_roles(
            task_no=task_no,
            notification_type=INSPECTION_TASK_RECEIVED,
            title=f"定检任务 {task_no} 已领取",
            body=f"任务 {task_no} 已由 {user_name or '未知用户'} 领取，请质量检验员跟进。",
            receivers=self._role_receivers("quality_inspector"),
            metadata={"task_no": task_no, "serial_no": task.get("serial_no", "")},
        )

    def notify_report_submitted(self, task_no: str) -> Dict:
        task = self._task_repo.get_task(task_no)
        if not task:
            return {"success": False, "error": "inspection task not found"}
        return self._notify_roles(
            task_no=task_no,
            notification_type=INSPECTION_REPORT_SUBMITTED,
            title=f"定检报告待验收 {task_no}",
            body=f"任务 {task_no} 的检测报告已提交，请质量检验员进行验收。",
            receivers=self._role_receivers("quality_inspector"),
            metadata={"task_no": task_no, "report_no": task.get("report_no", "")},
        )

    def notify_report_accepted(self, task_no: str) -> Dict:
        task = self._task_repo.get_task(task_no)
        if not task:
            return {"success": False, "error": "inspection task not found"}
        return self._notify_roles(
            task_no=task_no,
            notification_type=INSPECTION_REPORT_ACCEPTED,
            title=f"定检报告已通过 {task_no}",
            body=f"任务 {task_no} 的检测报告已验收通过，请班组长和保管员继续后续流转。",
            receivers=self._role_receivers("team_leader", "keeper"),
            metadata={"task_no": task_no, "serial_no": task.get("serial_no", "")},
        )

    def notify_report_rejected(self, task_no: str, reason: str) -> Dict:
        task = self._task_repo.get_task(task_no)
        if not task:
            return {"success": False, "error": "inspection task not found"}
        return self._notify_roles(
            task_no=task_no,
            notification_type=INSPECTION_REPORT_REJECTED,
            title=f"定检报告已驳回 {task_no}",
            body=f"任务 {task_no} 的检测报告被驳回，原因：{reason or '未填写'}。",
            receivers=self._role_receivers("team_leader"),
            metadata={"task_no": task_no, "reject_reason": reason or ""},
        )

    def notify_task_closed(self, task_no: str) -> Dict:
        task = self._task_repo.get_task(task_no)
        if not task:
            return {"success": False, "error": "inspection task not found"}
        return self._notify_roles(
            task_no=task_no,
            notification_type=INSPECTION_TASK_CLOSED,
            title=f"定检任务已关闭 {task_no}",
            body=f"任务 {task_no} 已关闭，工装 {task.get('serial_no', '-')} 的下次定检日期已更新。",
            receivers=self._role_receivers("planner"),
            metadata={"task_no": task_no, "serial_no": task.get("serial_no", "")},
        )

    def notify_overdue(self, task_no: str, overdue_hours: int) -> Dict:
        task = self._task_repo.get_task(task_no)
        if not task:
            return {"success": False, "error": "inspection task not found"}
        return self._notify_roles(
            task_no=task_no,
            notification_type=INSPECTION_TASK_OVERDUE,
            title=f"定检任务超时提醒 {task_no}",
            body=f"任务 {task_no} 自领取起已超时 {max(int(overdue_hours or 0), 0)} 小时，请尽快处理。",
            receivers=self._role_receivers("quality_inspector", "planner"),
            metadata={"task_no": task_no, "serial_no": task.get("serial_no", "")},
        )

    def notify_plan_published(self, plan_no: str, task_count: int) -> Dict:
        return self._notify_roles(
            task_no=plan_no,
            notification_type=INSPECTION_PLAN_PUBLISHED,
            title=f"定检计划已发布 {plan_no}",
            body=f"计划 {plan_no} 已发布，共生成 {max(int(task_count or 0), 0)} 条定检任务。",
            receivers=self._role_receivers("quality_inspector", "planner"),
            metadata={"plan_no": plan_no, "task_count": max(int(task_count or 0), 0)},
        )

    @staticmethod
    def _role_receivers(*roles: str) -> List[Dict[str, str]]:
        receivers: List[Dict[str, str]] = []
        for role in roles:
            normalized = str(role or "").strip().lower()
            if not normalized:
                continue
            receivers.append({"receiver": f"role:{normalized}", "display": normalized})
        return receivers

    def _notify_roles(
        self,
        *,
        task_no: str,
        notification_type: str,
        title: str,
        body: str,
        receivers: Iterable[Dict[str, str]],
        metadata: Optional[Dict] = None,
    ) -> Dict:
        deliveries: List[Dict] = []
        success = True
        for receiver in receivers:
            internal_result = create_notification_record(
                order_no=task_no,
                notification_type=notification_type,
                notify_channel="internal",
                receiver=receiver["receiver"],
                title=title,
                body=body,
                status=STATUS_UNREAD,
                metadata={"task_no": task_no, "receiver": receiver["receiver"], **(metadata or {})},
            )
            feishu_result = deliver_notification_to_feishu(
                {
                    "order_no": task_no,
                    "notification_type": notification_type,
                    "receiver": receiver["display"],
                    "title": title,
                    "body": body,
                    "copy_text": "",
                }
            )
            success = success and bool(internal_result.get("success")) and bool(feishu_result.get("success"))
            deliveries.append(
                {
                    "receiver": receiver["receiver"],
                    "internal_success": bool(internal_result.get("success")),
                    "feishu_success": bool(feishu_result.get("success")),
                    "feishu_result": feishu_result.get("send_result", ""),
                }
            )
            if not feishu_result.get("success"):
                logger.warning(
                    "inspection notification Feishu delivery failed for %s to %s: %s",
                    task_no,
                    receiver["receiver"],
                    feishu_result.get("send_result", ""),
                )
        return {"success": success, "deliveries": deliveries}
