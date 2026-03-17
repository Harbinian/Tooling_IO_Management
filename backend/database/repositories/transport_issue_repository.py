# -*- coding: utf-8 -*-
"""Repository for transport issue reporting and handling."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import TRANSPORT_ISSUE_COLUMNS

logger = logging.getLogger(__name__)

TRANSPORT_ISSUE_TABLE = "tool_io_transport_issue"


class TransportIssueRepository:
    """Database operations for transport issues."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    def create_issue(
        self,
        *,
        order_no: str,
        issue_type: str,
        description: str,
        image_urls: List[str],
        reporter_id: str,
        reporter_name: str,
    ) -> Dict:
        """Create one transport issue with explicit transaction."""
        conn = None
        cursor = None
        try:
            conn = self._db.connect()
            cursor = conn.cursor()
            image_urls_json = json.dumps(image_urls or [], ensure_ascii=False)

            sql = f"""
            INSERT INTO [{TRANSPORT_ISSUE_TABLE}] (
                [{TRANSPORT_ISSUE_COLUMNS['order_no']}],
                [{TRANSPORT_ISSUE_COLUMNS['issue_type']}],
                [{TRANSPORT_ISSUE_COLUMNS['description']}],
                [{TRANSPORT_ISSUE_COLUMNS['image_urls']}],
                [{TRANSPORT_ISSUE_COLUMNS['reporter_id']}],
                [{TRANSPORT_ISSUE_COLUMNS['reporter_name']}],
                [{TRANSPORT_ISSUE_COLUMNS['report_time']}],
                [{TRANSPORT_ISSUE_COLUMNS['status']}],
                [{TRANSPORT_ISSUE_COLUMNS['created_at']}]
            )
            OUTPUT INSERTED.[{TRANSPORT_ISSUE_COLUMNS['id']}] AS [issue_id]
            VALUES (?, ?, ?, ?, ?, ?, GETDATE(), 'pending', GETDATE())
            """
            cursor.execute(
                sql,
                (
                    order_no,
                    issue_type,
                    description or None,
                    image_urls_json or None,
                    reporter_id or None,
                    reporter_name or None,
                ),
            )
            inserted = cursor.fetchone()
            conn.commit()
            issue_id = int(inserted[0]) if inserted else 0
            return {"success": True, "issue_id": issue_id}
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            logger.error("failed to create transport issue for %s: %s", order_no, exc)
            return {"success": False, "error": str(exc)}
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._db.close(conn)

    def get_issues_by_order(self, order_no: str) -> List[Dict]:
        """Load all transport issues for one order."""
        sql = f"""
        SELECT
            [{TRANSPORT_ISSUE_COLUMNS['id']}] AS [id],
            [{TRANSPORT_ISSUE_COLUMNS['issue_type']}] AS [issue_type],
            [{TRANSPORT_ISSUE_COLUMNS['description']}] AS [description],
            [{TRANSPORT_ISSUE_COLUMNS['image_urls']}] AS [image_urls],
            [{TRANSPORT_ISSUE_COLUMNS['reporter_name']}] AS [reporter_name],
            [{TRANSPORT_ISSUE_COLUMNS['report_time']}] AS [report_time],
            [{TRANSPORT_ISSUE_COLUMNS['status']}] AS [status],
            [{TRANSPORT_ISSUE_COLUMNS['handler_name']}] AS [handler_name],
            [{TRANSPORT_ISSUE_COLUMNS['handle_time']}] AS [handle_time],
            [{TRANSPORT_ISSUE_COLUMNS['handle_reply']}] AS [handle_reply]
        FROM [{TRANSPORT_ISSUE_TABLE}]
        WHERE [{TRANSPORT_ISSUE_COLUMNS['order_no']}] = ?
        ORDER BY [{TRANSPORT_ISSUE_COLUMNS['report_time']}] DESC, [{TRANSPORT_ISSUE_COLUMNS['id']}] DESC
        """
        rows = self._db.execute_query(sql, (order_no,))
        issues: List[Dict] = []
        for row in rows:
            issues.append(
                {
                    "id": row.get("id"),
                    "issue_type": row.get("issue_type"),
                    "description": row.get("description") or "",
                    "image_urls": self._parse_image_urls(row.get("image_urls")),
                    "reporter_name": row.get("reporter_name"),
                    "report_time": self._to_iso_datetime(row.get("report_time")),
                    "status": row.get("status"),
                    "resolver_name": row.get("handler_name"),
                    "resolve_time": self._to_iso_datetime(row.get("handle_time")),
                    "resolution": row.get("handle_reply"),
                }
            )
        return issues

    def resolve_issue(
        self,
        *,
        order_no: str,
        issue_id: int,
        handle_reply: str,
        handler_id: str,
        handler_name: str,
    ) -> Dict:
        """Resolve one pending transport issue with explicit transaction."""
        conn = None
        cursor = None
        try:
            conn = self._db.connect()
            cursor = conn.cursor()
            query_sql = f"""
            SELECT [{TRANSPORT_ISSUE_COLUMNS['status']}] AS [status]
            FROM [{TRANSPORT_ISSUE_TABLE}]
            WHERE [{TRANSPORT_ISSUE_COLUMNS['id']}] = ?
              AND [{TRANSPORT_ISSUE_COLUMNS['order_no']}] = ?
            """
            cursor.execute(query_sql, (issue_id, order_no))
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                return {"success": False, "error": "issue not found"}
            current_status = (row[0] or "").strip().lower()
            if current_status == "resolved":
                conn.rollback()
                return {"success": False, "error": "issue already resolved"}

            update_sql = f"""
            UPDATE [{TRANSPORT_ISSUE_TABLE}]
            SET
                [{TRANSPORT_ISSUE_COLUMNS['status']}] = 'resolved',
                [{TRANSPORT_ISSUE_COLUMNS['handler_id']}] = ?,
                [{TRANSPORT_ISSUE_COLUMNS['handler_name']}] = ?,
                [{TRANSPORT_ISSUE_COLUMNS['handle_time']}] = GETDATE(),
                [{TRANSPORT_ISSUE_COLUMNS['handle_reply']}] = ?
            WHERE [{TRANSPORT_ISSUE_COLUMNS['id']}] = ?
              AND [{TRANSPORT_ISSUE_COLUMNS['order_no']}] = ?
            """
            cursor.execute(
                update_sql,
                (handler_id or None, handler_name or None, handle_reply or None, issue_id, order_no),
            )
            if cursor.rowcount <= 0:
                conn.rollback()
                return {"success": False, "error": "issue not found"}
            conn.commit()
            return {"success": True}
        except Exception as exc:
            if conn is not None:
                conn.rollback()
            logger.error("failed to resolve transport issue %s for %s: %s", issue_id, order_no, exc)
            return {"success": False, "error": str(exc)}
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                self._db.close(conn)

    @staticmethod
    def _parse_image_urls(raw_value) -> List[str]:
        if raw_value is None:
            return []
        if isinstance(raw_value, list):
            return [str(item).strip() for item in raw_value if str(item).strip()]
        if isinstance(raw_value, str):
            text = raw_value.strip()
            if not text:
                return []
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except Exception:
                pass
            return [text]
        return [str(raw_value).strip()]

    @staticmethod
    def _to_iso_datetime(value) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat(timespec="seconds")
        return str(value)
