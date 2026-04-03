# -*- coding: utf-8 -*-
"""Service for inspection statistics aggregation."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import INSPECTION_TASK_COLUMNS, TABLE_NAMES


def get_summary(current_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get inspection task statistics summary.

    Returns counts for pending, in_progress, overdue, and completed tasks.
    """
    _ = current_user
    from backend.services.inspection_task_service import _ensure_inspection_schema
    _ensure_inspection_schema()
    db = DatabaseManager()

    today = date.today()

    # Pending count: tasks with status 'pending'
    pending_rows = db.execute_query(
        f"""
        SELECT COUNT(1) AS cnt
        FROM [{TABLE_NAMES['INSPECTION_TASK']}]
        WHERE [{INSPECTION_TASK_COLUMNS['task_status']}] = 'pending'
        """,
    )
    pending_count = int((pending_rows[0] if pending_rows else {}).get("cnt", 0))

    # In progress count: tasks with status 'received' or 'in_progress'
    in_progress_rows = db.execute_query(
        f"""
        SELECT COUNT(1) AS cnt
        FROM [{TABLE_NAMES['INSPECTION_TASK']}]
        WHERE [{INSPECTION_TASK_COLUMNS['task_status']}] IN ('received', 'in_progress')
        """,
    )
    in_progress_count = int((in_progress_rows[0] if in_progress_rows else {}).get("cnt", 0))

    # Completed count: tasks with status 'closed'
    completed_rows = db.execute_query(
        f"""
        SELECT COUNT(1) AS cnt
        FROM [{TABLE_NAMES['INSPECTION_TASK']}]
        WHERE [{INSPECTION_TASK_COLUMNS['task_status']}] = 'closed'
        """,
    )
    completed_count = int((completed_rows[0] if completed_rows else {}).get("cnt", 0))

    # Overdue count: tasks with deadline < today and not closed/completed
    overdue_rows = db.execute_query(
        f"""
        SELECT COUNT(1) AS cnt
        FROM [{TABLE_NAMES['INSPECTION_TASK']}]
        WHERE [{INSPECTION_TASK_COLUMNS['deadline']}] < ?
          AND [{INSPECTION_TASK_COLUMNS['task_status']}] NOT IN ('closed', 'completed')
        """,
        (today,),
    )
    overdue_count = int((overdue_rows[0] if overdue_rows else {}).get("cnt", 0))

    return {
        "success": True,
        "data": {
            "pending_count": pending_count,
            "in_progress_count": in_progress_count,
            "completed_count": completed_count,
            "overdue_count": overdue_count,
        },
    }
