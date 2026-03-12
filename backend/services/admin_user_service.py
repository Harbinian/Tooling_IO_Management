# -*- coding: utf-8 -*-
"""
Administrator account management services.
"""

from __future__ import annotations

from uuid import uuid4
from typing import Dict, List, Optional, Sequence

from backend.services.auth_service import hash_password
from backend.services.org_service import get_organization
from backend.services.rbac_service import ensure_rbac_tables
from database import DatabaseManager


def _normalize_status(value: str, *, default: str = "active") -> str:
    normalized = (value or default).strip().lower()
    if normalized not in {"active", "disabled"}:
        raise ValueError("status must be active or disabled")
    return normalized


def _normalize_login_name(value: str) -> str:
    login_name = (value or "").strip()
    if not login_name:
        raise ValueError("login_name is required")
    if len(login_name) > 100:
        raise ValueError("login_name is too long")
    return login_name


def _normalize_display_name(value: str) -> str:
    display_name = (value or "").strip()
    if not display_name:
        raise ValueError("display_name is required")
    if len(display_name) > 100:
        raise ValueError("display_name is too long")
    return display_name


def _normalize_employee_no(value: str, *, required: bool) -> str:
    employee_no = (value or "").strip()
    if required and not employee_no:
        raise ValueError("employee_no is required")
    if len(employee_no) > 100:
        raise ValueError("employee_no is too long")
    return employee_no


def _normalize_org_id(org_id: str) -> Optional[str]:
    normalized = (org_id or "").strip()
    if not normalized:
        return None
    if not get_organization(normalized):
        raise ValueError("organization does not exist")
    return normalized


def _load_user_by_identity(*, user_id: str = "", login_name: str = "", employee_no: str = "") -> Optional[Dict]:
    clauses = []
    params: List[str] = []
    if user_id:
        clauses.append("user_id = ?")
        params.append(user_id)
    if login_name:
        clauses.append("login_name = ?")
        params.append(login_name)
    if employee_no:
        clauses.append("employee_no = ?")
        params.append(employee_no)
    if not clauses:
        return None

    sql = f"""
    SELECT TOP 1
        user_id,
        login_name,
        display_name,
        employee_no,
        mobile,
        email,
        status,
        default_org_id,
        last_login_at,
        remark,
        created_at,
        updated_at
    FROM sys_user
    WHERE {" OR ".join(clauses)}
    ORDER BY created_at DESC
    """
    rows = DatabaseManager().execute_query(sql, tuple(params))
    return rows[0] if rows else None


def _load_role_records(role_ids: Sequence[str]) -> List[Dict]:
    normalized = [role_id for role_id in role_ids if role_id]
    if not normalized:
        raise ValueError("at least one role_id is required")

    placeholders = ",".join(["?"] * len(normalized))
    sql = f"""
    SELECT role_id, role_code, role_name, status
    FROM sys_role
    WHERE role_id IN ({placeholders})
    """
    rows = DatabaseManager().execute_query(sql, tuple(normalized))
    if len(rows) != len(set(normalized)):
        raise ValueError("one or more roles do not exist")
    inactive = [row["role_name"] for row in rows if (row.get("status") or "").lower() != "active"]
    if inactive:
        raise ValueError(f"inactive roles cannot be assigned: {', '.join(sorted(inactive))}")
    return rows


def _replace_user_roles(user_id: str, role_ids: Sequence[str], org_id: Optional[str], actor_user_id: str) -> None:
    role_records = _load_role_records(role_ids)
    db = DatabaseManager()
    db.execute_query(
        """
        UPDATE sys_user_role_rel
        SET status = 'disabled',
            updated_at = SYSDATETIME(),
            updated_by = ?
        WHERE user_id = ?
        """,
        (actor_user_id or None, user_id),
        fetch=False,
    )

    for index, role in enumerate(role_records):
        db.execute_query(
            """
            INSERT INTO sys_user_role_rel (
                user_id, role_id, org_id, is_primary, status, created_at, created_by
            )
            VALUES (?, ?, ?, ?, 'active', SYSDATETIME(), ?)
            """,
            (
                user_id,
                role["role_id"],
                org_id,
                1 if index == 0 else 0,
                actor_user_id or None,
            ),
            fetch=False,
        )


