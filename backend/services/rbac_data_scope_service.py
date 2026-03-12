# -*- coding: utf-8 -*-
"""
RBAC data-scope helpers for organization-aware order access.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Set, Tuple

from database import DatabaseManager

from backend.services.org_service import get_descendant_org_ids

SUPPORTED_SCOPE_TYPES = {"ALL", "ORG", "ORG_AND_CHILDREN", "SELF", "ASSIGNED"}

ORDER_INITIATOR_COLUMN = "\u53d1\u8d77\u4ebaID"
ORDER_KEEPER_COLUMN = "\u4fdd\u7ba1\u5458ID"
ORDER_TRANSPORT_ASSIGNEE_COLUMN = "\u8fd0\u8f93\u4ebaID"
ORDER_ORG_COLUMN = "org_id"


def _unique_non_empty(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    result: List[str] = []
    for value in values:
        normalized = str(value or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def load_role_data_scopes(role_ids: Sequence[str]) -> List[Dict]:
    """Load active role data-scope rows."""
    normalized_role_ids = _unique_non_empty(role_ids)
    if not normalized_role_ids:
        return []

    placeholders = ",".join(["?"] * len(normalized_role_ids))
    sql = f"""
    SELECT role_id, scope_type, scope_value
    FROM sys_role_data_scope_rel
    WHERE role_id IN ({placeholders})
      AND status = 'active'
    ORDER BY role_id ASC, scope_type ASC
    """
    return DatabaseManager().execute_query(sql, tuple(normalized_role_ids))


def load_user_ids_for_org_ids(org_ids: Sequence[str]) -> List[str]:
    """Resolve all users associated with one or more organizations."""
    normalized_org_ids = _unique_non_empty(org_ids)
    if not normalized_org_ids:
        return []

    placeholders = ",".join(["?"] * len(normalized_org_ids))
    sql = f"""
    SELECT DISTINCT user_id
    FROM (
        SELECT user_id
        FROM sys_user
        WHERE default_org_id IN ({placeholders})

        UNION

        SELECT user_id
        FROM sys_user_role_rel
        WHERE org_id IN ({placeholders})
          AND status = 'active'
    ) scoped_users
    ORDER BY user_id ASC
    """
    params = tuple(normalized_org_ids + normalized_org_ids)
    rows = DatabaseManager().execute_query(sql, params)
    return [row.get("user_id", "") for row in rows if row.get("user_id")]


def _resolve_assignment_org_id(user: Dict, role: Dict) -> str:
    role_org_id = str(role.get("org_id", "")).strip()
    if role_org_id:
        return role_org_id

    current_org_id = str((user.get("current_org") or {}).get("org_id", "")).strip()
    if current_org_id:
        return current_org_id

    return str((user.get("default_org") or {}).get("org_id", "") or user.get("default_org_id", "")).strip()


def resolve_order_data_scope(user: Dict) -> Dict:
    """Resolve merged order-access scope for the current user."""
    roles = [role for role in user.get("roles", []) if role.get("role_id")]
    scope_rows = load_role_data_scopes([role.get("role_id", "") for role in roles])

    scope_rows_by_role: Dict[str, List[Dict]] = {}
    for row in scope_rows:
        role_id = str(row.get("role_id", "")).strip()
        if not role_id:
            continue
        scope_rows_by_role.setdefault(role_id, []).append(row)

    merged_scope_types: List[str] = []
    direct_org_ids: List[str] = []
    descendant_org_ids: List[str] = []
    assignment_scopes: List[Dict] = []
    for role in roles:
        role_id = str(role.get("role_id", "")).strip()
        role_scope_types = _unique_non_empty(
            str(row.get("scope_type", "")).upper() for row in scope_rows_by_role.get(role_id, [])
        )
        merged_scope_types.extend(role_scope_types)

        assignment_org_id = _resolve_assignment_org_id(user, role)
        if "ORG" in role_scope_types and assignment_org_id:
            direct_org_ids.append(assignment_org_id)
        if "ORG_AND_CHILDREN" in role_scope_types and assignment_org_id:
            descendant_org_ids.extend(get_descendant_org_ids(assignment_org_id))

        assignment_scopes.append(
            {
                "role_id": role_id,
                "role_code": role.get("role_code", ""),
                "org_id": assignment_org_id,
                "scope_types": role_scope_types,
            }
        )

    scope_types = _unique_non_empty(merged_scope_types)
    org_ids = _unique_non_empty([*direct_org_ids, *descendant_org_ids])
    user_id = str(user.get("user_id", "")).strip()
    if not scope_types and user_id:
        scope_types = ["SELF", "ASSIGNED"]

    return {
        "scope_types": scope_types,
        "all_access": "ALL" in scope_types,
        "org_ids": org_ids,
        "org_user_ids": load_user_ids_for_org_ids(org_ids) if org_ids else [],
        "self_user_ids": [user_id] if "SELF" in scope_types and user_id else [],
        "assigned_user_ids": [user_id] if "ASSIGNED" in scope_types and user_id else [],
        "current_user_id": user_id,
        "assignment_scopes": assignment_scopes,
    }


def build_order_scope_sql(scope_context: Dict) -> Tuple[str, Tuple[str, ...]]:
    """Return SQL fragment and params for order-list filtering."""
    if scope_context.get("all_access"):
        return "", ()

    conditions: List[str] = []
    params: List[str] = []

    self_user_ids = _unique_non_empty(scope_context.get("self_user_ids", []))
    if self_user_ids:
        placeholders = ",".join(["?"] * len(self_user_ids))
        conditions.append(f"{ORDER_INITIATOR_COLUMN} IN ({placeholders})")
        params.extend(self_user_ids)

    assigned_user_ids = _unique_non_empty(scope_context.get("assigned_user_ids", []))
    if assigned_user_ids:
        placeholders = ",".join(["?"] * len(assigned_user_ids))
        conditions.append(
            f"({ORDER_KEEPER_COLUMN} IN ({placeholders}) OR {ORDER_TRANSPORT_ASSIGNEE_COLUMN} IN ({placeholders}))"
        )
        params.extend(assigned_user_ids)
        params.extend(assigned_user_ids)

    org_ids = _unique_non_empty(scope_context.get("org_ids", []))
    if org_ids:
        placeholders = ",".join(["?"] * len(org_ids))
        conditions.append(f"{ORDER_ORG_COLUMN} IN ({placeholders})")
        params.extend(org_ids)

    if not conditions:
        return " AND 1 = 0", ()

    return f" AND ({' OR '.join(conditions)})", tuple(params)


def order_matches_scope(order: Dict, scope_context: Dict) -> bool:
    """Return whether one order record is inside the resolved scope."""
    if scope_context.get("all_access"):
        return True

    initiator_id = str(order.get("initiator_id") or order.get(ORDER_INITIATOR_COLUMN) or "").strip()
    keeper_id = str(order.get("keeper_id") or order.get(ORDER_KEEPER_COLUMN) or "").strip()
    transport_user_id = str(order.get("transport_assignee_id") or order.get(ORDER_TRANSPORT_ASSIGNEE_COLUMN) or "").strip()
    order_org_id = str(order.get("org_id") or order.get(ORDER_ORG_COLUMN) or "").strip()

    self_user_ids = set(scope_context.get("self_user_ids", []))
    if self_user_ids and initiator_id in self_user_ids:
        return True

    assigned_user_ids = set(scope_context.get("assigned_user_ids", []))
    if assigned_user_ids and (keeper_id in assigned_user_ids or transport_user_id in assigned_user_ids):
        return True

    org_ids = set(scope_context.get("org_ids", []))
    if org_ids and order_org_id in org_ids:
        return True

    return False
