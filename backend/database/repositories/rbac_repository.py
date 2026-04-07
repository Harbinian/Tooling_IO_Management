# -*- coding: utf-8 -*-
"""
Repository for RBAC role and permission management.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from backend.database.core.database_manager import DatabaseManager
from backend.database.schema.column_names import (
    PERMISSION_COLUMNS,
    ROLE_COLUMNS,
    ROLE_PERMISSION_REL_COLUMNS,
    USER_ROLE_REL_COLUMNS,
)


class RbacRepository:
    """Repository for role, permission and role-permission operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self._db = db_manager or DatabaseManager()

    @staticmethod
    def _normalize_status(value: str, *, default: str = "active") -> str:
        normalized = (value or default).strip().lower()
        if normalized not in {"active", "disabled"}:
            raise ValueError("status must be active or disabled")
        return normalized

    @staticmethod
    def _normalize_role_type(value: str, *, default: str = "business") -> str:
        normalized = (value or default).strip().lower()
        if normalized not in {"business", "system"}:
            raise ValueError("role_type must be business or system")
        return normalized

    @staticmethod
    def _trim_text(value: str, field_name: str, *, required: bool = False, max_length: int = 100) -> str:
        normalized = (value or "").strip()
        if required and not normalized:
            raise ValueError(f"{field_name} is required")
        if len(normalized) > max_length:
            raise ValueError(f"{field_name} is too long")
        return normalized

    def get_roles(
        self,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        role_type: Optional[str] = None,
    ) -> List[Dict]:
        sql = f"""
        SELECT
            role.[{ROLE_COLUMNS['role_id']}],
            role.[{ROLE_COLUMNS['role_code']}],
            role.[{ROLE_COLUMNS['role_name']}],
            role.[{ROLE_COLUMNS['role_type']}],
            role.[{ROLE_COLUMNS['status']}],
            role.[{ROLE_COLUMNS['remark']}],
            role.[{ROLE_COLUMNS['created_at']}],
            role.[{ROLE_COLUMNS['updated_at']}],
            (
                SELECT COUNT(1)
                FROM sys_role_permission_rel rel
                WHERE rel.[{ROLE_PERMISSION_REL_COLUMNS['role_id']}] = role.[{ROLE_COLUMNS['role_id']}]
                  AND rel.[{ROLE_PERMISSION_REL_COLUMNS['status']}] = 'active'
            ) AS permission_count
        FROM sys_role role
        WHERE 1 = 1
        """
        params: List[str] = []

        normalized_keyword = (keyword or "").strip()
        if normalized_keyword:
            like_value = f"%{normalized_keyword}%"
            sql += f"""
            AND (
                role.[{ROLE_COLUMNS['role_code']}] LIKE ?
                OR role.[{ROLE_COLUMNS['role_name']}] LIKE ?
            )
            """
            params.extend([like_value, like_value])

        normalized_status = (status or "").strip().lower()
        if normalized_status:
            sql += f" AND role.[{ROLE_COLUMNS['status']}] = ?"
            params.append(self._normalize_status(normalized_status))

        normalized_role_type = (role_type or "").strip().lower()
        if normalized_role_type:
            sql += f" AND role.[{ROLE_COLUMNS['role_type']}] = ?"
            params.append(self._normalize_role_type(normalized_role_type))

        sql += f"""
        ORDER BY
            CASE role.[{ROLE_COLUMNS['role_type']}] WHEN 'system' THEN 0 ELSE 1 END,
            role.[{ROLE_COLUMNS['role_code']}] ASC
        """
        return self._db.execute_query(sql, tuple(params))

    def get_role_by_id(self, role_id: str) -> Optional[Dict]:
        normalized_role_id = self._trim_text(role_id, "role_id", required=True, max_length=64)
        sql = f"""
        SELECT TOP 1
            [{ROLE_COLUMNS['role_id']}],
            [{ROLE_COLUMNS['role_code']}],
            [{ROLE_COLUMNS['role_name']}],
            [{ROLE_COLUMNS['role_type']}],
            [{ROLE_COLUMNS['status']}],
            [{ROLE_COLUMNS['remark']}],
            [{ROLE_COLUMNS['created_at']}],
            [{ROLE_COLUMNS['created_by']}],
            [{ROLE_COLUMNS['updated_at']}],
            [{ROLE_COLUMNS['updated_by']}]
        FROM sys_role
        WHERE [{ROLE_COLUMNS['role_id']}] = ?
        """
        rows = self._db.execute_query(sql, (normalized_role_id,))
        return rows[0] if rows else None

    def create_role(self, role_data: Dict, *, actor_user_id: str = "") -> Dict:
        role_code = self._trim_text(role_data.get("role_code"), "role_code", required=True)
        role_name = self._trim_text(role_data.get("role_name"), "role_name", required=True)
        role_type = self._normalize_role_type(role_data.get("role_type"))
        status = self._normalize_status(role_data.get("status"))
        remark = self._trim_text(role_data.get("remark"), "remark", max_length=500)

        if self._load_role_by_code(role_code):
            raise ValueError("role_code already exists")

        role_id = f"ROLE_{uuid4().hex[:16].upper()}"

        def _tx(conn) -> None:
            self._db.execute_query(
                f"""
                INSERT INTO sys_role (
                    [{ROLE_COLUMNS['role_id']}],
                    [{ROLE_COLUMNS['role_code']}],
                    [{ROLE_COLUMNS['role_name']}],
                    [{ROLE_COLUMNS['role_type']}],
                    [{ROLE_COLUMNS['status']}],
                    [{ROLE_COLUMNS['remark']}],
                    [{ROLE_COLUMNS['created_at']}],
                    [{ROLE_COLUMNS['created_by']}]
                ) VALUES (?, ?, ?, ?, ?, ?, SYSDATETIME(), ?)
                """,
                (role_id, role_code, role_name, role_type, status, remark or None, actor_user_id or None),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return self.get_role_by_id(role_id) or {}

    def update_role(self, role_id: str, role_data: Dict, *, actor_user_id: str = "") -> Optional[Dict]:
        existing = self.get_role_by_id(role_id)
        if not existing:
            return None

        role_code = self._trim_text(role_data.get("role_code", existing.get("role_code")), "role_code", required=True)
        role_name = self._trim_text(role_data.get("role_name", existing.get("role_name")), "role_name", required=True)
        role_type = self._normalize_role_type(role_data.get("role_type", existing.get("role_type")))
        status = self._normalize_status(role_data.get("status", existing.get("status")))
        remark = self._trim_text(role_data.get("remark", existing.get("remark")), "remark", max_length=500)

        duplicate = self._load_role_by_code(role_code)
        if duplicate and duplicate.get(ROLE_COLUMNS["role_id"]) != existing.get(ROLE_COLUMNS["role_id"]):
            raise ValueError("role_code already exists")

        if (existing.get(ROLE_COLUMNS["role_type"]) or "").lower() == "system" and role_type != "system":
            raise ValueError("system role type cannot be changed")

        def _tx(conn) -> None:
            self._db.execute_query(
                f"""
                UPDATE sys_role
                SET [{ROLE_COLUMNS['role_code']}] = ?,
                    [{ROLE_COLUMNS['role_name']}] = ?,
                    [{ROLE_COLUMNS['role_type']}] = ?,
                    [{ROLE_COLUMNS['status']}] = ?,
                    [{ROLE_COLUMNS['remark']}] = ?,
                    [{ROLE_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{ROLE_COLUMNS['updated_by']}] = ?
                WHERE [{ROLE_COLUMNS['role_id']}] = ?
                """,
                (role_code, role_name, role_type, status, remark or None, actor_user_id or None, role_id),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return self.get_role_by_id(role_id)

    def delete_role(self, role_id: str) -> Tuple[bool, str]:
        existing = self.get_role_by_id(role_id)
        if not existing:
            return False, "role not found"

        if (existing.get(ROLE_COLUMNS["role_type"]) or "").lower() == "system":
            return False, "system roles cannot be deleted"

        usage_sql = f"""
        SELECT COUNT(1) AS cnt
        FROM sys_user_role_rel
        WHERE [{USER_ROLE_REL_COLUMNS['role_id']}] = ?
          AND [{USER_ROLE_REL_COLUMNS['status']}] = 'active'
        """
        usage_rows = self._db.execute_query(usage_sql, (role_id,))
        if usage_rows and int(usage_rows[0].get("cnt", 0) or 0) > 0:
            return False, "role is assigned to users"

        def _tx(conn) -> None:
            self._db.execute_query(
                f"DELETE FROM sys_role_permission_rel WHERE [{ROLE_PERMISSION_REL_COLUMNS['role_id']}] = ?",
                (role_id,),
                fetch=False,
                conn=conn,
            )
            self._db.execute_query(
                "DELETE FROM sys_role_data_scope_rel WHERE role_id = ?",
                (role_id,),
                fetch=False,
                conn=conn,
            )
            self._db.execute_query(
                f"DELETE FROM sys_role WHERE [{ROLE_COLUMNS['role_id']}] = ?",
                (role_id,),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return True, ""

    def get_permissions(
        self,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        if page <= 0 or page_size <= 0:
            raise ValueError("page and page_size must be greater than 0")

        where_sql = "WHERE 1 = 1"
        params: List[str] = []

        normalized_keyword = (keyword or "").strip()
        if normalized_keyword:
            like_value = f"%{normalized_keyword}%"
            where_sql += f"""
             AND (
                perm.[{PERMISSION_COLUMNS['permission_code']}] LIKE ?
                OR perm.[{PERMISSION_COLUMNS['permission_name']}] LIKE ?
                OR perm.[{PERMISSION_COLUMNS['resource_name']}] LIKE ?
                OR perm.[{PERMISSION_COLUMNS['action_name']}] LIKE ?
             )
            """
            params.extend([like_value, like_value, like_value, like_value])

        normalized_status = (status or "").strip().lower()
        if normalized_status:
            where_sql += f" AND perm.[{PERMISSION_COLUMNS['status']}] = ?"
            params.append(self._normalize_status(normalized_status))

        total_rows = self._db.execute_query(
            f"SELECT COUNT(1) AS cnt FROM sys_permission perm {where_sql}",
            tuple(params),
        )
        total = int(total_rows[0].get("cnt", 0) or 0)
        offset = (page - 1) * page_size

        sql = f"""
        SELECT
            perm.[{PERMISSION_COLUMNS['permission_code']}],
            perm.[{PERMISSION_COLUMNS['permission_name']}],
            perm.[{PERMISSION_COLUMNS['resource_name']}],
            perm.[{PERMISSION_COLUMNS['action_name']}],
            perm.[{PERMISSION_COLUMNS['status']}],
            perm.[{PERMISSION_COLUMNS['remark']}],
            perm.[{PERMISSION_COLUMNS['created_at']}],
            perm.[{PERMISSION_COLUMNS['updated_at']}],
            (
                SELECT COUNT(1)
                FROM sys_role_permission_rel rel
                WHERE rel.[{ROLE_PERMISSION_REL_COLUMNS['permission_code']}] = perm.[{PERMISSION_COLUMNS['permission_code']}]
                  AND rel.[{ROLE_PERMISSION_REL_COLUMNS['status']}] = 'active'
            ) AS role_count
        FROM sys_permission perm
        {where_sql}
        ORDER BY perm.[{PERMISSION_COLUMNS['resource_name']}] ASC, perm.[{PERMISSION_COLUMNS['permission_code']}] ASC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """
        rows = self._db.execute_query(sql, tuple(params + [offset, page_size]))
        return {"items": rows, "total": total, "page": page, "page_size": page_size}

    def get_permission_by_code(self, permission_code: str) -> Optional[Dict]:
        normalized_code = self._trim_text(permission_code, "permission_code", required=True)
        sql = f"""
        SELECT TOP 1
            [{PERMISSION_COLUMNS['permission_code']}],
            [{PERMISSION_COLUMNS['permission_name']}],
            [{PERMISSION_COLUMNS['resource_name']}],
            [{PERMISSION_COLUMNS['action_name']}],
            [{PERMISSION_COLUMNS['status']}],
            [{PERMISSION_COLUMNS['remark']}],
            [{PERMISSION_COLUMNS['created_at']}],
            [{PERMISSION_COLUMNS['created_by']}],
            [{PERMISSION_COLUMNS['updated_at']}],
            [{PERMISSION_COLUMNS['updated_by']}]
        FROM sys_permission
        WHERE [{PERMISSION_COLUMNS['permission_code']}] = ?
        """
        rows = self._db.execute_query(sql, (normalized_code,))
        return rows[0] if rows else None

    def create_permission(self, permission_data: Dict, *, actor_user_id: str = "") -> Dict:
        permission_code = self._trim_text(permission_data.get("permission_code"), "permission_code", required=True)
        permission_name = self._trim_text(permission_data.get("permission_name"), "permission_name", required=True)
        resource_name = self._trim_text(permission_data.get("resource_name"), "resource_name", required=True)
        action_name = self._trim_text(permission_data.get("action_name"), "action_name", required=True)
        status = self._normalize_status(permission_data.get("status"))
        remark = self._trim_text(permission_data.get("remark"), "remark", max_length=500)

        if self.get_permission_by_code(permission_code):
            raise ValueError("permission_code already exists")

        def _tx(conn) -> None:
            self._db.execute_query(
                f"""
                INSERT INTO sys_permission (
                    [{PERMISSION_COLUMNS['permission_code']}],
                    [{PERMISSION_COLUMNS['permission_name']}],
                    [{PERMISSION_COLUMNS['resource_name']}],
                    [{PERMISSION_COLUMNS['action_name']}],
                    [{PERMISSION_COLUMNS['status']}],
                    [{PERMISSION_COLUMNS['remark']}],
                    [{PERMISSION_COLUMNS['created_at']}],
                    [{PERMISSION_COLUMNS['created_by']}]
                ) VALUES (?, ?, ?, ?, ?, ?, SYSDATETIME(), ?)
                """,
                (
                    permission_code,
                    permission_name,
                    resource_name,
                    action_name,
                    status,
                    remark or None,
                    actor_user_id or None,
                ),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return self.get_permission_by_code(permission_code) or {}

    def update_permission(
        self,
        permission_code: str,
        permission_data: Dict,
        *,
        actor_user_id: str = "",
    ) -> Optional[Dict]:
        existing = self.get_permission_by_code(permission_code)
        if not existing:
            return None

        next_permission_code = self._trim_text(
            permission_data.get("permission_code", existing.get("permission_code")),
            "permission_code",
            required=True,
        )
        permission_name = self._trim_text(
            permission_data.get("permission_name", existing.get("permission_name")),
            "permission_name",
            required=True,
        )
        resource_name = self._trim_text(
            permission_data.get("resource_name", existing.get("resource_name")),
            "resource_name",
            required=True,
        )
        action_name = self._trim_text(
            permission_data.get("action_name", existing.get("action_name")),
            "action_name",
            required=True,
        )
        status = self._normalize_status(permission_data.get("status", existing.get("status")))
        remark = self._trim_text(permission_data.get("remark", existing.get("remark")), "remark", max_length=500)

        duplicate = self.get_permission_by_code(next_permission_code)
        if duplicate and duplicate.get(PERMISSION_COLUMNS["permission_code"]) != existing.get(PERMISSION_COLUMNS["permission_code"]):
            raise ValueError("permission_code already exists")

        def _tx(conn) -> None:
            if next_permission_code != permission_code:
                self._db.execute_query(
                    f"""
                    UPDATE sys_role_permission_rel
                    SET [{ROLE_PERMISSION_REL_COLUMNS['permission_code']}] = ?,
                        [{ROLE_PERMISSION_REL_COLUMNS['updated_at']}] = SYSDATETIME(),
                        [{ROLE_PERMISSION_REL_COLUMNS['updated_by']}] = ?
                    WHERE [{ROLE_PERMISSION_REL_COLUMNS['permission_code']}] = ?
                    """,
                    (next_permission_code, actor_user_id or None, permission_code),
                    fetch=False,
                    conn=conn,
                )

            self._db.execute_query(
                f"""
                UPDATE sys_permission
                SET [{PERMISSION_COLUMNS['permission_code']}] = ?,
                    [{PERMISSION_COLUMNS['permission_name']}] = ?,
                    [{PERMISSION_COLUMNS['resource_name']}] = ?,
                    [{PERMISSION_COLUMNS['action_name']}] = ?,
                    [{PERMISSION_COLUMNS['status']}] = ?,
                    [{PERMISSION_COLUMNS['remark']}] = ?,
                    [{PERMISSION_COLUMNS['updated_at']}] = SYSDATETIME(),
                    [{PERMISSION_COLUMNS['updated_by']}] = ?
                WHERE [{PERMISSION_COLUMNS['permission_code']}] = ?
                """,
                (
                    next_permission_code,
                    permission_name,
                    resource_name,
                    action_name,
                    status,
                    remark or None,
                    actor_user_id or None,
                    permission_code,
                ),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return self.get_permission_by_code(next_permission_code)

    def delete_permission(self, permission_code: str) -> Tuple[bool, str]:
        existing = self.get_permission_by_code(permission_code)
        if not existing:
            return False, "permission not found"

        usage_sql = f"""
        SELECT COUNT(1) AS cnt
        FROM sys_role_permission_rel
        WHERE [{ROLE_PERMISSION_REL_COLUMNS['permission_code']}] = ?
          AND [{ROLE_PERMISSION_REL_COLUMNS['status']}] = 'active'
        """
        usage_rows = self._db.execute_query(usage_sql, (permission_code,))
        if usage_rows and int(usage_rows[0].get("cnt", 0) or 0) > 0:
            return False, "permission is assigned to roles"

        def _tx(conn) -> None:
            self._db.execute_query(
                f"DELETE FROM sys_permission WHERE [{PERMISSION_COLUMNS['permission_code']}] = ?",
                (permission_code,),
                fetch=False,
                conn=conn,
            )

        self._db.execute_with_transaction(_tx)
        return True, ""

    def get_role_permissions(self, role_id: str) -> List[str]:
        if not self.get_role_by_id(role_id):
            return []

        sql = f"""
        SELECT [{ROLE_PERMISSION_REL_COLUMNS['permission_code']}]
        FROM sys_role_permission_rel
        WHERE [{ROLE_PERMISSION_REL_COLUMNS['role_id']}] = ?
          AND [{ROLE_PERMISSION_REL_COLUMNS['status']}] = 'active'
        ORDER BY [{ROLE_PERMISSION_REL_COLUMNS['permission_code']}] ASC
        """
        rows = self._db.execute_query(sql, (role_id,))
        return [row.get(ROLE_PERMISSION_REL_COLUMNS["permission_code"], "") for row in rows if row.get(ROLE_PERMISSION_REL_COLUMNS["permission_code"])]

    def assign_permissions(
        self,
        role_id: str,
        permission_codes: List[str],
        *,
        actor_user_id: str = "",
    ) -> bool:
        if not self.get_role_by_id(role_id):
            raise ValueError("role not found")

        normalized_codes = []
        for permission_code in permission_codes or []:
            normalized = self._trim_text(permission_code, "permission_code", required=True)
            if normalized not in normalized_codes:
                normalized_codes.append(normalized)

        if normalized_codes:
            placeholders = ",".join(["?"] * len(normalized_codes))
            count_rows = self._db.execute_query(
                f"SELECT COUNT(1) AS cnt FROM sys_permission WHERE [{PERMISSION_COLUMNS['permission_code']}] IN ({placeholders})",
                tuple(normalized_codes),
            )
            if int(count_rows[0].get("cnt", 0) or 0) != len(normalized_codes):
                raise ValueError("one or more permissions do not exist")

        def _tx(conn) -> None:
            self._db.execute_query(
                f"DELETE FROM sys_role_permission_rel WHERE [{ROLE_PERMISSION_REL_COLUMNS['role_id']}] = ?",
                (role_id,),
                fetch=False,
                conn=conn,
            )
            for permission_code in normalized_codes:
                self._db.execute_query(
                    f"""
                    INSERT INTO sys_role_permission_rel (
                        [{ROLE_PERMISSION_REL_COLUMNS['role_id']}],
                        [{ROLE_PERMISSION_REL_COLUMNS['permission_code']}],
                        [{ROLE_PERMISSION_REL_COLUMNS['status']}],
                        [{ROLE_PERMISSION_REL_COLUMNS['created_at']}],
                        [{ROLE_PERMISSION_REL_COLUMNS['created_by']}]
                    ) VALUES (?, ?, 'active', SYSDATETIME(), ?)
                    """,
                    (role_id, permission_code, actor_user_id or None),
                    fetch=False,
                    conn=conn,
                )

        self._db.execute_with_transaction(_tx)
        return True

    def _load_role_by_code(self, role_code: str) -> Optional[Dict]:
        normalized_role_code = self._trim_text(role_code, "role_code", required=True)
        rows = self._db.execute_query(
            f"""
            SELECT TOP 1
                [{ROLE_COLUMNS['role_id']}],
                [{ROLE_COLUMNS['role_code']}]
            FROM sys_role
            WHERE [{ROLE_COLUMNS['role_code']}] = ?
            """,
            (normalized_role_code,),
        )
        return rows[0] if rows else None