def list_roles() -> List[Dict]:
    ensure_rbac_tables()
    rows = DatabaseManager().execute_query(
        """
        SELECT role_id, role_code, role_name, role_type, status
        FROM sys_role
        WHERE status = 'active'
        ORDER BY
            CASE role_code
                WHEN 'team_leader' THEN 1
                WHEN 'keeper' THEN 2
                WHEN 'planner' THEN 3
                WHEN 'sys_admin' THEN 4
                WHEN 'auditor' THEN 5
                ELSE 99
            END,
            role_name ASC
        """
    )
    return rows


def list_users(keyword: str = "", status: str = "", org_id: str = "") -> List[Dict]:
    ensure_rbac_tables()
    sql = """
    SELECT
        usr.user_id,
        usr.login_name,
        usr.display_name,
        usr.employee_no,
        usr.status,
        usr.default_org_id,
        org.org_name AS default_org_name,
        usr.last_login_at,
        usr.created_at,
        usr.updated_at
    FROM sys_user usr
    LEFT JOIN sys_org org ON org.org_id = usr.default_org_id
    WHERE 1 = 1
    """
    params: List[str] = []

    normalized_keyword = (keyword or "").strip()
    if normalized_keyword:
        like_value = f"%{normalized_keyword}%"
        sql += """
        AND (
            usr.login_name LIKE ?
            OR usr.display_name LIKE ?
            OR ISNULL(usr.employee_no, '') LIKE ?
        )
        """
        params.extend([like_value, like_value, like_value])

    normalized_status = (status or "").strip().lower()
    if normalized_status:
        sql += " AND usr.status = ?"
        params.append(_normalize_status(normalized_status))

    normalized_org_id = (org_id or "").strip()
    if normalized_org_id:
        sql += " AND usr.default_org_id = ?"
        params.append(normalized_org_id)

    sql += " ORDER BY usr.created_at DESC, usr.user_id DESC"
    rows = DatabaseManager().execute_query(sql, tuple(params))

    user_ids = [row["user_id"] for row in rows if row.get("user_id")]
    role_map = _load_role_map(user_ids)
    return [_attach_user_roles(row, role_map) for row in rows]


def _load_role_map(user_ids: Sequence[str]) -> Dict[str, List[Dict]]:
    normalized = [user_id for user_id in user_ids if user_id]
    if not normalized:
        return {}
    placeholders = ",".join(["?"] * len(normalized))
    sql = f"""
    SELECT
        rel.user_id,
        rel.role_id,
        rel.org_id,
        rel.is_primary,
        role.role_code,
        role.role_name,
        role.role_type,
        org.org_name
    FROM sys_user_role_rel rel
    INNER JOIN sys_role role ON role.role_id = rel.role_id
    LEFT JOIN sys_org org ON org.org_id = rel.org_id
    WHERE rel.user_id IN ({placeholders})
      AND rel.status = 'active'
      AND role.status = 'active'
    ORDER BY rel.user_id ASC, rel.is_primary DESC, role.role_name ASC
    """
    rows = DatabaseManager().execute_query(sql, tuple(normalized))
    role_map: Dict[str, List[Dict]] = {}
    for row in rows:
        role_map.setdefault(row["user_id"], []).append(
            {
                "role_id": row.get("role_id", ""),
                "role_code": row.get("role_code", ""),
                "role_name": row.get("role_name", ""),
                "role_type": row.get("role_type", ""),
                "org_id": row.get("org_id", ""),
                "org_name": row.get("org_name", ""),
                "is_primary": bool(row.get("is_primary")),
            }
        )
    return role_map


