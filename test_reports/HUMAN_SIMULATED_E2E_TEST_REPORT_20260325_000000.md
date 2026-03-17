# Human Simulated E2E Test Report

**Date**: 2026-03-25
**Tester**: Claude Code (Human E2E Tester Skill)
**System**: Tooling IO Management System
**Test Type**: RBAC Permission Matrix Verification
**Backend**: http://localhost:8151

---

## Executive Summary

### Test Result: ISSUES FOUND

RBAC permission verification revealed inconsistencies between documented permissions and actual database permissions.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Permissions Tested | 6 |
| Mismatches Found | 2 |
| Critical Issues | 1 |

---

## RBAC Permission Test Results

### Test Users

| User | Login Name | Role | Actual Permissions |
|------|------------|------|-------------------|
| 太东旭 | taidongxu | team_leader | dashboard:view, notification:create, notification:view, order:create, order:final_confirm, order:list, order:submit, order:view, tool:search, tool:view |
| 胡婷婷 | hutingting | keeper | dashboard:view, notification:create, notification:send_feishu, order:keeper_confirm, order:list, order:transport_execute, order:view, tool:status_update |

### Permission Test Matrix

| API Endpoint | Method | Permission Required | TEAM_LEADER (Doc/Actual) | KEEPER (Doc/Actual) |
|--------------|--------|-------------------|--------------------------|---------------------|
| /tool-io-orders | GET | order:list | 200 / 200 ✅ | 200 / 200 ✅ |
| /tool-io-orders | POST | order:create | 201 / 400 ❌ | 403 / 403 ✅ |
| /tools/search | GET | tool:search | 200 / 200 ✅ | 403 / 403 ✅ |
| /dashboard/metrics | GET | dashboard:view | 200 / 200 ✅ | 200 / 200 ✅ |
| /notifications | GET | notification:view | ❌403 / 200 ❌ | ✅200 / 403 ❌ |
| /tool-io-orders/pending-keeper | GET | order:keeper_confirm | 403 / 403 ✅ | 200 / 200 ✅ |

### Issues Found

#### Issue 1: KEEPER Missing notification:view Permission (CRITICAL)

**Problem**: KEEPER role cannot access `/api/notifications` because they lack `notification:view` permission.

**Actual KEEPER Permissions**:
```
dashboard:view, notification:create, notification:send_feishu,
order:keeper_confirm, order:list, order:transport_execute, order:view,
tool:status_update
```

**Missing**: `notification:view`

**Impact**: KEEPER can create notifications but cannot view them. This breaks the notification workflow.

**Root Cause**: The `_ensure_incremental_permission_defaults` function in `rbac_service.py` adds `notification:create` and `notification:send_feishu` to KEEPER, but does NOT add `notification:view`.

**Location**: `backend/services/rbac_service.py` lines 356-365

**Fix Required**: Add `_ensure_role_permission_rel(db, role_id="ROLE_KEEPER", permission_code="notification:view")` to the incremental defaults.

---

#### Issue 2: RBAC Permission Matrix Out of Sync (MEDIUM)

**Problem**: `docs/RBAC_PERMISSION_MATRIX.md` states TEAM_LEADER should NOT have `notification:view` or `notification:create`, but the actual database shows TEAM_LEADER has both.

**Documented (Wrong)**:
| Permission | TEAM_LEADER |
|------------|-------------|
| notification:view | ❌ |
| notification:create | ❌ |

**Actual (From Login)**:
| Permission | TEAM_LEADER |
|------------|-------------|
| notification:view | ✅ |
| notification:create | ✅ |

**Impact**: Documentation is misleading. If someone relies on the matrix for RBAC design, they will make incorrect decisions.

**Root Cause**: The permission matrix was not updated when TEAM_LEADER permissions were expanded.

---

## Issues Classification

| Issue | Severity | Status |
|-------|----------|--------|
| KEEPER missing notification:view | CRITICAL | Needs Fix |
| RBAC Matrix out of sync | MEDIUM | Documentation Fix |

---

## Recommended Fixes

### Fix 1: Add notification:view to KEEPER

**File**: `backend/services/rbac_service.py`
**Location**: In `_ensure_incremental_permission_defaults` function (around line 365)

**Add**:
```python
_ensure_role_permission_rel(
    db,
    role_id="ROLE_KEEPER",
    permission_code="notification:view",
)
```

### Fix 2: Update RBAC Permission Matrix

**File**: `docs/RBAC_PERMISSION_MATRIX.md`
**Change**: Update TEAM_LEADER row to show:
- `notification:view`: ✅ (change from ❌)
- `notification:create`: ✅ (change from ❌)

---

## Self-Healing Recommendation

This report triggers the self-healing-dev-loop for:
1. Bug Fix: Add `notification:view` to KEEPER in incremental permissions
2. Docs Update: Sync RBAC_PERMISSION_MATRIX.md with actual permissions

---

## Confusion Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Total confusion moments | 1 | API returns 403 but user expected 200 |
| Permission mismatches | 2 | Doc vs Actual discrepancy |

---

## Summary

| Category | Result |
|----------|--------|
| RBAC Permission Test | FAIL |
| KEEPER Notification Workflow | BLOCKED |
| Documentation Accuracy | OUT OF SYNC |
