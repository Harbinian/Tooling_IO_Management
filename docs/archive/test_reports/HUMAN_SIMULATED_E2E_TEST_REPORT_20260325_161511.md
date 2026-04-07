# Human Simulated E2E Test Report - Bug Fix Verification

**Date**: 2026-03-25 16:15:11
**Tester**: Claude Code (Human E2E Tester Skill)
**System**: Tooling IO Management System
**Test Type**: Bug Fix Verification - assign-transport SQL Encoding Corruption
**Backend**: http://localhost:8151
**Frontend**: http://localhost:8150

---

## Executive Summary

### Test Result: ✅ PASS - Bug Fix Verified

The SQL encoding corruption bug in `assign_transport()` function has been **SUCCESSFULLY FIXED**.

### Key Metrics

| Metric | Value |
|--------|-------|
| Bug Fix Status | ✅ VERIFIED |
| assign-transport API | ✅ PASS - HTTP 200, SQL executes correctly |
| SQL Parameter Markers | ✅ 4 markers (was 6 due to corruption) |
| Workflow Progress | ✅ Transport assignee fields updated correctly |

---

## Test Environment

### Backend Status
- **Health Check**: ✅ HTTP 200
- **Port**: 8151
- **SQL Server**: Connected

### Test User

| User | Login Name | Role | Organization | Status |
|------|------------|------|--------------|--------|
| 胡婷婷 | hutingting | KEEPER | ORG_DEPT_001 | Active |

---

## Bug Fix Verification

### Original Bug (from 2026-03-25 15:15 report)

**File**: `backend/services/tool_io_service.py` - `assign_transport()` function

**Error**:
```
('The SQL contains 6 parameter markers, but 4 parameters were supplied', 'HY000')
```

**Root Cause**: SQL UPDATE statement had corrupted Chinese column names with embedded `?` characters:
- `运输AssigneeName?= ?` (extra `?` in column name)
- `出入库单号?= ?` (extra `?` in column name)

### Fix Applied

**File Modified**: `backend/services/tool_io_service.py` lines 433-444

**Fix**: Replaced corrupted SQL with properly encoded version using `ORDER_COLUMNS` constants:

```python
# After fix (correct):
DatabaseManager().execute_query(
    f"""
    UPDATE 工装出入库单_主表
    SET {ORDER_COLUMNS['transport_assignee_id']} = ?,
        {ORDER_COLUMNS['transport_assignee_name']} = ?,
        {ORDER_COLUMNS['transport_type']} = ?,
        {ORDER_COLUMNS['updated_at']} = GETDATE()
    WHERE {ORDER_COLUMNS['order_no']} = ?
    """,
    (transport_assignee_id, transport_assignee_name, transport_type, order_no),
    fetch=False,
)
```

---

## Test Execution

### Step 1: Service Availability Check

```bash
curl http://localhost:8151/api/health → 200 ✅
curl http://localhost:8150 → 200 ✅
```

**Result**: ✅ PASS - Both services running

### Step 2: Login as KEEPER

```bash
curl -X POST http://localhost:8151/api/auth/login \
  -d '{"login_name":"hutingting","password":"test123"}'
```

**Result**: ✅ PASS - Token received

### Step 3: Get Order Details (TO-OUT-20260324-005)

Order was in `keeper_confirmed` status with:
- `运输AssigneeID`: empty (not assigned yet)
- `运输类型`: empty
- `明细状态`: pending_check

### Step 4: Call assign-transport API

```bash
curl -X POST http://localhost:8151/api/tool-io-orders/TO-OUT-20260324-005/assign-transport \
  -H "Authorization: Bearer $KEEPER_TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "transport_assignee_id":"U_D93CFFC1EB164658",
    "transport_assignee_name":"fengliang",
    "transport_type":"internal"
  }'
```

**Request**: ✅ Sent

**Response**:
```json
{
  "success": true,
  "data": {
    "单据状态": "keeper_confirmed",
    "运输AssigneeID": "U_D93CFFC1EB164658",
    "运输AssigneeName": "fengliang",
    "运输类型": "internal"
  }
}
```

**Result**: ✅ PASS - No SQL error, fields updated correctly

### Step 5: Verify Order Update

Retrieved order TO-OUT-20260324-005 to verify persistence:

| Field | Before | After |
|-------|--------|-------|
| 单据状态 | keeper_confirmed | keeper_confirmed |
| 运输AssigneeID | (empty) | U_D93CFFC1EB164658 ✅ |
| 运输AssigneeName | (empty) | fengliang ✅ |
| 运输类型 | (empty) | internal ✅ |

**Result**: ✅ PASS - All transport fields correctly updated

---

## Workflow Test Results

### Test Order: TO-OUT-20260324-005

| Step | Action | Actor | Status | Notes |
|------|--------|-------|--------|-------|
| 1 | Create order | TEAM_LEADER | ✅ PASS | (yesterday) |
| 2 | Submit order | TEAM_LEADER | ✅ PASS | (yesterday) |
| 3 | Keeper confirm | KEEPER | ✅ PASS | (yesterday) |
| 4 | **Assign transport** | **KEEPER** | **✅ PASS - BUG FIXED** | **SQL executes correctly** |
| 5 | Send notification | KEEPER | ⚠️ BLOCKED | Items not approved (pre-existing issue) |
| 6 | Transport start | PRODUCTION_PREP | ⏸️ PENDING | Waiting for step 5 |
| 7 | Transport complete | PRODUCTION_PREP | ⏸️ PENDING | Waiting for step 6 |
| 8 | Final confirm | TEAM_LEADER | ⏸️ PENDING | Waiting for step 7 |

### Note on Step 5 Issue

The `notify-transport` API returned error: "no approved items are available for transport preparation"

This is because the order items have `明细状态: pending_check` rather than an approved status. This is a **separate pre-existing issue** unrelated to the assign-transport SQL fix.

---

## Issues Found

### No Critical Issues (Bug Fix Verified)

| Issue | Severity | Status | Category |
|-------|----------|--------|----------|
| ~~assign-transport SQL encoding corruption~~ | ~~CRITICAL~~ | ✅ **FIXED** | Bug |

---

## Verification Summary

| Category | Result |
|----------|--------|
| assign-transport API | ✅ PASS - SQL executes correctly |
| SQL Parameter Markers | ✅ Correct count (4 vs 6 before) |
| Transport Fields Update | ✅ Persisted correctly |
| Error Response | ✅ None (was: SQL parameter mismatch) |

---

## Conclusion

The SQL encoding corruption bug in `assign_transport()` function has been **successfully fixed and verified**.

**Previous Error**:
```
('The SQL contains 6 parameter markers, but 4 parameters were supplied', 'HY000')
```

**After Fix**:
- assign-transport API returns `{"success": true}`
- Transport assignee fields are correctly updated
- SQL executes without parameter mismatch errors

**No new issues discovered during this verification test.**

---

## Appendix: Test Commands

```bash
# Login as KEEPER
curl -s http://localhost:8151/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"login_name":"hutingting","password":"test123"}'

# Get order details
curl -s "http://localhost:8151/api/tool-io-orders/TO-OUT-20260324-005" \
  -H "Authorization: Bearer $KEEPER_TOKEN"

# Call assign-transport (VERIFIED WORKING)
curl -s -X POST "http://localhost:8151/api/tool-io-orders/TO-OUT-20260324-005/assign-transport" \
  -H "Authorization: Bearer $KEEPER_TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{"transport_assignee_id":"U_D93CFFC1EB164658","transport_assignee_name":"fengliang","transport_type":"internal"}'
```
