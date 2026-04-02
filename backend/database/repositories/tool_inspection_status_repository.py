# -*- coding: utf-8 -*-
"""Repository for tool inspection status persistence."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import TABLE_NAMES, TOOL_INSPECTION_STATUS_COLUMNS


class ToolInspectionStatusRepository:
    """Persist and query tool inspection status snapshots."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def get_status(self, serial_no: str) -> Dict:
        rows = self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['TOOL_INSPECTION_STATUS']}]
            WHERE [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}] = ?
            """,
            (str(serial_no or "").strip(),),
        )
        return rows[0] if rows else {}

    def upsert_status(self, serial_no: str, status_data: Dict) -> Dict:
        normalized_serial_no = str(serial_no or "").strip()
        next_date = status_data.get("next_inspection_date")
        inspection_status = str(status_data.get("inspection_status") or self._derive_status(next_date)).strip()
        self._db.execute_query(
            f"""
            MERGE [{TABLE_NAMES['TOOL_INSPECTION_STATUS']}] AS target
            USING (
                SELECT
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['tool_name']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['drawing_no']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['last_inspection_date']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_cycle_days']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['remark']}],
                    ? AS [{TOOL_INSPECTION_STATUS_COLUMNS['updated_by']}]
            ) AS source
            ON target.[{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}]
            WHEN MATCHED THEN
                UPDATE SET
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['tool_name']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['tool_name']}],
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['drawing_no']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['drawing_no']}],
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['last_inspection_date']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['last_inspection_date']}],
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}],
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['inspection_cycle_days']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['inspection_cycle_days']}],
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}],
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['remark']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['remark']}],
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['updated_at']}] = SYSDATETIME(),
                    target.[{TOOL_INSPECTION_STATUS_COLUMNS['updated_by']}] = source.[{TOOL_INSPECTION_STATUS_COLUMNS['updated_by']}]
            WHEN NOT MATCHED THEN
                INSERT (
                    [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['tool_name']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['drawing_no']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['last_inspection_date']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_cycle_days']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['remark']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['updated_at']}],
                    [{TOOL_INSPECTION_STATUS_COLUMNS['updated_by']}]
                )
                VALUES (
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}],
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['tool_name']}],
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['drawing_no']}],
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['last_inspection_date']}],
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}],
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['inspection_cycle_days']}],
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}],
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['remark']}],
                    SYSDATETIME(),
                    source.[{TOOL_INSPECTION_STATUS_COLUMNS['updated_by']}]
                );
            """,
            (
                normalized_serial_no,
                status_data.get("tool_name"),
                status_data.get("drawing_no"),
                status_data.get("last_inspection_date"),
                next_date,
                status_data.get("inspection_cycle_days"),
                inspection_status,
                status_data.get("remark"),
                str(status_data.get("updated_by") or "system").strip(),
            ),
            fetch=False,
        )
        return self.get_status(normalized_serial_no)

    def update_next_inspection_date(self, serial_no: str, next_date, updated_by: str) -> Dict:
        normalized_status = self._derive_status(next_date)
        self._db.execute_query(
            f"""
            UPDATE [{TABLE_NAMES['TOOL_INSPECTION_STATUS']}]
            SET [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] = ?,
                [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}] = ?,
                [{TOOL_INSPECTION_STATUS_COLUMNS['updated_at']}] = SYSDATETIME(),
                [{TOOL_INSPECTION_STATUS_COLUMNS['updated_by']}] = ?
            WHERE [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}] = ?
            """,
            (next_date, normalized_status, str(updated_by or "system").strip(), str(serial_no or "").strip()),
            fetch=False,
        )
        return self.get_status(serial_no)

    def get_expiring_tools(self, days_before: int = 30) -> List[Dict]:
        today = date.today()
        cutoff = today + timedelta(days=max(int(days_before or 30), 1))
        return self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['TOOL_INSPECTION_STATUS']}]
            WHERE [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] IS NOT NULL
              AND [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] >= ?
              AND [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] <= ?
            ORDER BY [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}],
                     [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}]
            """,
            (today, cutoff),
        )

    def get_overdue_tools(self) -> List[Dict]:
        today = date.today()
        return self._db.execute_query(
            f"""
            SELECT *
            FROM [{TABLE_NAMES['TOOL_INSPECTION_STATUS']}]
            WHERE [{TOOL_INSPECTION_STATUS_COLUMNS['inspection_status']}] = 'overdue'
               OR (
                    [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] IS NOT NULL
                    AND [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}] < ?
               )
            ORDER BY [{TOOL_INSPECTION_STATUS_COLUMNS['next_inspection_date']}],
                     [{TOOL_INSPECTION_STATUS_COLUMNS['serial_no']}]
            """,
            (today,),
        )

    @staticmethod
    def _derive_status(next_date) -> str:
        if next_date in (None, ""):
            return "pending"
        if isinstance(next_date, datetime):
            next_date = next_date.date()
        if next_date < date.today():
            return "overdue"
        return "normal"
