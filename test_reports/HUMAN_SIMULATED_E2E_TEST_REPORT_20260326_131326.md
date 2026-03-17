# Human E2E Test Report
**Date**: 2026-03-26 13:13:26
**Tester**: Claude Code (Human E2E Tester Skill)
**System**: Tooling IO Management System
**Frontend**: http://localhost:8150
**Backend**: http://localhost:8151

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Result** | :x: **CRITICAL ISSUES FOUND** |
| **Total Test Steps** | 18 |
| **Passed** | 8 |
| **Failed** | 2 |
| **Blocked** | 8 |
| **Issues Found** | 4 (3 Critical, 1 High) |

---

## Test Users

| User | Login Name | Role | Organization | Permissions Count |
|------|------------|------|-------------|-------------------|
| :heavy_check_mark: 太东旭 | taidongxu | TEAM_LEADER | 复材车间 (ORG_DEPT_005) | 10 |
| :heavy_check_mark: 胡婷婷 | hutingting | KEEPER | 物资保障部 (ORG_DEPT_001) | 14 |
| :heavy_check_mark: 冯亮 | fengliang | PRODUCTION_PREP | 物资保障部 (ORG_DEPT_001) | 4 |
| :heavy_check_mark: CA | admin | SYS_ADMIN | 昌兴航空复材 (ORG_ROOT) | 20 |

---

## RBAC Permission Test Results

### RBAC Test: TEAM_LEADER (taidongxu)

| API Endpoint | Method | Permission | Expected | Actual | Status |
|--------------|--------|------------|----------|--------|--------|
| /api/auth/login | POST | - | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders | POST | order:create | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders | GET | order:list | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders/<id>/submit | POST | order:submit | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders/<id>/reject | POST | order:cancel | :white_check_mark: ALLOW | :x: 500 Error | :x: **BLOCKED** |
| /api/tool-io-orders/<id>/final-confirm | POST | order:final_confirm | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/dashboard | GET | dashboard:view | :white_check_mark: ALLOW | :x: 404 Not Found | :warning: UNKNOWN |
| /api/tools/search | GET | tool:search | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |

### RBAC Test: KEEPER (hutingting)

| API Endpoint | Method | Permission | Expected | Actual | Status |
|--------------|--------|------------|----------|--------|--------|
| /api/auth/login | POST | - | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders | POST | order:create | :x: FORBIDDEN | :x: FORBIDDEN (403) | :white_check_mark: PASS |
| /api/tool-io-orders | GET | order:list | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders/<id>/keeper-confirm | POST | order:keeper_confirm | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders/<id>/assign-transport | POST | order:keeper_confirm | :white_check_mark: ALLOW | :x: KeyError | :x: **BLOCKED** |
| /api/tool-io-orders/<id>/notify-transport | POST | notification:send_feishu | :white_check_mark: ALLOW | :x: KeyError | :x: **BLOCKED** |
| /api/tool-io-orders/<id>/cancel | POST | order:cancel | :white_check_mark: ALLOW | :x: PERMISSION_DENIED | :x: **BUG** |
| /api/tools/search | GET | tool:search | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/logs | GET | log:view | :white_check_mark: ALLOW | :x: 404 Not Found | :warning: UNKNOWN |

### RBAC Test: PRODUCTION_PREP (fengliang)

| API Endpoint | Method | Permission | Expected | Actual | Status |
|--------------|--------|------------|----------|--------|--------|
| /api/auth/login | POST | - | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders/pre-transport | GET | order:transport_execute | :white_check_mark: ALLOW | :white_check_mark: ALLOW (empty) | :white_check_mark: PASS |
| /api/tools/search | GET | tool:search | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |

### RBAC Test: SYS_ADMIN (admin)

| API Endpoint | Method | Permission | Expected | Actual | Status |
|--------------|--------|------------|----------|--------|--------|
| /api/auth/login | POST | - | :white_check_mark: ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| /api/tool-io-orders/<id>/reject | POST | order:cancel | :white_check_mark: ALLOW | :x: Missing param | :x: **BUG** |

---

## Workflow Test Results

### Phase 3: Full Outbound Workflow

**Status**: :x: **BLOCKED** at transport assignment step

#### Workflow Steps:

