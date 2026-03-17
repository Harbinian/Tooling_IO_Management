# -*- coding: utf-8 -*-
"""Feedback persistence services."""

from __future__ import annotations

from typing import Dict, List, Tuple

from database import DatabaseManager, ensure_feedback_reply_table, ensure_feedback_table

ALLOWED_CATEGORIES = {"bug", "feature", "ux", "other"}
ALLOWED_STATUSES = {"pending", "reviewed", "resolved"}
ALLOWED_STATUS_TRANSITIONS = {
    ("pending", "reviewed"),
    ("pending", "resolved"),
    ("reviewed", "resolved"),
    ("resolved", "reviewed"),
}


def _normalize_category(value: str) -> str:
    category = (value or "").strip().lower()
    if category not in ALLOWED_CATEGORIES:
        raise ValueError("category must be one of: bug, feature, ux, other")
    return category


def _normalize_subject(value: str) -> str:
    subject = (value or "").strip()
    if len(subject) < 2:
        raise ValueError("subject must be at least 2 characters")
    if len(subject) > 100:
        raise ValueError("subject cannot exceed 100 characters")
    return subject


def _normalize_content(value: str) -> str:
    content = (value or "").strip()
    if len(content) < 10:
        raise ValueError("content must be at least 10 characters")
    if len(content) > 2000:
        raise ValueError("content cannot exceed 2000 characters")
    return content


def _normalize_status(value: str, *, default: str = "pending") -> str:
    status = (value or default).strip().lower()
    if status not in ALLOWED_STATUSES:
        raise ValueError("status must be one of: pending, reviewed, resolved")
    return status


def _normalize_limit(value, *, default: int, max_value: int) -> int:
    try:
        normalized = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    return max(1, min(normalized, max_value))


def _normalize_offset(value, *, default: int = 0) -> int:
    try:
        normalized = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("offset must be an integer") from exc
    if normalized < 0:
        raise ValueError("offset must be greater than or equal to 0")
    return normalized


def _normalize_reply_content(value: str) -> str:
    content = (value or "").strip()
    if len(content) < 1:
        raise ValueError("reply_content is required")
    if len(content) > 1000:
        raise ValueError("reply_content cannot exceed 1000 characters")
    return content


