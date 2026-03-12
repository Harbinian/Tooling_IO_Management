# -*- coding: utf-8 -*-
"""
Organization service and hierarchy utilities.
"""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Optional, Set

from database import DatabaseManager

logger = logging.getLogger(__name__)

SUPPORTED_ORG_TYPES = {
    "company",
    "factory",
    "workshop",
    "team",
    "warehouse",
    "project_group",
}


def ensure_org_tables() -> bool:
    """Ensure the organization table exists for first-time deployments."""
    create_org_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sys_org' AND xtype='U')
    CREATE TABLE sys_org (
        id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        org_id NVARCHAR(64) NOT NULL,
        org_name NVARCHAR(100) NOT NULL,
        org_code NVARCHAR(100) NULL,
        org_type NVARCHAR(50) NOT NULL,
        parent_org_id NVARCHAR(64) NULL,
        sort_no INT NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        remark NVARCHAR(500) NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        created_by NVARCHAR(64) NULL,
        updated_at DATETIME2 NULL,
        updated_by NVARCHAR(64) NULL
    )
    """

    create_org_unique_index_sql = """
    IF NOT EXISTS (
        SELECT 1 FROM sys.indexes
        WHERE name = 'UX_sys_org_org_id'
          AND object_id = OBJECT_ID(N'sys_org')
    )
    BEGIN
        CREATE UNIQUE INDEX UX_sys_org_org_id ON sys_org(org_id)
    END
    """

    create_parent_index_sql = """
    IF NOT EXISTS (
        SELECT 1 FROM sys.indexes
        WHERE name = 'IX_sys_org_parent_org_id'
          AND object_id = OBJECT_ID(N'sys_org')
    )
    BEGIN
        CREATE INDEX IX_sys_org_parent_org_id ON sys_org(parent_org_id)
    END
    """

    db = DatabaseManager()
    try:
        for sql in (create_org_table_sql, create_org_unique_index_sql, create_parent_index_sql):
            db.execute_query(sql, fetch=False)
        return True
    except Exception as exc:
        logger.error("failed to ensure sys_org table: %s", exc)
        return False


def _normalize_org(record: Dict) -> Dict:
    return {
        "org_id": record.get("org_id", ""),
        "org_name": record.get("org_name", ""),
        "org_code": record.get("org_code", ""),
        "org_type": record.get("org_type", ""),
        "parent_org_id": record.get("parent_org_id", ""),
        "sort_no": record.get("sort_no"),
        "status": record.get("status", ""),
        "remark": record.get("remark", ""),
        "created_at": record.get("created_at"),
        "updated_at": record.get("updated_at"),
    }


def list_organizations(include_disabled: bool = True) -> List[Dict]:
    """Return all organizations ordered for tree rendering."""
    ensure_org_tables()

    sql = """
    SELECT
        org_id,
        org_name,
        org_code,
        org_type,
        parent_org_id,
        sort_no,
        status,
        remark,
        created_at,
        updated_at
    FROM sys_org
    """
    params: List[str] = []
    if not include_disabled:
        sql += " WHERE status = 'active'"

    sql += " ORDER BY COALESCE(sort_no, 2147483647), org_name ASC"
    return [_normalize_org(row) for row in DatabaseManager().execute_query(sql, tuple(params))]


def get_organization(org_id: str) -> Optional[Dict]:
    """Return one organization by org_id."""
    ensure_org_tables()

    rows = DatabaseManager().execute_query(
        """
        SELECT
            org_id,
            org_name,
            org_code,
            org_type,
            parent_org_id,
            sort_no,
            status,
            remark,
            created_at,
            updated_at
        FROM sys_org
        WHERE org_id = ?
        """,
        (org_id,),
    )
    return _normalize_org(rows[0]) if rows else None


def build_org_tree(records: Iterable[Dict]) -> List[Dict]:
    """Build a nested organization tree."""
    nodes = {}
    roots = []

    for record in records:
        node = {**_normalize_org(record), "children": []}
        nodes[node["org_id"]] = node

    for node in nodes.values():
        parent_org_id = node.get("parent_org_id") or ""
        parent = nodes.get(parent_org_id)
        if parent:
            parent["children"].append(node)
        else:
            roots.append(node)

    def sort_children(children: List[Dict]) -> List[Dict]:
        children.sort(key=lambda item: ((item.get("sort_no") is None), item.get("sort_no") or 0, item.get("org_name") or ""))
        for child in children:
            sort_children(child["children"])
        return children

    return sort_children(roots)


def get_org_tree(include_disabled: bool = True) -> List[Dict]:
    """Return the organization tree."""
    return build_org_tree(list_organizations(include_disabled=include_disabled))


def _validate_org_type(org_type: str) -> None:
    if org_type not in SUPPORTED_ORG_TYPES:
        raise ValueError(f"org_type must be one of: {', '.join(sorted(SUPPORTED_ORG_TYPES))}")


def _validate_parent(org_id: str, parent_org_id: str) -> None:
    if not parent_org_id:
        return

    if parent_org_id == org_id:
        raise ValueError("organization cannot be its own parent")

    parent = get_organization(parent_org_id)
    if not parent:
        raise ValueError("parent organization does not exist")


def _detect_cycle(org_id: str, parent_org_id: str) -> None:
    if not parent_org_id:
        return

    visited: Set[str] = {org_id}
    current_parent = parent_org_id
    while current_parent:
        if current_parent in visited:
            raise ValueError("organization hierarchy would create a cycle")
        visited.add(current_parent)
        parent = get_organization(current_parent)
        current_parent = parent.get("parent_org_id", "") if parent else ""


def create_organization(payload: Dict, actor_user_id: str = "") -> Dict:
    """Create one organization."""
    ensure_org_tables()

    org_id = (payload.get("org_id") or "").strip()
    org_name = (payload.get("org_name") or "").strip()
    org_type = (payload.get("org_type") or "").strip()
    parent_org_id = (payload.get("parent_org_id") or "").strip()
    status = (payload.get("status") or "active").strip() or "active"

    if not org_id:
        raise ValueError("org_id is required")
    if not org_name:
        raise ValueError("org_name is required")
    _validate_org_type(org_type)
    _validate_parent(org_id, parent_org_id)

    if get_organization(org_id):
        raise ValueError("org_id already exists")

    DatabaseManager().execute_query(
        """
        INSERT INTO sys_org (
            org_id, org_name, org_code, org_type, parent_org_id, sort_no,
            status, remark, created_at, created_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME(), ?)
        """,
        (
            org_id,
            org_name,
            payload.get("org_code"),
            org_type,
            parent_org_id or None,
            payload.get("sort_no"),
            status,
            payload.get("remark"),
            actor_user_id or None,
        ),
        fetch=False,
    )
    return {"success": True, "data": get_organization(org_id)}


def update_organization(org_id: str, payload: Dict, actor_user_id: str = "") -> Dict:
    """Update one organization."""
    ensure_org_tables()

    existing = get_organization(org_id)
    if not existing:
        return {"success": False, "error": "organization not found"}

    org_name = (payload.get("org_name", existing.get("org_name")) or "").strip()
    org_type = (payload.get("org_type", existing.get("org_type")) or "").strip()
    parent_org_id = (payload.get("parent_org_id", existing.get("parent_org_id")) or "").strip()
    status = (payload.get("status", existing.get("status")) or "").strip()

    if not org_name:
        raise ValueError("org_name is required")
    _validate_org_type(org_type)
    _validate_parent(org_id, parent_org_id)
    _detect_cycle(org_id, parent_org_id)

    DatabaseManager().execute_query(
        """
        UPDATE sys_org
        SET org_name = ?,
            org_code = ?,
            org_type = ?,
            parent_org_id = ?,
            sort_no = ?,
            status = ?,
            remark = ?,
            updated_at = SYSDATETIME(),
            updated_by = ?
        WHERE org_id = ?
        """,
        (
            org_name,
            payload.get("org_code", existing.get("org_code")),
            org_type,
            parent_org_id or None,
            payload.get("sort_no", existing.get("sort_no")),
            status,
            payload.get("remark", existing.get("remark")),
            actor_user_id or None,
            org_id,
        ),
        fetch=False,
    )
    return {"success": True, "data": get_organization(org_id)}


def get_descendant_org_ids(org_id: str) -> List[str]:
    """Return one org_id plus all descendant org_ids."""
    records = list_organizations(include_disabled=True)
    children_by_parent: Dict[str, List[str]] = {}
    for record in records:
        parent_org_id = record.get("parent_org_id") or ""
        children_by_parent.setdefault(parent_org_id, []).append(record.get("org_id", ""))

    result: List[str] = []
    stack = [org_id]
    while stack:
        current = stack.pop()
        if current in result:
            continue
        result.append(current)
        stack.extend(children_by_parent.get(current, []))
    return result


def get_role_assignments_with_org_context(user_id: str) -> List[Dict]:
    """Return user role assignments enriched with organization details."""
    ensure_org_tables()

    sql = """
    SELECT
        rel.role_id,
        rel.org_id,
        rel.is_primary,
        role.role_code,
        role.role_name,
        org.org_name,
        org.org_type,
        org.status AS org_status
    FROM sys_user_role_rel rel
    INNER JOIN sys_role role ON role.role_id = rel.role_id
    LEFT JOIN sys_org org ON org.org_id = rel.org_id
    WHERE rel.user_id = ?
      AND rel.status = 'active'
      AND role.status = 'active'
    ORDER BY rel.is_primary DESC, role.role_code ASC
    """
    return DatabaseManager().execute_query(sql, (user_id,))


def resolve_user_org_context(user_id: str, default_org_id: str = "") -> Dict:
    """Resolve default and current organization context for one user."""
    role_assignments = get_role_assignments_with_org_context(user_id)
    default_org = get_organization(default_org_id) if default_org_id else None
    current_org = None

    for assignment in role_assignments:
        if assignment.get("org_id"):
            current_org = get_organization(assignment["org_id"])
            if current_org:
                break

    if current_org is None:
        current_org = default_org

    role_orgs = []
    seen_org_ids: Set[str] = set()
    for assignment in role_assignments:
        org_id = assignment.get("org_id") or ""
        if not org_id or org_id in seen_org_ids:
            continue
        seen_org_ids.add(org_id)
        role_orgs.append(
            {
                "org_id": org_id,
                "org_name": assignment.get("org_name", ""),
                "org_type": assignment.get("org_type", ""),
                "status": assignment.get("org_status", ""),
            }
        )

    return {
        "default_org": default_org,
        "current_org": current_org,
        "role_orgs": role_orgs,
    }


def get_bootstrap_org_sql() -> str:
    """Return SQL example for initial organization bootstrap."""
    return """
INSERT INTO sys_org (org_id, org_name, org_code, org_type, parent_org_id, sort_no, status, created_at, created_by)
VALUES
('ORG_COMPANY', 'Example Company', 'COMPANY', 'company', NULL, 1, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_FACTORY', 'Factory A', 'FACTORY_A', 'factory', 'ORG_COMPANY', 10, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_WORKSHOP', 'Workshop 1', 'WORKSHOP_1', 'workshop', 'ORG_FACTORY', 20, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_TEAM', 'Team Alpha', 'TEAM_ALPHA', 'team', 'ORG_WORKSHOP', 30, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_WAREHOUSE', 'Warehouse East', 'WAREHOUSE_E', 'warehouse', 'ORG_FACTORY', 40, 'active', SYSDATETIME(), 'bootstrap');
""".strip()