| Step | Actor | Action | Expected | Actual | Status |
|------|-------|--------|----------|--------|--------|
| 1 | taidongxu | Create outbound order | order:create ALLOW | :white_check_mark: ALLOW | :white_check_mark: PASS |
| 2 | taidongxu | Submit order | order:submit ALLOW | :white_check_mark: ALLOW (status: submitted) | :white_check_mark: PASS |
| 3 | hutingting | Keeper confirm | order:keeper_confirm ALLOW | :white_check_mark: ALLOW (status: keeper_confirmed) | :white_check_mark: PASS |
| 4 | hutingting | Assign transport | order:keeper_confirm ALLOW | :x: KeyError 'transport_assignee_id' | :x: **BLOCKED** |
| 5 | hutingting | Notify transport | notification:send_feishu ALLOW | :x: KeyError 'transport_notify_text' | :x: **BLOCKED** |
| 6 | fengliang | Transport start | order:transport_execute ALLOW | :x: BLOCKED (order not in correct status) | :x: **BLOCKED** |
| 7 | fengliang | Transport complete | order:transport_execute ALLOW | :x: BLOCKED | :x: **BLOCKED** |
| 8 | taidongxu | Final confirm | order:final_confirm ALLOW | :x: BLOCKED | :x: **BLOCKED** |

---

## Issues Found

### :red_circle: CRITICAL-1: Missing Column Constants for Transport Assignment

**Severity**: CRITICAL
**Component**: `backend/database/schema/column_names.py`
**File(s) Affected**:
- `backend/services/tool_io_service.py` (assign_transport function)
- `backend/services/tool_io_service.py` (notify_transport function)

**Description**:
`ORDER_COLUMNS` dictionary is missing the following keys:
- `transport_assignee_id`
- `transport_assignee_name`
- `transport_type`

This causes a `KeyError` when the `assign_transport` and `notify_transport` functions try to build SQL queries using f-strings with `ORDER_COLUMNS[...]`.

**Root Cause**:
The column name constants for transport-related fields were never added to `ORDER_COLUMNS` in `column_names.py`, even though the database schema has these columns.

**Impact**:
- Keeper cannot assign transport operators to orders
- Keeper cannot send transport notifications
- The entire transport workflow is blocked after keeper confirmation
- Orders get stuck in `keeper_confirmed` status

**Evidence**:
```python
# In tool_io_service.py:436-438
SET {ORDER_COLUMNS['transport_assignee_id']} = ?,
    {ORDER_COLUMNS['transport_assignee_name']} = ?,
    {ORDER_COLUMNS['transport_type']} = ?,
```
When `ORDER_COLUMNS` doesn't contain these keys, Python raises `KeyError: 'transport_assignee_id'` during f-string formatting.

**Recommended Fix**:
Add the missing constants to `ORDER_COLUMNS` in `backend/database/schema/column_names.py`:
```python
ORDER_COLUMNS = {
    # ... existing columns ...
    'transport_assignee_id': '运输AssigneeID',  # ADD
    'transport_assignee_name': '运输AssigneeName',  # ADD
    'transport_type': '运输类型',  # ADD
}
```

---

### :red_circle: CRITICAL-2: Missing `order:cancel` Permission for KEEPER Role

**Severity**: CRITICAL
**Component**: RBAC Permission System
**File(s) Affected**: Database role permissions

**Description**:
KEEPER role token does not include `order:cancel` permission, even though the RBAC Permission Matrix (`docs/RBAC_PERMISSION_MATRIX.md`) explicitly shows KEEPER should have this permission.

**Expected (from RBAC matrix)**:
| Permission | SYS_ADMIN | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|------------|-----------|-------------|--------|---------|-----------------|---------|
| `order:cancel` | :white_check_mark: | :white_check_mark: | :white_check_mark: | :x: | :x: | :x: |

**Actual**:
KEEPER token permissions do not include `order:cancel`.

**Impact**:
- KEEPER cannot reject or cancel orders
- This violates the documented RBAC specification
- Keepers cannot perform their documented role of rejecting invalid orders

