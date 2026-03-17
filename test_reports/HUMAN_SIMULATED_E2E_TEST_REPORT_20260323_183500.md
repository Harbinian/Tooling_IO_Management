# Human Simulated E2E Test Report

**Date**: 2026-03-23
**Tester**: Claude Code (Human E2E Tester Skill)
**System**: Tooling IO Management System
**Frontend**: Vue 3 + Element Plus + Vite
**Backend**: Flask REST API + SQL Server

---

## Executive Summary

### RBAC Permission Fix Verified

The previously reported issue with team_leader's `notification:view` permission has been **fixed**.

**Root Cause**: The `sys_role_permission_rel` table was missing entries for `ROLE_TEAM_LEADER` for the following permissions:
- `notification:view`
- `tool:view`
- `order:final_confirm`

**Fix Applied**: Manually inserted the missing permission relations into `sys_role_permission_rel` table.

**Verification**: Team leader (taidongxu) now has all required permissions.

---

## Test Data Constraint

All testing used the following test tooling data as required:

| Field | Value |
|-------|-------|
| Serial Number (序列号) | T000001 |
| Tooling Drawing Number (工装图号) | Tooling_IO_TEST |
| Tool Name (工装名称) | 测试用工装 |
| Model (机型) | 测试机型 |

---

## Simulated User Accounts

| Role | Login Name | Password | User ID | Organization |
|------|------------|----------|---------|--------------|
| Team Leader (班组长) | taidongxu | 123456 | U_8546A79BA76D4FD2 | ORG_DEPT_005 (复材车间) |
| Keeper (保管员) | hutingting | 123456 | U_7954837C515844BA | ORG_DEPT_001 (树脂事业部) |

---

## Phase 1: RBAC Permission Verification

### Step 1: Team Leader Login and Permission Check

**API Endpoint**: `POST /api/auth/login`

**Result**: SUCCESS

**User Info**:
- User ID: U_8546A79BA76D4FD2
- Login Name: taidongxu
- Role: team_leader
- Organization: ORG_DEPT_005 (复材车间)

**Permissions Verified**:
```
[OK] dashboard:view
[OK] notification:view  <-- PREVIOUSLY MISSING, NOW FIXED
[OK] order:create
[OK] order:final_confirm  <-- PREVIOUSLY MISSING, NOW FIXED
[OK] order:list
[OK] order:submit
[OK] order:view
[OK] tool:search
[OK] tool:view  <-- PREVIOUSLY MISSING, NOW FIXED
```

**Assessment**: PASS - All documented permissions now correctly assigned

---

## Phase 2: Workflow Test

### Step 2: Tool Search

**API Endpoint**: `GET /api/tools/search?keyword=T000001`

**Result**: SUCCESS

**Tool Found**:
- Tool ID: T000001
- Drawing No: Tooling_IO_TEST
- Name: 测试用工装

**Assessment**: PASS

### Step 3: Create Order

**API Endpoint**: `POST /api/tool-io-orders`

**Result**: SUCCESS

**Order Created**: TO-OUT-20260323-002

**Assessment**: PASS

### Step 4: Submit Order

**API Endpoint**: `POST /api/tool-io-orders/{order_no}/submit`

**Result**: SUCCESS

**Order Status**: submitted

**Assessment**: PASS

### Step 5: Keeper Confirmation

**Issue Identified**: Keeper (hutingting) from ORG_DEPT_001 cannot confirm orders created by team_leader (taidongxu) from ORG_DEPT_005 due to **RBAC Data Isolation**.

**Error Response**:
```json
{
  "error": "order not found",
  "success": false
}
```

**Root Cause Analysis**:
- The `get_order_detail` function calls `_is_order_accessible(order, current_user)` which filters orders based on organization scope
- Keeper from ORG_DEPT_001 cannot access orders from ORG_DEPT_005
- This is **expected RBAC behavior** for cross-organization data isolation

**Workaround for E2E Testing**:
- Full E2E workflow testing requires users from the **same organization**
- ORG_DEPT_005 has team_leader (taidongxu) but no keeper
- ORG_DEPT_001 has keeper (hutingting, fengliang) but no team_leader

**Assessment**: BLOCKED - RBAC data isolation prevents cross-org workflow completion

---

## Phase 3: Notification Records Access

### Step 6: Verify notification:view Permission

**API Endpoint**: `GET /api/tool-io-orders/{order_no}/notification-records`

**Previous Issue**: 403 FORBIDDEN - team_leader lacked `notification:view` permission

**After Fix Result**: 200 OK - Permission granted

**Assessment**: PASS - The original issue is RESOLVED

---

## RBAC Issues Identified

| Issue | Severity | Status |
|-------|----------|--------|
| team_leader missing `notification:view` permission | Critical | FIXED |
| team_leader missing `tool:view` permission | High | FIXED |
| team_leader missing `order:final_confirm` permission | High | FIXED |
| Cross-organization workflow isolation | Medium | BY DESIGN |

---

## Workflow Completeness Check

| Step | Status | Notes |
|------|--------|-------|
| Create Order | PASS | |
| Submit Order | PASS | |
| Keeper Confirmation | BLOCKED | Different organizations |
| Transport Notification | N/A | Skipped (keeper confirm failed) |
| Final Confirmation | N/A | Skipped (keeper confirm failed) |
| Order Closed | N/A | Skipped |

---

## Settings Page Findings

Not tested in this session (frontend not accessible from CLI testing).

---

## Confusion Metrics

- Total confusion moments detected: 0
- Cross-org RBAC isolation is expected behavior, not a confusion issue

---

## Workflow Guidance Assessment

Unable to complete full workflow assessment due to RBAC data isolation.

---

## Recommended Fixes

### 1. Add Keeper to ORG_DEPT_005 (High Priority)

For proper E2E testing and production use, ORG_DEPT_005 needs its own keeper role assignment.

**SQL**:
```sql
-- Assign keeper role to a user in ORG_DEPT_005
INSERT INTO sys_user_role_rel (user_id, role_id, org_id, is_primary, status)
SELECT u.user_id, r.role_id, 'ORG_DEPT_005', 1, 'active'
FROM sys_user u
CROSS JOIN sys_role r
WHERE u.login_name = '<existing_user>'
AND r.role_code = 'keeper'
AND NOT EXISTS (
    SELECT 1 FROM sys_user_role_rel
    WHERE user_id = u.user_id AND role_id = r.role_id
);
```

### 2. Add Production Preparation Worker Role (User Request)

User requested adding a "生产准备工" (Production Preparation Worker) role under "物资保障部" (Material Support Department).

**Required Actions**:
1. Create new role `ROLE_PRODUCTION_PREP`
2. Assign permissions for transport operations
3. Add users to this role
4. Update RBAC documentation

---

## Summary

| Category | Result |
|----------|--------|
| RBAC Permission Fix | SUCCESS |
| notification:view Access | VERIFIED |
| Order Creation | SUCCESS |
| Order Submission | SUCCESS |
| Cross-Org Workflow | BLOCKED (by design) |
| E2E Full Workflow | INCOMPLETE |

**Overall Assessment**: The RBAC permission issue that caused the 403 error has been fixed. Full E2E workflow testing requires users from the same organization due to data isolation.
