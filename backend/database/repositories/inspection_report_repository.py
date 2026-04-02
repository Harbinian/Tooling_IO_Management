# -*- coding: utf-8 -*-
"""Repository for inspection report persistence."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.repositories.inspection_repository_common import (
    decode_base64_payload,
    generate_inspection_no_atomic,
)
from backend.database.schema.column_names import (
    INSPECTION_REPORT_COLUMNS,
    INSPECTION_TASK_COLUMNS,
    TABLE_NAMES,
)


class InspectionReportRepository:
    """Persist inspection reports and report-task linkage."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        report_no = str(report_data.get("report_no") or "").strip() or generate_inspection_no_atomic("RPT")
        normalized = self._normalize_report_data(report_data)

        def _tx(conn: Any) -> None:
            self._db.execute_query(
                f"""
                INSERT INTO [{TABLE_NAMES['INSPECTION_REPORT']}] (
                    [{INSPECTION_REPORT_COLUMNS['report_no']}],
                    [{INSPECTION_REPORT_COLUMNS['task_no']}],
                    [{INSPECTION_REPORT_COLUMNS['inspector_id']}],
                    [{INSPECTION_REPORT_COLUMNS['inspector_name']}],
                    [{INSPECTION_REPORT_COLUMNS['inspection_date']}],
                    [{INSPECTION_REPORT_COLUMNS['inspection_result']}],
                    [{INSPECTION_REPORT_COLUMNS['measurement_data']}],
                    [{INSPECTION_REPORT_COLUMNS['attachment_data']}],
                    [{INSPECTION_REPORT_COLUMNS['attachment_name']}],
                    [{INSPECTION_REPORT_COLUMNS['remark']}],
                    [{INSPECTION_REPORT_COLUMNS['created_at']}],
                    [{INSPECTION_REPORT_COLUMNS['updated_at']}],
                    [{INSPECTION_REPORT_COLUMNS['created_by']}],
                    [{INSPECTION_REPORT_COLUMNS['updated_by']}]
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), SYSDATETIME(), ?, ?)
                """,
                (
                    report_no,
                    normalized["task_no"],
                    normalized["inspector_id"],
                    normalized["inspector_name"],
                    normalized["inspection_date"],
                    normalized["inspection_result"],
                    normalized["measurement_data"],
                    normalized["attachment_data"],
                    normalized["attachment_name"],
                    normalized["remark"],
                    normalized["created_by"],
                    normalized["updated_by"],
                ),
                fetch=False,
                conn=conn,
            )
            self._db.execute_query(
                f"""
                UPDATE [{TABLE_NAMES['INSPECTION_TASK']}]
                SET [{INSPECTION_TASK_COLUMNS['report_no']}] = ?,
                    [{INSPECTION_TASK_COLUMNS['inspection_result']}] = ?,
                    [{INSPECTION_TASK_COLUMNS['task_status']}] = 'report_submitted',
                    [{INSPECTION_TASK_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{INSPECTION_TASK_COLUMNS['updated_by']}] = ?
                WHERE [{INSPECTION_TASK_COLUMNS['task_no']}] = ?
                """,
                (
                    report_no,
                    normalized["inspection_result"],
                    normalized["updated_by"],
                    normalized["task_no"],
                ),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return self.get_report(report_no)

    def get_report(self, report_no: str) -> Dict[str, Any]:
        rows = self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['INSPECTION_REPORT']}]
            WHERE [{INSPECTION_REPORT_COLUMNS['report_no']}] = ?
            """,
            (str(report_no or "").strip(),),
        )
        return rows[0] if rows else {}

    def get_reports_by_task(self, task_no: str) -> List[Dict[str, Any]]:
        return self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['INSPECTION_REPORT']}]
            WHERE [{INSPECTION_REPORT_COLUMNS['task_no']}] = ?
            ORDER BY [{INSPECTION_REPORT_COLUMNS['created_at']}] DESC
            """,
            (str(task_no or "").strip(),),
        )

    def update_report(self, report_no: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        normalized_report_no = str(report_no or "").strip()
        if not normalized_report_no:
            return {}

        normalized = self._normalize_report_data(report_data, allow_partial=True)
        assignments: List[str] = []
        params: List[Any] = []
        for key in (
            "inspector_id",
            "inspector_name",
            "inspection_date",
            "inspection_result",
            "measurement_data",
            "attachment_data",
            "attachment_name",
            "remark",
            "updated_by",
        ):
            if key in normalized:
                assignments.append(f"[{INSPECTION_REPORT_COLUMNS[key]}] = ?")
                params.append(normalized[key])

        assignments.append(f"[{INSPECTION_REPORT_COLUMNS['updated_at']}] = SYSDATETIME()")
        params.append(normalized_report_no)
        self._db.execute_query(
            f"""
            UPDATE [{TABLE_NAMES['INSPECTION_REPORT']}]
            SET {", ".join(assignments)}
            WHERE [{INSPECTION_REPORT_COLUMNS['report_no']}] = ?
            """,
            tuple(params),
            fetch=False,
        )
        return self.get_report(normalized_report_no)

    @staticmethod
    def _normalize_report_data(report_data: Dict[str, Any], allow_partial: bool = False) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        updated_by = str(report_data.get("updated_by") or report_data.get("created_by") or "system").strip()
        created_by = str(report_data.get("created_by") or updated_by).strip()
        if not allow_partial or "task_no" in report_data:
            normalized["task_no"] = str(report_data.get("task_no") or "").strip()
        if not allow_partial or "inspector_id" in report_data:
            normalized["inspector_id"] = str(report_data.get("inspector_id") or "").strip()
        if not allow_partial or "inspector_name" in report_data:
            normalized["inspector_name"] = str(report_data.get("inspector_name") or "").strip()
        if not allow_partial or "inspection_date" in report_data:
            normalized["inspection_date"] = report_data.get("inspection_date")
        if not allow_partial or "inspection_result" in report_data:
            normalized["inspection_result"] = str(report_data.get("inspection_result") or "pass").strip()
        if not allow_partial or "measurement_data" in report_data:
            measurement_data = report_data.get("measurement_data")
            if measurement_data is None or isinstance(measurement_data, str):
                normalized["measurement_data"] = measurement_data
            else:
                normalized["measurement_data"] = json.dumps(measurement_data, ensure_ascii=False)
        if not allow_partial or "attachment_data" in report_data:
            attachment_data = report_data.get("attachment_data")
            if attachment_data not in (None, ""):
                decode_base64_payload(str(attachment_data))
                normalized["attachment_data"] = attachment_data
            else:
                normalized["attachment_data"] = None if allow_partial else attachment_data
        if not allow_partial or "attachment_name" in report_data:
            attachment_name = str(report_data.get("attachment_name") or "").strip()
            normalized["attachment_name"] = attachment_name or None
        if not allow_partial or "remark" in report_data:
            normalized["remark"] = report_data.get("remark")
        normalized["created_by"] = created_by
        normalized["updated_by"] = updated_by
        return normalized
