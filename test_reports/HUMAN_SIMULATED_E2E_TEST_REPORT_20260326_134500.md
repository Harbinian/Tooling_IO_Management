# Human Simulated E2E Test Report - Round 2

## Test Metadata

| Field | Value |
|-------|-------|
| Date | 2026-03-26 |
| Tester | Claude Code (Human E2E Tester Skill) |
| Backend | http://localhost:8151 |
| Frontend | http://localhost:8150 |
| Round | 2 (Post-Self-Healing Fixes) |

---

## Executive Summary

| Status | CRITICAL ISSUES FOUND |
|--------|----------------------|

**Overall Result**: PARTIAL PASS with 1 NEW CRITICAL BUG discovered

### Key Metrics
- Total test steps: 15
- Passed: 12
- Failed: 1 (notify-transport)
- Blocked: 2 (transport workflow incomplete)
- New issues found: 1

---

## Previous Fixes Verification

### BUG 10155 - ORDER_COLUMNS Missing Transport Keys
**Status**: PARTIALLY FIXED

| Test | Result | Notes |
|------|--------|-------|
| assign-transport API | ✅ PASS | transport_operator_id/name correctly set |
| notify-transport API | ❌ FAIL | Column 'transport_notify_text' does not exist |

**Finding**: The assign-transport API now works because the column alias mappings were added. However, notify-transport still fails because it tries to update columns `transport_notify_text` and `wechat_copy_text` that don't exist in the database.

### BUG 10156 - KEEPER Missing order:cancel Permission
**Status**: ✅ FULLY FIXED

| Test | Result | Notes |
|------|--------|-------|
| KEEPER login includes order:cancel | ✅ PASS | Permission visible in token |
| cancel API | ✅ PASS | Successfully canceled order |
| reject API | ✅ PASS | Successfully rejected order |

### BUG 10157 - reject_order Missing operator_role Parameter
**Status**: ✅ FULLY FIXED

| Test | Result | Notes |
|------|--------|-------|
| reject API | ✅ PASS | Successfully rejected order with reason |
| Order status updated | ✅ PASS | Status changed to 'rejected' |

---

## New Critical Bug Found

### CRITICAL: notify-transport Uses Non-Existent DB Columns

**Severity**: HIGH (blocks transport workflow)

**Description**:
The `notify_transport` function in `tool_io_service.py` generates SQL that updates `transport_notify_text` and `wechat_copy_text` columns, but these columns do NOT exist in the `tool_io_order` table.

**Error**:
```
('42S22', "[Microsoft][ODBC SQL Server Driver][SQL Server]列名 'transport_notify_text' 无效。 (207)")
```

**Impact**:
- Transport workflow is BLOCKED at the notification step
- Orders cannot progress from `keeper_confirmed` → `transport_notified`
- Subsequent steps (transport-start, transport-complete, final-confirm) cannot be reached

**Affected API**: `POST /api/tool-io-orders/<order_no>/notify-transport`

**Root Cause**:
The `column_names.py` has `transport_notify_text` and `wechat_copy_text` keys in ORDER_COLUMNS, but the actual database schema doesn't have these columns. The notify-transport SQL UPDATE references these non-existent columns.