def _serialize_feedback_row(row: Dict) -> Dict:
    return {
        "id": row.get("id"),
        "category": row.get("category", ""),
        "subject": row.get("subject", ""),
        "content": row.get("content", ""),
        "login_name": row.get("login_name", ""),
        "user_name": row.get("user_name", ""),
        "status": row.get("status", "pending"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _serialize_feedback_reply_row(row: Dict) -> Dict:
    return {
        "id": row.get("id"),
        "feedback_id": row.get("feedback_id"),
        "reply_content": row.get("reply_content", ""),
        "replier_login_name": row.get("replier_login_name", ""),
        "replier_user_name": row.get("replier_user_name", ""),
        "created_at": row.get("created_at"),
    }


def list_feedback(*, login_name: str = "", status: str = "", limit: int = 200) -> List[Dict]:
    """List feedback records filtered by optional login_name and status."""
    ensure_feedback_table()
    db = DatabaseManager()

    safe_limit = _normalize_limit(limit, default=200, max_value=500)
    sql = f"""
    SELECT TOP ({safe_limit})
        id,
        category,
        subject,
        content,
        login_name,
        user_name,
        status,
        created_at,
        updated_at
    FROM tool_io_feedback
    WHERE 1 = 1
    """
    params: List[str] = []

    normalized_login_name = (login_name or "").strip()
    if normalized_login_name:
        sql += " AND login_name = ?"
        params.append(normalized_login_name)

    normalized_status = (status or "").strip().lower()
    if normalized_status:
        normalized_status = _normalize_status(normalized_status)
        sql += " AND status = ?"
        params.append(normalized_status)

    sql += " ORDER BY created_at DESC, id DESC"
    rows = db.execute_query(sql, tuple(params))
    return [_serialize_feedback_row(row) for row in rows]


def list_all_feedback(
    *,
    status: str = "",
    category: str = "",
    keyword: str = "",
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Dict], int]:
    """List all feedback records for admins with filters and pagination."""
    ensure_feedback_table()
    db = DatabaseManager()

    safe_limit = _normalize_limit(limit, default=50, max_value=500)
    safe_offset = _normalize_offset(offset, default=0)

    where_clauses: List[str] = ["1 = 1"]
    params: List[str] = []

    normalized_status = (status or "").strip().lower()
    if normalized_status:
        where_clauses.append("status = ?")
        params.append(_normalize_status(normalized_status))

    normalized_category = (category or "").strip().lower()
    if normalized_category:
        where_clauses.append("category = ?")
        params.append(_normalize_category(normalized_category))

    normalized_keyword = (keyword or "").strip()
    if normalized_keyword:
        where_clauses.append("(subject LIKE ? OR content LIKE ? OR login_name LIKE ? OR user_name LIKE ?)")
        like_pattern = f"%{normalized_keyword}%"
        params.extend([like_pattern, like_pattern, like_pattern, like_pattern])

    where_sql = " AND ".join(where_clauses)
    total_sql = f"SELECT COUNT(1) AS total FROM tool_io_feedback WHERE {where_sql}"
    total_rows = db.execute_query(total_sql, tuple(params))
    total = int((total_rows[0] or {}).get("total", 0)) if total_rows else 0

    list_sql = f"""
    SELECT
        id,
        category,
        subject,
        content,
        login_name,
        user_name,
        status,
        created_at,
        updated_at
    FROM tool_io_feedback
    WHERE {where_sql}
    ORDER BY created_at DESC, id DESC
    OFFSET {safe_offset} ROWS FETCH NEXT {safe_limit} ROWS ONLY
    """
    rows = db.execute_query(list_sql, tuple(params))
    return ([_serialize_feedback_row(row) for row in rows], total)


def create_feedback(payload: Dict, *, login_name: str, user_name: str) -> Dict:
    """Create one feedback record and return the saved row."""
    ensure_feedback_table()
    db = DatabaseManager()

    normalized_login_name = (login_name or "").strip()
    normalized_user_name = (user_name or "").strip()
    if not normalized_login_name:
        raise ValueError("login_name is required")
    if not normalized_user_name:
        raise ValueError("user_name is required")

    category = _normalize_category(payload.get("category"))
    subject = _normalize_subject(payload.get("subject"))
    content = _normalize_content(payload.get("content"))
    status = _normalize_status(payload.get("status"), default="pending")

    inserted = db.execute_query(
        """
        INSERT INTO tool_io_feedback (
            category, subject, content, login_name, user_name, status, created_at, updated_at
        )
        OUTPUT
            inserted.id,
            inserted.category,
            inserted.subject,
            inserted.content,
            inserted.login_name,
            inserted.user_name,
            inserted.status,
            inserted.created_at,
            inserted.updated_at
        VALUES (?, ?, ?, ?, ?, ?, SYSDATETIME(), SYSDATETIME())
        """,
        (category, subject, content, normalized_login_name, normalized_user_name, status),
    )
    return _serialize_feedback_row(inserted[0]) if inserted else {}


def update_feedback_status(
    feedback_id: int,
    new_status: str,
    *,
    login_name: str,
    user_name: str,
) -> Dict:
    """Update feedback status with allowed transition validation."""
    ensure_feedback_table()
    db = DatabaseManager()

    normalized_login_name = (login_name or "").strip()
    normalized_user_name = (user_name or "").strip()
    if not normalized_login_name:
        raise ValueError("login_name is required")
    if not normalized_user_name:
        raise ValueError("user_name is required")

    target_status = _normalize_status(new_status)
    existing_rows = db.execute_query(
        """
        SELECT
            id,
            category,
            subject,
            content,
            login_name,
            user_name,
            status,
            created_at,
            updated_at
        FROM tool_io_feedback
        WHERE id = ?
        """,
        (feedback_id,),
    )
    if not existing_rows:
        return {}

    existing = existing_rows[0]
    current_status = _normalize_status(existing.get("status"), default="pending")

    if target_status == current_status:
        return _serialize_feedback_row(existing)
    if (current_status, target_status) not in ALLOWED_STATUS_TRANSITIONS:
        raise ValueError(f"status transition not allowed: {current_status} -> {target_status}")

    updated_rows = db.execute_query(
        """
        UPDATE tool_io_feedback
        SET
            status = ?,
            updated_at = SYSDATETIME()
        OUTPUT
            inserted.id,
            inserted.category,
            inserted.subject,
            inserted.content,
            inserted.login_name,
            inserted.user_name,
            inserted.status,
            inserted.created_at,
            inserted.updated_at
        WHERE id = ?
        """,
        (target_status, feedback_id),
    )
    return _serialize_feedback_row(updated_rows[0]) if updated_rows else {}


def add_feedback_reply(
    feedback_id: int,
    content: str,
    *,
    login_name: str,
    user_name: str,
) -> Dict:
    """Add one reply to feedback and auto-mark pending feedback as reviewed."""
    ensure_feedback_table()
    ensure_feedback_reply_table()
    db = DatabaseManager()

    normalized_login_name = (login_name or "").strip()
    normalized_user_name = (user_name or "").strip()
    if not normalized_login_name:
        raise ValueError("login_name is required")
    if not normalized_user_name:
        raise ValueError("user_name is required")

    reply_content = _normalize_reply_content(content)
    existing_rows = db.execute_query(
        "SELECT id, status FROM tool_io_feedback WHERE id = ?",
        (feedback_id,),
    )
    if not existing_rows:
        return {}

    inserted_rows = db.execute_query(
        """
        INSERT INTO tool_io_feedback_reply (
            feedback_id,
            reply_content,
            replier_login_name,
            replier_user_name,
            created_at
        )
        OUTPUT
            inserted.id,
            inserted.feedback_id,
            inserted.reply_content,
            inserted.replier_login_name,
            inserted.replier_user_name,
            inserted.created_at
        VALUES (?, ?, ?, ?, SYSDATETIME())
        """,
        (feedback_id, reply_content, normalized_login_name, normalized_user_name),
    )
    if not inserted_rows:
        return {}

    current_status = _normalize_status(existing_rows[0].get("status"), default="pending")
    status_after = current_status
    if current_status == "pending":
        db.execute_query(
            """
            UPDATE tool_io_feedback
            SET
                status = 'reviewed',
                updated_at = SYSDATETIME()
            WHERE id = ?
            """,
            (feedback_id,),
        )
        status_after = "reviewed"

    reply_payload = _serialize_feedback_reply_row(inserted_rows[0])
    reply_payload["feedback_status_after_reply"] = status_after
    return reply_payload


def get_feedback_replies(feedback_id: int) -> List[Dict]:
    """Get replies for one feedback record."""
    ensure_feedback_reply_table()
    db = DatabaseManager()
    rows = db.execute_query(
        """
        SELECT
            id,
            feedback_id,
            reply_content,
            replier_login_name,
            replier_user_name,
            created_at
        FROM tool_io_feedback_reply
        WHERE feedback_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (feedback_id,),
    )
    return [_serialize_feedback_reply_row(row) for row in rows]


def delete_feedback(feedback_id: int, *, login_name: str, is_admin: bool = False) -> bool:
    """Delete one feedback row by id. Non-admin users can only delete their own rows."""
    ensure_feedback_table()
    db = DatabaseManager()

    if is_admin:
        rows = db.execute_query(
            """
            DELETE FROM tool_io_feedback
            OUTPUT deleted.id
            WHERE id = ?
            """,
            (feedback_id,),
        )
    else:
        rows = db.execute_query(
            """
            DELETE FROM tool_io_feedback
            OUTPUT deleted.id
            WHERE id = ? AND login_name = ?
            """,
            (feedback_id, (login_name or "").strip()),
        )
    return bool(rows)


def resolve_feedback_owner_filter(*, requested_login_name: str, current_user: Dict) -> str:
    """Resolve list filter so normal users can only access their own feedback."""
    user_login_name = (current_user.get("login_name") or "").strip()
    requested = (requested_login_name or "").strip()
    permissions = set(current_user.get("permissions") or [])
    can_view_all = "admin:user_manage" in permissions
    return requested if can_view_all and requested else user_login_name
