# Bug Fix: transport-start SQL Parameter Count Mismatch

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10151
Goal: Fix transport-start API SQL parameter count mismatch
Dependencies: None
Execution: RUNPROMPT

---

## Context

The `transport-start` API fails with a SQL parameter count mismatch error when called.

**Error**:
```
"The SQL contains 7 parameter markers, but 3 parameters were supplied"
```

**Test evidence (order TO-OUT-20260325-001)**:
```bash
curl -X POST "http://localhost:8151/api/tool-io-orders/TO-OUT-20260325-001/transport-start" \
  -H "Authorization: Bearer $PROD_PREP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Returns:
{
  "error": "('HY000', '[Microsoft][ODBC SQL Server Driver][SQL Server]The SQL contains 7 parameter markers, but 3 parameters were supplied')",
  "success": false
}
```

---

## Required References

1. **Affected file**: `backend/services/order_workflow_service.py` - `transport_start()` function
2. **API route**: Check `backend/routes/` for transport-start endpoint
3. **Database schema**: `backend/database/schema/column_names.py`
4. **Related**: `backend/database/repositories/order_repository.py` - any transport-related methods

---

## Core Task

### Step 1: Find the Transport-Start Implementation

Search for `transport_start` in the codebase to find:
- The API route handler
- The service layer function
- The database query being executed

### Step 2: Identify the SQL Parameter Mismatch

Find the SQL statement that has 7 parameter placeholders (`?`) but is being called with fewer parameters.

### Step 3: Fix the Parameter Count

Ensure the number of `?` placeholders matches the number of parameters passed in the tuple.

---

## Constraints

1. **DO NOT change the API contract** - the transport-start endpoint must still accept the same payload format
2. **Use column name constants** from `backend/database/schema/column_names.py` where applicable
3. **Preserve existing functionality** - only fix the parameter mismatch

---

## Completion Criteria

1. `transport-start` API returns `{"success": true}` when called
2. The order status transitions from `transport_notified` to `transport_in_progress`
3. No SQL parameter count errors occur

---

## Test Sequence

```bash
# Login as KEEPER first to set up the order
KEEPER_TOKEN=$(curl -s http://localhost:8151/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"login_name":"hutingting","password":"test123"}' | python -c "import json,sys; print(json.load(sys.stdin)['token'])")

# Get current order status
curl -s -X GET "http://localhost:8151/api/tool-io-orders/TO-OUT-20260325-001" \
  -H "Authorization: Bearer $KEEPER_TOKEN" | python -c "import json,sys; print(json.load(sys.stdin)['data']['单据状态'])"

# Login as PRODUCTION_PREP
PROD_PREP_TOKEN=$(curl -s http://localhost:8151/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"login_name":"fengliang","password":"test123"}' | python -c "import json,sys; print(json.load(sys.stdin)['token'])")

# Call transport-start
curl -X POST "http://localhost:8151/api/tool-io-orders/TO-OUT-20260325-001/transport-start" \
  -H "Authorization: Bearer $PROD_PREP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Notes

- This bug was found during the keeper_confirm bug fix verification
- The order TO-OUT-20260325-001 should be in `transport_notified` status after the keeper_confirm fix