def _attach_user_roles(row: Dict, role_map: Dict[str, List[Dict]]) -> Dict:
    return {
        "user_id": row.get("user_id", ""),
        "login_name": row.get("login_name", ""),
        "display_name": row.get("display_name", ""),
        "employee_no": row.get("employee_no", ""),
        "status": row.get("status", ""),
        "default_org_id": row.get("default_org_id", ""),
        "default_org_name": row.get("default_org_name", ""),
        "last_login_at": row.get("last_login_at"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "roles": role_map.get(row.get("user_id", ""), []),
    }


def get_user_detail(user_id: str) -> Optional[Dict]:
    ensure_rbac_tables()
    record = _load_user_by_identity(user_id=user_id)
    if not record:
        return None
    role_map = _load_role_map([user_id])
    return _attach_user_roles(record, role_map)


def create_user(payload: Dict, actor_user_id: str) -> Dict:
    ensure_rbac_tables()

    login_name = _normalize_login_name(payload.get("login_name"))
    display_name = _normalize_display_name(payload.get("display_name"))
    employee_no = _normalize_employee_no(payload.get("employee_no"), required=True)
    password = (payload.get("initial_password") or "").strip()
    if not password:
        raise ValueError("initial_password is required")

    status = _normalize_status(payload.get("status"))
    default_org_id = _normalize_org_id(payload.get("default_org_id"))
    role_ids = payload.get("role_ids") or []
    if not isinstance(role_ids, list):
        raise ValueError("role_ids must be an array")
    if not role_ids:
        raise ValueError("at least one role must be assigned")

    if _load_user_by_identity(login_name=login_name):
        raise ValueError("login_name already exists")
    if _load_user_by_identity(employee_no=employee_no):
        raise ValueError("employee_no already exists")

    user_id = f"U_{uuid4().hex[:16].upper()}"
    db = DatabaseManager()
    db.execute_query(
        """
        INSERT INTO sys_user (
            user_id, login_name, display_name, employee_no, password_hash,
            status, default_org_id, created_at, created_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), ?)
        """,
        (
            user_id,
            login_name,
            display_name,
            employee_no,
            hash_password(password),
            status,
            default_org_id,
            actor_user_id or None,
        ),
        fetch=False,
    )
    _replace_user_roles(user_id, role_ids, default_org_id, actor_user_id)
    return get_user_detail(user_id)


def update_user(user_id: str, payload: Dict, actor_user_id: str) -> Optional[Dict]:
    ensure_rbac_tables()
    existing = _load_user_by_identity(user_id=user_id)
    if not existing:
        return None

    login_name = _normalize_login_name(payload.get("login_name", existing.get("login_name")))
    display_name = _normalize_display_name(payload.get("display_name", existing.get("display_name")))
    employee_no = _normalize_employee_no(payload.get("employee_no", existing.get("employee_no")), required=True)
    status = _normalize_status(payload.get("status", existing.get("status")))
    default_org_id = _normalize_org_id(payload.get("default_org_id", existing.get("default_org_id")))

    duplicate_login = _load_user_by_identity(login_name=login_name)
    if duplicate_login and duplicate_login.get("user_id") != user_id:
        raise ValueError("login_name already exists")

    duplicate_employee = _load_user_by_identity(employee_no=employee_no)
    if duplicate_employee and duplicate_employee.get("user_id") != user_id:
        raise ValueError("employee_no already exists")

    DatabaseManager().execute_query(
        """
        UPDATE sys_user
        SET login_name = ?,
            display_name = ?,
            employee_no = ?,
            status = ?,
            default_org_id = ?,
            updated_at = SYSDATETIME(),
            updated_by = ?
        WHERE user_id = ?
        """,
        (
            login_name,
            display_name,
            employee_no,
            status,
            default_org_id,
            actor_user_id or None,
            user_id,
        ),
        fetch=False,
    )
    return get_user_detail(user_id)


def assign_user_roles(user_id: str, role_ids: Sequence[str], org_id: Optional[str], actor_user_id: str) -> Optional[Dict]:
    ensure_rbac_tables()
    if not _load_user_by_identity(user_id=user_id):
        return None
    normalized_org_id = _normalize_org_id(org_id or "")
    _replace_user_roles(user_id, role_ids, normalized_org_id, actor_user_id)
    return get_user_detail(user_id)


def update_user_status(user_id: str, status: str, actor_user_id: str) -> Optional[Dict]:
    ensure_rbac_tables()
    if not _load_user_by_identity(user_id=user_id):
        return None

    normalized_status = _normalize_status(status)
    DatabaseManager().execute_query(
        """
        UPDATE sys_user
        SET status = ?,
            updated_at = SYSDATETIME(),
            updated_by = ?
        WHERE user_id = ?
        """,
        (normalized_status, actor_user_id or None, user_id),
        fetch=False,
    )
    return get_user_detail(user_id)


def reset_user_password(user_id: str, new_password: str, actor_user_id: str) -> Optional[Dict]:
    ensure_rbac_tables()
    if not _load_user_by_identity(user_id=user_id):
        return None
    password = (new_password or "").strip()
    if not password:
        raise ValueError("new_password is required")

    DatabaseManager().execute_query(
        """
        UPDATE sys_user
        SET password_hash = ?,
            updated_at = SYSDATETIME(),
            updated_by = ?
        WHERE user_id = ?
        """,
        (hash_password(password), actor_user_id or None, user_id),
        fetch=False,
    )
    return get_user_detail(user_id)