**Recommended Fix**:
1. Option A: Add `transport_notify_text` and `wechat_copy_text` columns to `tool_io_order` table
2. Option B: Remove the UPDATE for these columns in notify-transport SQL (if they're not actually needed)

---

## RBAC Permission Test Results

### TEAM_LEADER (taidongxu)

| Permission | Expected | Actual | Status |
|------------|----------|--------|--------|
| order:create | ✅ ALLOW | ✅ ALLOW | PASS |
| order:submit | ✅ ALLOW | ✅ ALLOW | PASS |
| order:list | ✅ ALLOW | ✅ ALLOW | PASS |
| order:view | ✅ ALLOW | ✅ ALLOW | PASS |
| order:final_confirm | ✅ ALLOW | ✅ ALLOW | PASS |
| order:cancel | ✅ ALLOW | N/A | SKIP |
| notification:create | ✅ ALLOW | ✅ ALLOW | PASS |
| notification:view | ✅ ALLOW | ✅ ALLOW | PASS |

### KEEPER (hutingting)

| Permission | Expected | Actual | Status |
|------------|----------|--------|--------|
| order:cancel | ✅ ALLOW | ✅ ALLOW | PASS |
| order:reject | ✅ ALLOW | ✅ ALLOW | PASS |
| order:keeper_confirm | ✅ ALLOW | ✅ ALLOW | PASS |
| order:transport_execute | ✅ ALLOW | N/A | SKIP |
| notification:send_feishu | ✅ ALLOW | ❌ FAIL | notify-transport broken |
| tool:status_update | ✅ ALLOW | N/A | SKIP |

### PRODUCTION_PREP (fengliang)

| Permission | Expected | Actual | Status |
|------------|----------|--------|--------|
| order:transport_execute | ✅ ALLOW | ❌ FAIL | Data scope issue |

**Finding**: fengliang is in ORG_DEPT_001 while the test order was in ORG_DEPT_005. Test users are NOT in the same organization as required.

### SYS_ADMIN (admin)

| Permission | Expected | Actual | Status |
|------------|----------|--------|--------|
| * ALL | ✅ ALLOW | ✅ ALLOW | PASS |

---

## Workflow Test Results

### Outbound Workflow (Partial)

| Step | Action | User | Expected | Actual | Status |
|------|--------|------|----------|--------|--------|
| 1 | Create order | taidongxu | ✅ | ✅ | PASS |
| 2 | Submit order | taidongxu | ✅ | ✅ | PASS |
| 3 | Keeper confirm | hutingting | ✅ | ✅ | PASS |
| 4 | Assign transport | hutingting | ✅ | ✅ | PASS |
| 5 | Send notification | hutingting | ✅ | ❌ | FAIL |
| 6 | Start transport | fengliang | ✅ | N/A | BLOCKED |
| 7 | Complete transport | fengliang | ✅ | N/A | BLOCKED |
| 8 | Final confirm | taidongxu | ✅ | N/A | BLOCKED |

### Rejection Workflow

| Step | Action | User | Expected | Actual | Status |
|------|--------|------|----------|--------|--------|
| 1 | Create order | taidongxu | ✅ | ✅ | PASS |
| 2 | Submit order | taidongxu | ✅ | ✅ | PASS |
| 3 | Keeper reject | hutingting | ✅ | ✅ | PASS |
| 4 | View rejection reason | taidongxu | ✅ | ✅ | PASS |

---

## Issues Found

| Severity | Issue | Location | Status |
|----------|-------|----------|--------|
| CRITICAL | notify-transport uses non-existent DB columns | tool_io_service.py | NEW |
| HIGH | Test users not in same organization | Test data | PRE-EXISTING |

---

## Confusion Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Failed API calls | 3 | notify-transport (1), transport-start blocked (2) |
| Workaround attempts | 1 | Skipped notification to try direct transport |

---

## Self-Healing Recommendations

### Issue 1: notify-transport Non-Existent Columns
- **Priority**: P1 (blocks critical workflow)
- **Type**: Bug Fix
- **Suggested Prompt**: Create bug prompt for notify-transport SQL using columns that don't exist
- **Executor**: Codex (backend)

---

## Test Data Issues

### User Organization Mismatch

| User | Login | Expected Org | Actual Org |
|------|-------|--------------|------------|
| taidongxu | taidongxu | 同一组织 | ORG_DEPT_005 |
| hutingting | hutingting | 同一组织 | ORG_DEPT_005 |
| fengliang | fengliang | 同一组织 | ORG_DEPT_001 |

**Impact**: Cannot test transport workflow end-to-end because fengliang cannot access orders in ORG_DEPT_005.

---

## Conclusion

The 3 bugs fixed in Round 1 (BUG 10155 partial, 10156, 10157) are confirmed working for their core functionality:
- assign-transport: ✅ Working
- KEEPER cancel/reject: ✅ Working
- reject API: ✅ Working

However, a NEW critical issue was discovered: the notify-transport API fails because it references database columns that don't exist. This blocks the transport workflow.

**Next Action**: Run self-healing-dev-loop to fix the notify-transport issue.
