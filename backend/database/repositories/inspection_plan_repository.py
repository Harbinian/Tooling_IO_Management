# -*- coding: utf-8 -*-
"""Repository for inspection plan persistence."""

from __future__ import annotations

import calendar
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.repositories.inspection_repository_common import generate_inspection_no_atomic
from backend.database.schema.column_names import (
    INSPECTION_PLAN_COLUMNS,
    INSPECTION_TASK_COLUMNS,
    TABLE_NAMES,
    TOOL_INSPECTION_STATUS_COLUMNS,
)


class InspectionPlanRepository:
    """Persist inspection plans and plan-driven task generation."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def create_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        plan_no = str(plan_data.get("plan_no") or "").strip() or generate_inspection_no_atomic("DJP")
        creator_name = str(plan_data.get("creator_name") or "").strip()
        self._db.execute_query(
            f"""
            INSERT INTO [{TABLE_NAMES['INSPECTION_PLAN']}] (
                [{INSPECTION_PLAN_COLUMNS['plan_no']}],
                [{INSPECTION_PLAN_COLUMNS['plan_name']}],
                [{INSPECTION_PLAN_COLUMNS['plan_year']}],
                [{INSPECTION_PLAN_COLUMNS['plan_month']}],
                [{INSPECTION_PLAN_COLUMNS['inspection_type']}],
                [{INSPECTION_PLAN_COLUMNS['status']}],
                [{INSPECTION_PLAN_COLUMNS['creator_id']}],
                [{INSPECTION_PLAN_COLUMNS['creator_name']}],
                [{INSPECTION_PLAN_COLUMNS['remark']}],
                [{INSPECTION_PLAN_COLUMNS['created_at']}],
                [{INSPECTION_PLAN_COLUMNS['updated_at']}],
                [{INSPECTION_PLAN_COLUMNS['created_by']}],
                [{INSPECTION_PLAN_COLUMNS['updated_by']}]
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), SYSDATETIME(), ?, ?)
            """,
            (
                plan_no,
                str(plan_data.get("plan_name") or "").strip(),
                int(plan_data.get("plan_year") or 0),
                int(plan_data.get("plan_month") or 0),
                str(plan_data.get("inspection_type") or "regular").strip(),
                str(plan_data.get("status") or "draft").strip(),
                str(plan_data.get("creator_id") or "").strip(),
                creator_name,
                plan_data.get("remark"),
                str(plan_data.get("created_by") or creator_name or "system").strip(),
                str(plan_data.get("updated_by") or creator_name or "system").strip(),
            ),
            fetch=False,
        )
        return self.get_plan(plan_no)

    def get_plan(self, plan_no: str) -> Dict[str, Any]:
        rows = self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['INSPECTION_PLAN']}]
            WHERE [{INSPECTION_PLAN_COLUMNS['plan_no']}] = ?
            """,
            (str(plan_no or "").strip(),),
        )
        if not rows:
            return {}

        plan = rows[0]
        task_rows = self._db.execute_query(
            f"""
            SELECT COUNT(1) AS total_count
            FROM [{TABLE_NAMES['INSPECTION_TASK']}]
            WHERE [{INSPECTION_TASK_COLUMNS['plan_no']}] = ?
            """,
            (str(plan_no or "").strip(),),
        )
        plan["task_count"] = int((task_rows[0] if task_rows else {}).get("total_count", 0))
        return plan

    def get_plans(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        filters = filters or {}
        page_no = max(int(filters.get("page_no") or 1), 1)
        page_size = max(int(filters.get("page_size") or 20), 1)
        offset = (page_no - 1) * page_size

        conditions = ["1=1"]
        params: List[Any] = []
        for key in ("status", "plan_year", "plan_month", "creator_id", "inspection_type"):
            value = filters.get(key)
            if value not in (None, ""):
                conditions.append(f"p.[{INSPECTION_PLAN_COLUMNS[key]}] = ?")
                params.append(value)

        keyword = str(filters.get("keyword") or "").strip()
        if keyword:
            conditions.append(
                f"""(
                    p.[{INSPECTION_PLAN_COLUMNS['plan_no']}] LIKE ?
                    OR p.[{INSPECTION_PLAN_COLUMNS['plan_name']}] LIKE ?
                    OR p.[{INSPECTION_PLAN_COLUMNS['creator_name']}] LIKE ?
                )"""
            )
            params.extend([f"%{keyword}%"] * 3)

        where_clause = " AND ".join(conditions)
        total_rows = self._db.execute_query(
            f"""
            SELECT COUNT(1) AS total
            FROM [{TABLE_NAMES['INSPECTION_PLAN']}] AS p
            WHERE {where_clause}
            """,
            tuple(params),
        )
        total = int((total_rows[0] if total_rows else {}).get("total", 0))

        rows = self._db.execute_query(
            f"""
            SELECT
                p.*,
                ISNULL(task_stat.task_count, 0) AS task_count
            FROM [{TABLE_NAMES['INSPECTION_PLAN']}] AS p
            LEFT JOIN (
                SELECT
                    [{INSPECTION_TASK_COLUMNS['plan_no']}] AS plan_no,
                    COUNT(1) AS task_count
                FROM [{TABLE_NAMES['INSPECTION_TASK']}]
                GROUP BY [{INSPECTION_TASK_COLUMNS['plan_no']}]
            ) AS task_stat
                ON p.[{INSPECTION_PLAN_COLUMNS['plan_no']}] = task_stat.plan_no
            WHERE {where_clause}
            ORDER BY p.[{INSPECTION_PLAN_COLUMNS['plan_year']}] DESC,
                     p.[{INSPECTION_PLAN_COLUMNS['plan_month']}] DESC,
                     p.[{INSPECTION_PLAN_COLUMNS['created_at']}] DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """,
            tuple(params + [offset, page_size]),
        )
        return {"data": rows, "total": total, "page_no": page_no, "page_size": page_size}

    def update_plan(self, plan_no: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        normalized_plan_no = str(plan_no or "").strip()
        if not normalized_plan_no:
            return {}

        assignments: List[str] = []
        params: List[Any] = []
        for key in (
            "plan_name",
            "plan_year",
            "plan_month",
            "inspection_type",
            "status",
            "creator_id",
            "creator_name",
            "publish_time",
            "remark",
            "updated_by",
        ):
            if key in plan_data:
                assignments.append(f"[{INSPECTION_PLAN_COLUMNS[key]}] = ?")
                params.append(plan_data.get(key))

        assignments.append(f"[{INSPECTION_PLAN_COLUMNS['updated_at']}] = SYSDATETIME()")
        params.append(normalized_plan_no)
        self._db.execute_query(
            f"""
            UPDATE [{TABLE_NAMES['INSPECTION_PLAN']}]
            SET {", ".join(assignments)}
            WHERE [{INSPECTION_PLAN_COLUMNS['plan_no']}] = ?
            """,
            tuple(params),
            fetch=False,
        )
        return self.get_plan(normalized_plan_no)

    def publish_plan(self, plan_no: str) -> Dict[str, Any]:
        plan = self.get_plan(plan_no)
        if not plan:
            return {"success": False, "error": "inspection plan not found"}
        if str(plan.get("status") or "") == "published":
            return {"success": False, "error": "inspection plan already published"}

        preview_rows = self.preview_tasks(plan_no)
        tasks_payload: List[Dict[str, Any]] = []
        for row in preview_rows:
            tasks_payload.append(
                {
                    "task_no": generate_inspection_no_atomic("DJT"),
                    "plan_no": plan["plan_no"],
                    "serial_no": row.get("serial_no"),
                    "tool_name": row.get("tool_name"),
                    "drawing_no": row.get("drawing_no"),
                    "spec_model": row.get("spec_model"),
                    "task_status": "pending",
                    "deadline": self._build_deadline(plan),
                    "next_inspection_date": row.get("next_inspection_date"),
                    "remark": row.get("remark"),
                    "created_by": plan.get("creator_name") or plan.get("updated_by") or "system",
                    "updated_by": plan.get("creator_name") or plan.get("updated_by") or "system",
                }
            )

        def _publish_tx(conn: Any) -> None:
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['INSPECTION_PLAN']}]
                SET [{INSPECTION_PLAN_COLUMNS['status']}] = 'published',
                    [{INSPECTION_PLAN_COLUMNS['publish_time']}] = SYSDATETIME(),
                    [{INSPECTION_PLAN_COLUMNS['updated_at']}] = SYSDATETIME()
                WHERE [{INSPECTION_PLAN_COLUMNS['plan_no']}] = ?
                """,
                (plan["plan_no"],),
                fetch=False,
                conn=conn,
            )
            if not tasks_payload:
                return

            insert_sql = f"""
            INSERT INTO [{TABLE_NAMES['INSPECTION_TASK']}] (
                [{INSPECTION_TASK_COLUMNS['task_no']}],
                [{INSPECTION_TASK_COLUMNS['plan_no']}],
                [{INSPECTION_TASK_COLUMNS['serial_no']}],
                [{INSPECTION_TASK_COLUMNS['tool_name']}],
                [{INSPECTION_TASK_COLUMNS['drawing_no']}],
                [{INSPECTION_TASK_COLUMNS['spec_model']}],
                [{INSPECTION_TASK_COLUMNS['task_status']}],
                [{INSPECTION_TASK_COLUMNS['deadline']}],
                [{INSPECTION_TASK_COLUMNS['next_inspection_date']}],
                [{INSPECTION_TASK_COLUMNS['remark']}],
                [{INSPECTION_TASK_COLUMNS['created_at']}],
                [{INSPECTION_TASK_COLUMNS['updated_at']}],
                [{INSPECTION_TASK_COLUMNS['created_by']}],
                [{INSPECTION_TASK_COLUMNS['updated_by']}]
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), SYSDATETIME(), ?, ?)
            """
            for task in tasks_payload:
                self._db.execute_query(
                    insert_sql,
                    (
                        task["task_no"],
                        task["plan_no"],
                        task["serial_no"],
                        task["tool_name"],
                        task["drawing_no"],
                        task["spec_model"],
                        task["task_status"],
                        task["deadline"],
                        task["next_inspection_date"],
                        task["remark"],
                        task["created_by"],
                        task["updated_by"],
                    ),
                    fetch=False,
                    conn=conn,
                )

        self._db.execute_with_transaction(_publish_tx)
        return {"success": True, "plan_no": plan["plan_no"], "generated_task_count": len(tasks_payload)}

    def preview_tasks(self, plan_no: str) -> List[Dict[str, Any]]:
        plan = self.get_plan(plan_no)
        if not plan:
            return []

        month_end = self._build_deadline(plan)
        return self._db.execute_query(
            f"""
            SELECT
                [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}] AS serial_no,
                [{TOOL_INSPECTION_STATUS_COLUMNS['tool_name']}] AS tool_name,
                [{TOOL_INSPECTION_STATUS_COLUMNS['drawing_no']}] AS drawing_no,
                CAST(NULL AS VARCHAR(100)) AS spec_model,
                [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] AS next_inspection_date,
                [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}] AS inspection_status,
                [{TOOL_INSPECTION_STATUS_COLUMNS['remark']}] AS remark
            FROM [{TABLE_NAMES['TOOL_INSPECTION_STATUS']}]
            WHERE [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] IS NOT NULL
              AND (
                    [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}] IN ('pending', 'overdue')
                    OR [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] <= ?
              )
            ORDER BY [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}],
                     [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}]
            """,
            (month_end.date(),),
        )

    @staticmethod
    def _build_deadline(plan: Dict[str, Any]) -> datetime:
        year = int(plan.get("plan_year") or datetime.now().year)
        month = int(plan.get("plan_month") or datetime.now().month)
        last_day = calendar.monthrange(year, month)[1]
        return datetime(year, month, last_day, 23, 59, 59)
