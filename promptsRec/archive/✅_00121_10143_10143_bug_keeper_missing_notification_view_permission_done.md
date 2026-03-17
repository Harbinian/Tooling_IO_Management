# 10143: Bug Fix - KEEPER Missing notification:view Permission

## Metadata

| Field | Value |
|-------|-------|
| **Prompt Number** | 10143 |
| **Type** | Bug Fix (10xxx) |
| **Executor** | Codex |
| **Stage** | Execution |
| **Test Report** | HUMAN_SIMULATED_E2E_TEST_REPORT_20260325_000000.md |

---

## Context

### Bug Description

KEEPER role cannot access `/api/notifications` because they lack `notification:view` permission in the database.

### Root Cause

The `_ensure_incremental_permission_defaults` function in `backend/services/rbac_service.py` adds `notification:create` and `notification:send_feishu` to KEEPER role, but does NOT add `notification:view`.

---

## Implementation Summary

### Files Modified

| File | Lines | Change |
|------|-------|--------|
| `backend/services/rbac_service.py` | 361-367 | Added `notification:view` for KEEPER |
| `docs/RBAC_PERMISSION_MATRIX.md` | 63-64 | Updated TEAM_LEADER permissions |

### Code Changes

**backend/services/rbac_service.py (incremental defaults):**
```python
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="notification:create",
)
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="notification:view",  # ADDED
)
_ensure_role_permission_rel(
    db,
    role_id="ROLE_SYS_ADMIN",
    permission_code="tool:status_update",
)
```

**docs/RBAC_PERMISSION_MATRIX.md:**
```
| `notification:view` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `notification:create` | ✅ | ✅ | ✅ | ❌ | ❌ |
```

---

## Verification

- Syntax check: `python -m py_compile backend/services/rbac_service.py` - **PASSED**

---

## Note

The fix adds the permission to the incremental defaults. Existing databases will get the new permission on next service restart when `_ensure_incremental_permission_defaults` is called.
