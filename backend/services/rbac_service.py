# -*- coding: utf-8 -*-
"""
RBAC permission resolution helpers for the Tooling IO Management System.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Sequence, Set

from database import DatabaseManager

logger = logging.getLogger(__name__)


def ensure_rbac_tables() -> bool:
    """Ensure all RBAC system tables exist."""
    db = DatabaseManager()
    
    # Table definitions
    tables = {
        "sys_user": """
            CREATE TABLE sys_user (
                id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
                user_id NVARCHAR(64) NOT NULL,
                login_name NVARCHAR(100) NOT NULL,
                display_name NVARCHAR(100) NOT NULL,
                employee_no NVARCHAR(100) NULL,
                password_hash NVARCHAR(255) NOT NULL,
                mobile NVARCHAR(50) NULL,
                email NVARCHAR(100) NULL,
                status NVARCHAR(20) NOT NULL DEFAULT 'active',
                default_org_id NVARCHAR(64) NULL,
                last_login_at DATETIME2 NULL,
                remark NVARCHAR(500) NULL,
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                created_by NVARCHAR(64) NULL,
                updated_at DATETIME2 NULL,
                updated_by NVARCHAR(64) NULL
            )
        """,
        "sys_role": """
            CREATE TABLE sys_role (
                id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
                role_id NVARCHAR(64) NOT NULL,
                role_code NVARCHAR(100) NOT NULL,
                role_name NVARCHAR(100) NOT NULL,
                role_type NVARCHAR(50) NOT NULL,
                status NVARCHAR(20) NOT NULL DEFAULT 'active',
                remark NVARCHAR(500) NULL,
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                created_by NVARCHAR(64) NULL,
                updated_at DATETIME2 NULL,
                updated_by NVARCHAR(64) NULL
            )
        """,
        "sys_permission": """
            CREATE TABLE sys_permission (
                id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
                permission_code NVARCHAR(100) NOT NULL,
                permission_name NVARCHAR(100) NOT NULL,
                resource_name NVARCHAR(100) NOT NULL,
                action_name NVARCHAR(100) NOT NULL,
                status NVARCHAR(20) NOT NULL DEFAULT 'active',
                remark NVARCHAR(500) NULL,
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                created_by NVARCHAR(64) NULL,
                updated_at DATETIME2 NULL,
                updated_by NVARCHAR(64) NULL
            )
        """,
        "sys_user_role_rel": """
            CREATE TABLE sys_user_role_rel (
                id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
                user_id NVARCHAR(64) NOT NULL,
                role_id NVARCHAR(64) NOT NULL,
                org_id NVARCHAR(64) NULL,
                is_primary BIT NOT NULL DEFAULT 0,
                status NVARCHAR(20) NOT NULL DEFAULT 'active',
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                created_by NVARCHAR(64) NULL,
                updated_at DATETIME2 NULL,
                updated_by NVARCHAR(64) NULL
            )
        """,
        "sys_role_permission_rel": """
            CREATE TABLE sys_role_permission_rel (
                id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
                role_id NVARCHAR(64) NOT NULL,
                permission_code NVARCHAR(100) NOT NULL,
                status NVARCHAR(20) NOT NULL DEFAULT 'active',
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                created_by NVARCHAR(64) NULL,
                updated_at DATETIME2 NULL,
                updated_by NVARCHAR(64) NULL
            )
        """,
        "sys_role_data_scope_rel": """
            CREATE TABLE sys_role_data_scope_rel (
                id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
                role_id NVARCHAR(64) NOT NULL,
                scope_type NVARCHAR(50) NOT NULL,
                scope_value NVARCHAR(500) NULL,
                status NVARCHAR(20) NOT NULL DEFAULT 'active',
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                created_by NVARCHAR(64) NULL,
                updated_at DATETIME2 NULL,
                updated_by NVARCHAR(64) NULL
            )
        """
    }

    try:
        for table_name, create_sql in tables.items():
            check_sql = f"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U') BEGIN {create_sql} END"
            db.execute_query(check_sql, fetch=False)

        db.execute_query(
            """
            IF COL_LENGTH(N'sys_user', N'employee_no') IS NULL
            BEGIN
                ALTER TABLE sys_user ADD employee_no NVARCHAR(100) NULL
            END
            """,
            fetch=False,
        )
        
        # Add indexes
        indexes = [
            "IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_sys_user_user_id' AND object_id = OBJECT_ID(N'sys_user')) CREATE UNIQUE INDEX UX_sys_user_user_id ON sys_user(user_id)",
            "IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_sys_user_login_name' AND object_id = OBJECT_ID(N'sys_user')) CREATE UNIQUE INDEX UX_sys_user_login_name ON sys_user(login_name)",
            "IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_sys_user_employee_no' AND object_id = OBJECT_ID(N'sys_user')) CREATE UNIQUE INDEX UX_sys_user_employee_no ON sys_user(employee_no) WHERE employee_no IS NOT NULL"
        ]
        for idx_sql in indexes:
            db.execute_query(idx_sql, fetch=False)
            
        # Bootstrap data if empty
        _bootstrap_initial_data(db)
        _ensure_incremental_permission_defaults(db)
            
        return True
    except Exception as exc:
        logger.error("failed to ensure RBAC tables: %s", exc)
        return False


def _bootstrap_initial_data(db: DatabaseManager):
    """Insert initial roles, permissions and admin user if tables are empty."""
    # 1. Roles
    role_count = db.execute_query("SELECT COUNT(*) as cnt FROM sys_role")[0]["cnt"]
    if role_count == 0:
        logger.info("Bootstrapping initial roles...")
        db.execute_query("""
            INSERT INTO sys_role (role_id, role_code, role_name, role_type)
            VALUES
            ('ROLE_TEAM_LEADER', 'team_leader', 'Team Leader', 'business'),
            ('ROLE_KEEPER', 'keeper', 'Keeper', 'business'),
            ('ROLE_PLANNER', 'planner', 'Planner', 'business'),
            ('ROLE_SYS_ADMIN', 'sys_admin', 'System Administrator', 'system'),
            ('ROLE_AUDITOR', 'auditor', 'Auditor', 'system')
        """, fetch=False)

    # 2. Permissions
    perm_count = db.execute_query("SELECT COUNT(*) as cnt FROM sys_permission")[0]["cnt"]
    if perm_count == 0:
        logger.info("Bootstrapping initial permissions...")
        db.execute_query("""
            INSERT INTO sys_permission (permission_code, permission_name, resource_name, action_name)
            VALUES
            ('dashboard:view', 'View Dashboard', 'dashboard', 'view'),
            ('tool:search', 'Search Tools', 'tool', 'search'),
            ('tool:view', 'View Tool', 'tool', 'view'),
            ('tool:location_view', 'View Tool Location', 'tool', 'location_view'),
            ('order:create', 'Create Order', 'order', 'create'),
            ('order:view', 'View Order', 'order', 'view'),
            ('order:list', 'List Orders', 'order', 'list'),
            ('order:submit', 'Submit Order', 'order', 'submit'),
            ('order:keeper_confirm', 'Keeper Confirm Order', 'order', 'keeper_confirm'),
            ('order:final_confirm', 'Final Confirm Order', 'order', 'final_confirm'),
            ('order:cancel', 'Cancel Order', 'order', 'cancel'),
            ('notification:view', 'View Notification', 'notification', 'view'),
            ('notification:create', 'Create Notification', 'notification', 'create'),
            ('notification:send_feishu', 'Send Feishu Notification', 'notification', 'send_feishu'),
            ('log:view', 'View System Log', 'log', 'view'),
            ('admin:user_manage', 'Manage Users', 'admin', 'user_manage'),
            ('admin:role_manage', 'Manage Roles', 'admin', 'role_manage')
        """, fetch=False)

    # 3. Role-Permission Relations
    rp_count = db.execute_query("SELECT COUNT(*) as cnt FROM sys_role_permission_rel")[0]["cnt"]
    if rp_count == 0:
        logger.info("Bootstrapping role-permission relations...")
        # Sys Admin gets all
        db.execute_query("""
            INSERT INTO sys_role_permission_rel (role_id, permission_code)
            SELECT 'ROLE_SYS_ADMIN', permission_code FROM sys_permission
        """, fetch=False)
        # Other roles (simplified for bootstrap)
        db.execute_query("""
            INSERT INTO sys_role_permission_rel (role_id, permission_code)
            VALUES
            ('ROLE_TEAM_LEADER', 'dashboard:view'),
            ('ROLE_TEAM_LEADER', 'tool:search'),
            ('ROLE_TEAM_LEADER', 'order:create'),
            ('ROLE_TEAM_LEADER', 'order:list'),
            ('ROLE_TEAM_LEADER', 'order:submit'),
            ('ROLE_KEEPER', 'dashboard:view'),
            ('ROLE_KEEPER', 'order:list'),
            ('ROLE_KEEPER', 'order:keeper_confirm')
        """, fetch=False)

    # 4. Admin User
    user_count = db.execute_query("SELECT COUNT(*) as cnt FROM sys_user")[0]["cnt"]
    if user_count == 0:
        logger.info("Bootstrapping initial admin user...")
        from backend.services.auth_service import hash_password
        # password is 'admin123'
        admin_pwd_hash = hash_password("admin123")
        db.execute_query("""
            INSERT INTO sys_user (user_id, login_name, display_name, password_hash, status, created_at, created_by)
            VALUES ('U_ADMIN', 'admin', 'System Administrator', ?, 'active', SYSDATETIME(), 'bootstrap')
        """, (admin_pwd_hash,), fetch=False)
        db.execute_query("""
            INSERT INTO sys_user_role_rel (user_id, role_id, is_primary, status, created_at, created_by)
            VALUES ('U_ADMIN', 'ROLE_SYS_ADMIN', 1, 'active', SYSDATETIME(), 'bootstrap')
        """, fetch=False)


def _ensure_incremental_permission_defaults(db: DatabaseManager):
    """Ensure newly introduced permissions exist in upgraded environments."""
    db.execute_query(
        """
        IF NOT EXISTS (SELECT 1 FROM sys_permission WHERE permission_code = 'order:transport_execute')
        BEGIN
            INSERT INTO sys_permission (permission_code, permission_name, resource_name, action_name)
            VALUES ('order:transport_execute', 'Execute Transport Workflow', 'order', 'transport_execute')
        END
        """,
        fetch=False,
    )
    db.execute_query(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys_role_permission_rel
            WHERE role_id = 'ROLE_KEEPER' AND permission_code = 'order:transport_execute'
        )
        BEGIN
            INSERT INTO sys_role_permission_rel (role_id, permission_code)
            VALUES ('ROLE_KEEPER', 'order:transport_execute')
        END
        """,
        fetch=False,
    )
    db.execute_query(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys_role_permission_rel
            WHERE role_id = 'ROLE_SYS_ADMIN' AND permission_code = 'order:transport_execute'
        )
        BEGIN
            INSERT INTO sys_role_permission_rel (role_id, permission_code)
            VALUES ('ROLE_SYS_ADMIN', 'order:transport_execute')
        END
        """,
        fetch=False,
    )


def _normalize_role(record: Dict) -> Dict:
    return {
        "role_id": record.get("role_id", ""),
        "role_code": record.get("role_code", ""),
        "role_name": record.get("role_name", ""),
        "org_id": record.get("org_id", ""),
        "org_name": record.get("org_name", ""),
        "org_type": record.get("org_type", ""),
        "org_status": record.get("org_status", ""),
        "is_primary": bool(record.get("is_primary")),
    }


def load_user_roles(user_id: str) -> List[Dict]:
    """Load active role assignments with organization context."""
    if not user_id:
        return []

    from backend.services.org_service import ensure_org_tables

    ensure_rbac_tables()
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
    return [_normalize_role(row) for row in DatabaseManager().execute_query(sql, (user_id,))]


def load_permissions_for_role_ids(role_ids: Sequence[str]) -> List[str]:
    """Load distinct active permissions for one or more roles."""
    normalized_role_ids = [role_id for role_id in role_ids if role_id]
    if not normalized_role_ids:
        return []

    placeholders = ",".join(["?"] * len(normalized_role_ids))
    sql = f"""
    SELECT DISTINCT rel.permission_code
    FROM sys_role_permission_rel rel
    INNER JOIN sys_permission perm ON perm.permission_code = rel.permission_code
    WHERE rel.role_id IN ({placeholders})
      AND rel.status = 'active'
      AND perm.status = 'active'
    ORDER BY rel.permission_code ASC
    """
    rows = DatabaseManager().execute_query(sql, tuple(normalized_role_ids))
    return [row.get("permission_code", "") for row in rows if row.get("permission_code")]


def resolve_user_permissions(user_id: str, roles: Optional[Sequence[Dict]] = None) -> List[str]:
    """Resolve a normalized permission list for the current user."""
    role_records = list(roles) if roles is not None else load_user_roles(user_id)
    role_ids = [role.get("role_id", "") for role in role_records if role.get("role_id")]
    return load_permissions_for_role_ids(role_ids)


def build_permission_context(user_id: str, roles: Optional[Sequence[Dict]] = None) -> Dict:
    """Build a permission-aware authorization context."""
    role_records = list(roles) if roles is not None else load_user_roles(user_id)
    permissions = resolve_user_permissions(user_id, role_records)
    return {
        "user_id": user_id,
        "roles": role_records,
        "role_codes": [role.get("role_code", "") for role in role_records if role.get("role_code")],
        "permissions": permissions,
    }


def has_permission(user: Optional[Dict], permission_code: str) -> bool:
    """Return whether the resolved user has the requested permission."""
    if not user or not permission_code:
        return False
    permission_set: Set[str] = set(user.get("permissions") or [])
    return permission_code in permission_set
