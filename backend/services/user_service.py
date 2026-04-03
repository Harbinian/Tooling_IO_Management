# -*- coding: utf-8 -*-
"""User lookup services for non-admin workflow screens."""

from __future__ import annotations

from typing import Dict, List

from backend.database.schema.column_names import ORG_COLUMNS, SYS_USER_COLUMNS
from backend.services.org_service import ensure_org_tables
from backend.services.rbac_service import ensure_rbac_tables
from database import DatabaseManager


def list_users_by_role(role_code: str, org_id: str = "") -> List[Dict]:
    """Return active users bound to one active role, optionally filtered by org."""
    ensure_rbac_tables()
    ensure_org_tables()

    normalized_role_code = (role_code or "").strip()
    if not normalized_role_code:
        raise ValueError("role_code is required")

    normalized_org_id = (org_id or "").strip()
    sql = f"""
    SELECT
        u.[{SYS_USER_COLUMNS['user_id']}] AS [user_id],
        u.[{SYS_USER_COLUMNS['login_name']}] AS [login_name],
        u.[{SYS_USER_COLUMNS['display_name']}] AS [display_name],
        u.[{SYS_USER_COLUMNS['default_org_id']}] AS [default_org_id],
        o.[{ORG_COLUMNS['org_name']}] AS [org_name]
    FROM sys_user u
    INNER JOIN sys_user_role_rel ur ON u.user_id = ur.user_id
    INNER JOIN sys_role r ON ur.role_id = r.role_id
    LEFT JOIN sys_org o ON u.[{SYS_USER_COLUMNS['default_org_id']}] = o.[{ORG_COLUMNS['org_id']}]
    WHERE LOWER(r.role_code) = LOWER(?)
      AND u.[{SYS_USER_COLUMNS['status']}] = 'active'
      AND ur.status = 'active'
      AND r.status = 'active'
    """
    params: List[str] = [normalized_role_code]
    if normalized_org_id:
        sql += f" AND u.[{SYS_USER_COLUMNS['default_org_id']}] = ?"
        params.append(normalized_org_id)
    sql += f" ORDER BY u.[{SYS_USER_COLUMNS['display_name']}] ASC, u.[{SYS_USER_COLUMNS['login_name']}] ASC"

    return DatabaseManager().execute_query(sql, tuple(params))
