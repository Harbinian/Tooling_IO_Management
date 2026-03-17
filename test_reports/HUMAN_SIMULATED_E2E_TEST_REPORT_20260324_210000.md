# Human Simulated E2E Test Report

**Date**: 2026-03-24
**Tester**: Claude Code (Human E2E Tester Skill)
**System**: Tooling IO Management System
**Test Users**: 太东旭 (team_leader), 胡婷婷 (keeper)
**Backend**: http://localhost:8151
**Frontend**: http://localhost:5173

---

## Executive Summary

### Test Result: CRITICAL BUG FOUND

A critical bug was discovered in the keeper confirmation workflow where the API returns success without actually updating item data when incorrect field names are provided.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Test Steps | 12 |
| Passed | 7 |
| Failed | 1 |
| Blocked | 2 |
| Issues Found | 3 |

---

## Test Users

| User | Login Name | Role | Organization | Permissions |
|------|------------|------|--------------|-------------|
| 太东旭 | taidongxu | team_leader | 复材车间 (ORG_DEPT_005) | 10 |
| 胡婷婷 | hutingting | keeper | 物资保障部 (ORG_DEPT_001) | 7 |

---

## Test Data Constraint

All tests used only the designated test tooling data:

| Field | Value |
|-------|-------|
| Serial Number | T000001 |
| Drawing Number | Tooling_IO_TEST |
| Tool Name | 测试用工装 |
| Model | 测试机型 |

---

## PHASE 1: Authentication Flow

### Login Verification

| User | Status | Organization | Permissions |
|------|--------|--------------|-------------|
| 太东旭 (team_leader) | PASS | 复材车间 | 10 |
| 胡婷婷 (keeper) | PASS | 物资保障部 | 7 |

**Finding**: All users successfully authenticated. Role and organization assignments are correct.

---

## PHASE 2: Tool Search

| Test | Result |
|------|--------|
| Search T000001 | PASS |
| Search Tooling_IO_TEST | PASS |

**Finding**: Tool search correctly returns the test tooling T000001.

---

## PHASE 3: Order Discovery

| Test | Result | Details |
|------|--------|---------|
| List orders (team_leader) | PASS | Found order TO-OUT-20260324-005 |
| Cross-org order access (keeper) | PASS | keeper can view order from different org |

**Finding**: Cross-organization access works correctly. Keeper (胡婷婷, ORG_DEPT_001) can view orders from team_leader (太东旭, ORG_DEPT_005).

---

## PHASE 4: Keeper Confirmation - CRITICAL BUG

### Bug Description

When calling the keeper confirmation API with incorrect field names, the API returns `success: true` but does NOT actually update the items.

**API Call Made:**
```json
{
  "items": [
    {
      "item_id": 22,
      "confirmed_quantity": 1,
      "keeper_check_result": "pass",
      ...
    }
  ]
}
```

**Issue**: The backend expects `tool_code` in the WHERE clause, but `item_id` was sent. The API returned success without updating any rows.

**Affected Order**: TO-OUT-20260324-005

**Order State After Buggy Confirmation:**
- Order status: `keeper_confirmed` (updated)
- Item status: empty (NOT updated)
- Item approved_qty: 0 (NOT updated)
- Order confirmed_count: 1 (order-level aggregate updated)

**Root Cause**: `backend/database/repositories/order_repository.py` line 461:
```python
WHERE 出入库单号 = ? AND 序列号 = ?
```
The `序列号` (tool_code) was not provided, so the WHERE clause matched no rows.

### Bug Impact

1. Order appears to be confirmed but items are not actually approved
2. Transport notification fails because it checks for items with `item_status == "approved"`
3. Order workflow is stuck in an inconsistent state

### Error from Transport Notification:
```
"no approved items are available for transport preparation"
```

### Severity: CRITICAL

The keeper confirmation API should validate that items exist before returning success.

---

## PHASE 5: Transport Notification Workflow

| Test | Result | Error |
|------|--------|-------|
| Assign transport | BLOCKED | No approved items (due to bug above) |
| Send transport notification | BLOCKED | No approved items (due to bug above) |

**Finding**: Blocked by the keeper confirmation bug. Cannot proceed with transport workflow.

---

## PHASE 6: Dashboard API

| Endpoint | Result | Data |
|----------|--------|------|
| GET /api/dashboard/metrics | PASS | 1 active order, 0 pending keeper |

**Finding**: Dashboard API works correctly at `/api/dashboard/metrics`.

---

## PHASE 7: Notification Access

| User | Permission | Result |
|------|------------|--------|
| 太东旭 (team_leader) | notification:view | PASS |
| 胡婷婷 (keeper) | NOT PRESENT | FAIL - missing permission |

**Finding**: Keeper role does not have `notification:view` permission. This may be intentional RBAC design, but keepers may need to view notification history.

---

## PHASE 8: Settings/Profile API

| Endpoint | Result |
|----------|--------|
| GET /api/auth/me | PASS |

**Finding**: Profile API works correctly.

---

## RBAC Issues Identified

| Issue | Severity | Status |
|-------|----------|--------|
| Keeper confirmation returns success without updating items | CRITICAL | BUG - needs fix |
| Keeper lacks notification:view permission | LOW | Design decision |

---

## Recommended Fixes

### Critical Fix Required

**File**: `backend/database/repositories/order_repository.py`

The `keeper_confirm` method should verify that at least one item was actually updated:

```python
# After the item update loop, add:
if updated_count == 0:
    return {'success': False, 'error': 'no items were updated - check item identifiers'}
```

Or validate input before processing:
```python
for item in items:
    tool_code = item.get('tool_code')
    if not tool_code:
        return {'success': False, 'error': 'tool_code is required for each item'}
```

### Permission Review

Consider adding `notification:view` permission to keeper role if keepers need to track notification history.

---

## Confusion Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Total confusion moments | 1 | API returned success but action not completed |
| Page residence >30s | N/A | CLI test |
| Repeated failed operations | 1 | Transport notification failed after keeper "success" |
| Abandoned drafts | 0 | N/A |

---

## Summary

| Category | Result |
|----------|--------|
| Authentication | PASS |
| Tool Search | PASS |
| Order Discovery | PASS |
| Cross-Org Access | PASS |
| Keeper Confirmation | **CRITICAL BUG** |
| Transport Workflow | BLOCKED |
| Dashboard API | PASS |
| Notification Access | PARTIAL |
| Profile API | PASS |

**Overall**: System has a critical bug in keeper confirmation that causes inconsistent order state. The API returns success without actually updating item data when incorrect identifiers are provided.

---

## Test Artifacts

- Problematic order: TO-OUT-20260324-005 (in keeper_confirmed status with unconfirmed items)
- Test user passwords were reset to: test123
