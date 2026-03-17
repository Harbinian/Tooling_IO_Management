# Bug Fix: keeper_confirm Order Header Status Not Updated

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10150
Goal: Fix keeper_confirm to update order header status from 'submitted' to 'keeper_confirmed'
Dependencies: None
Execution: RUNPROMPT

---

## Context

After the `keeper_confirm` API is called, the order **header** status remains "submitted" instead of being updated to "keeper_confirmed". While the **item-level** data is correctly updated (明细状态=approved, 确认人=胡婷婷, 确认数量=1), the order header fields (单据状态, 保管员ID, 保管员姓名, 保管员确认时间, 已确认数量) are NOT updated.

This completely blocks the transportation workflow:
- `assign-transport` fails with: "current status does not allow transport assignment: submitted"
- `notify-transport` fails with: "current status does not allow transport notification: submitted"

**Evidence from E2E test (order TO-OUT-20260325-001)**:
```
Order header (NOT updated - BUG):
  "单据状态": "submitted"        ← should be "keeper_confirmed"
  "保管员ID": ""                ← should be keeper's user_id
  "保管员姓名": ""               ← should be keeper's name
  "保管员确认时间": null          ← should be timestamp
  "已确认数量": 0               ← should be > 0

Item data (correctly updated):
  "明细状态": "approved"
  "确认人": "胡婷婷"
  "确认数量": "1.00"
  "确认时间": "Wed, 25 Mar 2026 17:58:02 GMT"
```

---

## Required References

1. **Affected file**: `backend/database/repositories/order_repository.py` - `keeper_confirm()` method (lines 407-537)
2. **Service layer caller**: `backend/services/tool_io_runtime.py` - `keeper_confirm_runtime()` function
3. **API route**: `backend/routes/order_routes.py` - `api_tool_io_order_keeper_confirm()` (line 105)
4. **Database schema**: `backend/database/schema/column_names.py` - for Chinese column name constants
5. **API spec**: `docs/API_SPEC.md` - keeper-confirm endpoint contract

---

## Core Task

Fix the `keeper_confirm()` method in `backend/database/repositories/order_repository.py` to correctly update the order header after confirming items.

### Suspected Issues (must investigate before fixing)

1. **Parameter count mismatch in order header UPDATE** (line 510): The UPDATE SQL has 9 parameter placeholders but the execute_query() call passes parameters in a way that may not align correctly with all columns.

2. **Parameter misalignment in item UPDATE** (line 460-470): The item SQL maps parameters to wrong columns:
   - `item.get('location_id')` → `确认人ID` (confirmer ID - but we're passing a location ID here)
   - `item.get('location_text')` → `确认人姓名` (confirmer name - but we're passing a location text here)
   These should map keeper_id/keeper_name to the confirmer fields, and location to location fields.

3. **No validation of UPDATE success**: The order header UPDATE at line 510-519 executes with `fetch=False` but the return value (rows affected) is never checked. If the UPDATE fails or affects 0 rows, the function still returns `success: True`.

---

## Required Work

### Step 1: Inspect Source Code
Read and analyze `backend/database/repositories/order_repository.py` lines 407-537 to understand the full keeper_confirm flow.

### Step 2: Inspect Database Schema
Read `backend/database/schema/column_names.py` to get correct Chinese column name constants. Verify the exact column names used in both the main table (工装出入库单_主表) and detail table (工装出入库单_明细).

### Step 3: Identify Root Cause
Before modifying any code, determine the exact cause of why the order header is not being updated:
- Check if the UPDATE SQL syntax is correct
- Check if the parameter order matches the SQL placeholders
- Check if rows_affected from execute_query is being validated

### Step 4: Fix the Code
Based on root cause analysis, fix ONE OR MORE of:
- Fix the order header UPDATE to correctly set: 单据状态='keeper_confirmed', 保管员ID, 保管员姓名, 保管员确认时间, 已确认数量
- Fix item UPDATE parameter order so keeper_id/keeper_name go to confirmer fields, and location fields go to location fields
- Add proper validation that the header UPDATE affected at least 1 row

### Step 5: Verify Fix
After fixing, the keeper_confirm API should:
1. Return `{"success": true, "status": "keeper_confirmed", ...}`
2. The order header should show 单据状态='keeper_confirmed' when queried via GET /api/tool-io-orders/{order_no}
3. assign-transport and notify-transport should then work (not return "current status does not allow" errors)

---

## Constraints

1. **DO NOT change the API contract** - the keeper-confirm endpoint must still accept the same payload format
2. **Use column name constants** from `backend/database/schema/column_names.py` - do not use hardcoded Chinese column names
3. **Use transactions** where appropriate for data consistency
4. **Preserve item-level updates** - items that were correctly confirmed should remain correctly updated
5. **DO NOT add new dependencies or restructure the codebase**

---

## Completion Criteria

1. After calling `keeper_confirm`, the order header's `单据状态` is updated to `keeper_confirmed`
2. The `保管员ID`, `保管员姓名`, `保管员确认时间`, `已确认数量` fields are correctly set
3. The `assign-transport` API no longer returns "current status does not allow transport assignment"
4. The `notify-transport` API no longer returns "current status does not allow transport notification"
5. The workflow can proceed from "submitted" → "keeper_confirmed" → "transport_notified" → "transport_completed" → "completed"

### Test Sequence to Verify Fix

```bash
# Login as keeper
KEEPER_TOKEN=$(curl -s http://localhost:8151/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"login_name":"hutingting","password":"test123"}' | python -c "import json,sys; print(json.load(sys.stdin)['token'])")

# Call keeper-confirm
curl -X POST "http://localhost:8151/api/tool-io-orders/TO-OUT-20260325-001/keeper-confirm" \
  -H "Authorization: Bearer $KEEPER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"item_id":23,"approved_qty":1}]}'

# Verify response: should have success=true, status="keeper_confirmed"
# Then verify order header shows 单据状态="keeper_confirmed"
```

---

## Notes

- This bug was discovered during Human E2E testing (report: test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260325_175447.md)
- The bug is a **workflow-blocking critical issue** - no orders can complete the transportation phase
- Similar bug 10142 (keeper_confirm_api_returns_success_without_updating_items) was previously fixed, but the root cause appears to be in the parameter handling, not the logic itself
