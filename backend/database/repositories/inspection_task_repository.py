# -*- coding: utf-8 -*-
"""Repository for inspection task persistence."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.repositories.inspection_repository_common import generate_inspection_no_atomic
from backend.database.schema.column_names import INSPECTION_TASK_COLUMNS, TABLE_NAMES


class InspectionTaskRepository:
    """Persist inspection tasks and task state transitions."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def create_task(self, task_data: Dict[str, Any], conn: Any = None) -> Dict[str, Any]:
        task_no = str(task_data.get("task_no") or "").strip() or generate_inspection_no_atomic("DJT")
        normalized = self._normalize_task_data(task_data)
        self._db.execute_query(
            f"""
            INSERT INTO [{TABLE_NAMES['INSPECTION_TASK']}] (
                [{INSPECTION_TASK_COLUMNS['task_no']}],
                [{INSPECTION_TASK_COLUMNS['plan_no']}],
                [{INSPECTION_TASK_COLUMNS['serial_no']}],
                [{INSPECTION_TASK_COLUMNS['tool_name']}],
                [{INSPECTION_TASK_COLUMNS['drawing_no']}],
                [{INSPECTION_TASK_COLUMNS['spec_model']}],
                [{INSPECTION_TASK_COLUMNS['task_status']}],
                [{INSPECTION_TASK_COLUMNS['assigned_to_id']}],
                [{INSPECTION_TASK_COLUMNS['assigned_to_name']}],
                [{INSPECTION_TASK_COLUMNS['receive_time']}],
                [{INSPECTION_TASK_COLUMNS['outbound_order_no']}],
                [{INSPECTION_TASK_COLUMNS['inbound_order_no']}],
                [{INSPECTION_TASK_COLUMNS['inspection_result']}],
                [{INSPECTION_TASK_COLUMNS['reject_reason']}],
                [{INSPECTION_TASK_COLUMNS['report_no']}],
                [{INSPECTION_TASK_COLUMNS['next_inspection_date']}],
                [{INSPECTION_TASK_COLUMNS['deadline']}],
                [{INSPECTION_TASK_COLUMNS['actual_complete_time']}],
                [{INSPECTION_TASK_COLUMNS['remark']}],
                [{INSPECTION_TASK_COLUMNS['created_at']}],
                [{INSPECTION_TASK_COLUMNS['updated_at']}],
                [{INSPECTION_TASK_COLUMNS['created_by']}],
                [{INSPECTION_TASK_COLUMNS['updated_by']}]
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), SYSDATETIME(), ?, ?)
            """,
            (
                task_no,
                normalized["plan_no"],
                normalized["serial_no"],
                normalized["tool_name"],
                normalized["drawing_no"],
                normalized["spec_model"],
                normalized["task_status"],
                normalized["assigned_to_id"],
                normalized["assigned_to_name"],
                normalized["receive_time"],
                normalized["outbound_order_no"],
                normalized["inbound_order_no"],
                normalized["inspection_result"],
                normalized["reject_reason"],
                normalized["report_no"],
                normalized["next_inspection_date"],
                normalized["deadline"],
                normalized["actual_complete_time"],
                normalized["remark"],
                normalized["created_by"],
                normalized["updated_by"],
            ),
            fetch=False,
            conn=conn,
        )
        if conn is not None:
            result = {"task_no": task_no}
            result.update(normalized)
            return result
        return self.get_task(task_no)

    def create_tasks_bulk(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        created_task_nos: List[str] = []

        def _bulk_tx(conn: Any) -> None:
            for task in tasks:
                result = self.create_task(task, conn=conn)
                if result.get("task_no"):
                    created_task_nos.append(str(result["task_no"]))

        self._db.execute_with_transaction(_bulk_tx)
        return {"success": True, "created_count": len(created_task_nos), "task_nos": created_task_nos}

    def get_task(self, task_no: str) -> Dict[str, Any]:
        rows = self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['INSPECTION_TASK']}]
            WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
            """,
            (str(task_no or "").strip(),),
        )
        return rows[0] if rows else {}

    def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        filters = filters or {}
        page_no = max(int(filters.get("page_no") or 1), 1)
        page_size = max(int(filters.get("page_size") or 20), 1)
        offset = (page_no - 1) * page_size

        conditions = ["1=1"]
        params: List[Any] = []
        for key in ("task_status", "plan_no", "assigned_to_id", "inspection_result", "report_no"):
            value = filters.get(key)
            if value not in (None, ""):
                conditions.append(f"t.[{INSPECTION_TASK_COLUMNS[key]}] = ?")
                params.append(value)

        keyword = str(filters.get("keyword") or "").strip()
        if keyword:
            conditions.append(
                f"""(
                    t.[{INSPECTION_TASK_COLUMNS['task_no']}] LIKE ?
                    OR t.[{INSPECTION_TASK_COLUMNS['serial_no']}] LIKE ?
                    OR t.[{INSPECTION_TASK_COLUMNS['tool_name']}] LIKE ?
                    OR t.[{INSPECTION_TASK_COLUMNS['drawing_no']}] LIKE ?
                )"""
            )
            params.extend([f"%{keyword}%"] * 4)

        where_clause = " AND ".join(conditions)
        total_rows = self._db.execute_query(
            f"""
            SELECT COUNT(1) AS total
            FROM [{TABLE_NAMES['INSPECTION_TASK']}] AS t
            WHERE {where_clause}
            """,
            tuple(params),
        )
        total = int((total_rows[0] if total_rows else {}).get("total", 0))

        rows = self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['INSPECTION_TASK']}] AS t
            WHERE {where_clause}
            ORDER BY t.[{INSPECTION_TASK_COLUMNS['created_at']}] DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """,
            tuple(params + [offset, page_size]),
        )
        return {"data": rows, "total": total, "page_no": page_no, "page_size": page_size}

    def update_task_status(self, task_no: str, new_status: str, operator_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        operator_info = operator_info or {}
        normalized_status = str(new_status or "").strip()
        assignments = [
            f"[{INSPECTION_TASK_COLUMNS['task_status']}] = ?",
            f"[{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME()",
            f"[{INSPECTION_TASK_COLUMNS['updated_by']}] = ?",
        ]
        params: List[Any] = [
            normalized_status,
            str(operator_info.get("operator_name") or operator_info.get("updated_by") or "system").strip(),
        ]
        if normalized_status == "received":
            assignments.append(f"[{INSPECTION_TASK_COLUMNS['receive_time']}] = SYSDATETIME()")
        if normalized_status in {"closed", "inbound_completed"}:
            assignments.append(f"[{INSPECTION_TASK_COLUMNS['actual_complete_time']}] = SYSDATETIME()")
        params.append(str(task_no or "").strip())
        self._db.execute_query(
            f"""
            UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
            SET {", ".join(assignments)}
            WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
            """,
            tuple(params),
            fetch=False,
        )
        return self.get_task(task_no)

    def link_outbound_order(self, task_no: str, order_no: str) -> Dict[str, Any]:
        return self._link_order(task_no, order_no, "outbound_order_no", "outbound_created")

    def link_inbound_order(self, task_no: str, order_no: str) -> Dict[str, Any]:
        return self._link_order(task_no, order_no, "inbound_order_no", "inbound_created")

    def get_overdue_tasks(self, hours: int = 72) -> List[Dict[str, Any]]:
        cutoff = datetime.now() - timedelta(hours=max(int(hours or 72), 1))
        return self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['INSPECTION_TASK']}]
            WHERE [{INSPECTION_TASK_COLUMNS['task_status']}] = 'received'
              AND [{INSPECTION_TASK_COLUMNS['receive_time']}] IS NOT NULL
              AND [{INSPECTION_TASK_COLUMNS['receive_time']}] < ?
            ORDER BY [{INSPECTION_TASK_COLUMNS['receive_time']}]
            """,
            (cutoff,),
        )

    def _link_order(self, task_no: str, order_no: str, order_field: str, next_status: str) -> Dict[str, Any]:
        def _tx(conn: Any) -> None:
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
                SET [{INSPECTION_TASK_COLUMNS[order_field]}] = ?,
                    [{INSPECTION_TASK_COLUMNS['task_status']}] = ?,
                    [{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{INSPECTION_TASK_COLUMNS['updated_by']}] = ?
                WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
                """,
                (str(order_no or "").strip(), next_status, "system", str(task_no or "").strip()),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return self.get_task(task_no)

    @staticmethod
    def _normalize_task_data(task_data: Dict[str, Any]) -> Dict[str, Any]:
        updated_by = str(task_data.get("updated_by") or task_data.get("created_by") or "system").strip()
        created_by = str(task_data.get("created_by") or updated_by).strip()
        return {
            "plan_no": str(task_data.get("plan_no") or "").strip(),
            "serial_no": str(task_data.get("serial_no") or "").strip(),
            "tool_name": task_data.get("tool_name"),
            "drawing_no": task_data.get("drawing_no"),
            "spec_model": task_data.get("spec_model"),
            "task_status": str(task_data.get("task_status") or "pending").strip(),
            "assigned_to_id": str(task_data.get("assigned_to_id") or "").strip() or None,
            "assigned_to_name": task_data.get("assigned_to_name"),
            "receive_time": task_data.get("receive_time"),
            "outbound_order_no": str(task_data.get("outbound_order_no") or "").strip() or None,
            "inbound_order_no": str(task_data.get("inbound_order_no") or "").strip() or None,
            "inspection_result": str(task_data.get("inspection_result") or "").strip() or None,
            "reject_reason": task_data.get("reject_reason"),
            "report_no": str(task_data.get("report_no") or "").strip() or None,
            "next_inspection_date": task_data.get("next_inspection_date"),
            "deadline": task_data.get("deadline"),
            "actual_complete_time": task_data.get("actual_complete_time"),
            "remark": task_data.get("remark"),
            "created_by": created_by,
            "updated_by": updated_by,
        }