**Evidence**:
```bash
# Login as KEEPER and try to cancel
curl -X POST -H "Authorization: Bearer $KEEPER_TOKEN" \
  "http://localhost:8151/api/tool-io-orders/TO-OUT-20260326-009/cancel" \
  -d '{"operator_role":"keeper","cancel_reason":"test"}'
# Response: {"error":{"code":"PERMISSION_DENIED","details":{"required_permission":"order:cancel"},"message":"missing required permission: order:cancel"},"success":false}
```

**Recommended Fix**:
Add `order:cancel` permission to KEEPER role in the database. This may require running an RBAC initialization script or directly updating the role_permissions table.

---

### :red_circle: CRITICAL-3: `reject_order` Function Missing `operator_role` Parameter

**Severity**: CRITICAL
**Component**: `backend/services/tool_io_service.py`
**File(s) Affected**: `backend/services/tool_io_service.py:573-581`

**Description**:
The `reject_order` function in `tool_io_service.py` does not pass the `operator_role` parameter to the underlying `reject_tool_io_order` database function, which expects it as a required positional argument.

**Evidence**:
```python
# In tool_io_service.py:576-581
result = reject_tool_io_order(
    order_no,
    payload.get("operator_id", ""),
    payload.get("operator_name", ""),
    payload.get("reject_reason", ""),
)  # Missing: payload.get("operator_role", "")
```

But `database.py:reject_tool_io_order` signature:
```python
def reject_tool_io_order(order_no: str, reject_reason: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
```

**Impact**:
- The reject endpoint is completely broken for all roles
- Error message: `TypeError: reject_order() missing 1 required positional argument: 'operator_role'`

**Recommended Fix**:
Add the missing parameter in `tool_io_service.py`:
```python
result = reject_tool_io_order(
    order_no,
    payload.get("reject_reason", ""),  # Note: reject_reason comes BEFORE operator fields in DB function
    payload.get("operator_id", ""),
    payload.get("operator_name", ""),
    payload.get("operator_role", ""),
)
```

---

### :orange_circle: HIGH-1: Dashboard API Returns 404 for All Users

**Severity**: HIGH
**Component**: Backend API Routes
**File(s) Affected**: Likely `web_server.py` or dashboard route registration

**Description**:
The `/api/dashboard/stats` endpoint returns 404 Not Found regardless of user authentication status. This affects all roles including those that should have `dashboard:view` permission.

**Impact**:
- Dashboard page may be non-functional
- Cannot verify dashboard permission enforcement

**Evidence**:
```bash
curl -H "Authorization: Bearer $TEAM_LEADER_TOKEN" "http://localhost:8151/api/dashboard/stats"
# Response: 404 Not Found
```

**Recommended Fix**:
Check if the dashboard blueprint is properly registered in `web_server.py`. The route may be missing or registered under a different URL prefix.

---

## Confusion Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Page residence time | N/A | UI testing not performed |
| Repeated failed operations | 3 | assign-transport, notify-transport, reject |
| Abandoned workflows | 1 | Outbound workflow blocked at step 4 |
| Navigation loops | 0 | Not measured during API testing |

---

## Self-Healing Recommendations

The following issues should trigger the **self-healing-dev-loop** skill:

1. **CRITICAL-1** (Missing Column Constants): This is a code-level bug that can be fixed by adding the missing constants to `column_names.py`. Use dev-inspector to identify all places using these missing keys, then auto-task-generator to create fix tasks.

2. **CRITICAL-2** (Missing Permission): This may require database initialization script fix. Use auto-task-generator to create a prompt for adding the missing permission.

3. **CRITICAL-3** (Missing Parameter): Simple code fix - add one missing parameter to a function call. Use dev-inspector to verify the fix.

---

## Test Summary

**Workflow Completion Rate**: 37.5% (3 out of 8 steps completed)

**Blockers**:
1. assign-transport fails due to missing column constants (CRITICAL-1)
2. notify-transport fails due to missing column constants (CRITICAL-1)
3. reject/cancel fails due to missing permission (CRITICAL-2)
4. reject API also fails due to missing operator_role parameter (CRITICAL-3)

**Positive Findings**:
- Authentication system works correctly
- Order creation works correctly
- Order submission works correctly
- Keeper confirmation works correctly
- Tool search works correctly
- RBAC permission enforcement mostly works (except the identified bugs)

---

*Report generated by Human E2E Tester skill at 2026-03-26 13:13:26*
