# Prompt: Fix KEEPER Role Missing order:cancel Permission

**Primary Executor**: Claude Code
**Task Type**: Bug Fix (P1 Critical)
**Priority**: P1
**Stage**: 10156
**Goal**: Add missing `order:cancel` permission to KEEPER role so Keepers can reject/cancel orders
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context

During E2E testing, the KEEPER role was unable to reject or cancel orders despite the RBAC Permission Matrix (`docs/RBAC_PERMISSION_MATRIX.md`) explicitly showing that KEEPER should have the `order:cancel` permission.

**Error observed**:
```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "details": {"required_permission": "order:cancel"},
    "message": "missing required permission: order:cancel"
  },
  "success": false
}
```

**Affected operation**: `POST /api/tool-io-orders/<order_no>/cancel` and `POST /api/tool-io-orders/<order_no>/reject`

**Impact**: KEEPER cannot reject invalid or problematic orders - this violates the documented RBAC specification and blocks the keeper workflow.

---

## Required References

- `docs/RBAC_PERMISSION_MATRIX.md` - Shows KEEPER should have `order:cancel`
- `docs/RBAC_INIT_DATA.md` - Contains permission catalog and role definitions
- `docs/RBAC_DESIGN.md` - RBAC design documentation
- Database role_permissions table structure
- `backend/services/tool_io_service.py` - Where permission is checked

---

## Core Task

The `order:cancel` permission exists in the permission catalog (as shown in `RBAC_INIT_DATA.md`), and the RBAC matrix shows KEEPER should have it, but the permission was never assigned to the KEEPER role in the database. Fix this by adding the missing permission assignment.

---

## Required Work

1. **Verify the permission exists** in the permission catalog:
   - Check `docs/RBAC_INIT_DATA.md` for `order:cancel` permission definition

2. **Identify the KEEPER role**:
   - Check `RBAC_INIT_DATA.md` for role_code for KEEPER (likely `ROLE_KEEPER` or `keeper`)

3. **Find the role_permissions table**:
   - Determine which database table stores role-permission assignments
   - Check `backend/database/` for RBAC-related code that manages permissions

4. **Add the missing permission**:
   - Insert the appropriate record linking KEEPER role to `order:cancel` permission
   - Or run the RBAC initialization script if that's how permissions are managed

5. **Verify the fix**:
   - Login as KEEPER user and verify token now includes `order:cancel` permission
   - Test that cancel/reject API no longer returns PERMISSION_DENIED

---

## Constraints

- Do NOT modify the RBAC Permission Matrix documentation
- Do NOT change any code files
- Only modify database role_permissions data
- The permission catalog itself is correct - only the role-permission assignment is missing

---

## Completion Criteria

1. KEEPER role has `order:cancel` permission assigned in the database
2. Login as KEEPER user returns a token that includes `order:cancel` in the permissions list
3. `POST /api/tool-io-orders/<order_no>/cancel` no longer returns PERMISSION_DENIED for KEEPER users
4. `POST /api/tool-io-orders/<order_no>/reject` no longer returns PERMISSION_DENIED for KEEPER users

---

## Bug Investigation Required

Before making any changes, you MUST:

1. Read `docs/RBAC_INIT_DATA.md` to confirm `order:cancel` permission definition and KEEPER role code
2. Find where role-permission assignments are stored (likely in database, check backend/database/ for RBAC code)
3. Check how permissions are loaded and cached at login time
4. Identify the exact INSERT statement or update needed
