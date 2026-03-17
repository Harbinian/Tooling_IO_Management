# Bug Fix: KEEPER Role Missing 5 Documented Permissions

**Priority**: P0
**Stage**: 10146
**Executor**: Claude Code (Simplified Task - Direct Fix)

---

## Context

KEEPER role is missing 5 permissions that are documented in `RBAC_INIT_DATA.md`:
1. `tool:search` - Search for tools
2. `tool:view` - View tool details
3. `tool:location_view` - View tool locations
4. `order:final_confirm` - Final confirm inbound orders
5. `log:view` - View system logs

### Actual KEEPER Permissions (from login)
```
dashboard:view, notification:create, notification:send_feishu,
notification:view, order:keeper_confirm, order:list, order:transport_execute,
order:view, tool:status_update
```

### Missing (but documented)
```
tool:search, tool:view, tool:location_view, order:final_confirm, log:view
```

### Impact
- KEEPER cannot search for tools (breaks tool selection)
- KEEPER cannot view tool details
- KEEPER cannot view tool locations
- KEEPER cannot perform final confirmation on inbound orders
- KEEPER cannot view system logs
- This is a P0 critical issue

---

## Required References

1. `backend/services/rbac_service.py` - Contains `_ensure_incremental_permission_defaults`
2. `docs/RBAC_INIT_DATA.md` - Documents KEEPER permissions (lines 169-201)
3. `docs/RBAC_PERMISSION_MATRIX.md` - Permission matrix

---

## Core Task

Add missing permission assignments for ROLE_KEEPER in `_ensure_incremental_permission_defaults` function.

### Root Cause
The `_ensure_incremental_permission_defaults` function only adds these permissions for KEEPER:
- `order:transport_execute`
- `tool:status_update`
- `notification:send_feishu`
- `notification:create`
- `notification:view`

Missing for KEEPER:
- `tool:search`
- `tool:view`
- `tool:location_view`
- `order:final_confirm`
- `log:view`

### Solution
Add `_ensure_role_permission_rel` calls for the 5 missing permissions.

---

## Required Work

1. Read `backend/services/rbac_service.py`
2. Locate `_ensure_incremental_permission_defaults` function (around line 287)
3. Add the following permission assignments after existing KEEPER calls:

```python
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="tool:search",
)
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="tool:view",
)
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="tool:location_view",
)
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="order:final_confirm",
)
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="log:view",
)
```

4. Also add `tool:location_view` for ROLE_PRODUCTION_PREP (also missing per RBAC_INIT_DATA.md line 233-251)
5. Run syntax check: `python -m py_compile backend/services/rbac_service.py`
6. Verify the fix by checking login response for KEEPER user

---

## Constraints

- Do NOT change any existing permission assignments
- Only add NEW missing permissions
- Follow the existing code pattern exactly
- Ensure proper function call syntax

---

## Completion Criteria

1. All 5 missing KEEPER permissions are added
2. `tool:location_view` is added for PRODUCTION_PREP
3. Syntax check passes: `python -m py_compile backend/services/rbac_service.py`
4. After restart, KEEPER login shows all documented permissions
