# Bug Fix: E2E Order Creation and RBAC Test Expectations

## Metadata
- **Prompt Number**: 10182
- **Task Type**: Bug Fix
- **Priority**: P1
- **Stage**: 1
- **Goal**: Fix remaining E2E test failures - serial_no SQL error and RBAC test expectations
- **Dependencies**: None
- **Execution**: RUNPROMPT

## Context

The previous bug fix (10181) partially resolved E2E test issues:
- ✅ Login password hardcoding was fixed (test123 → test1234)
- ❌ Order creation still fails with `serial_no` SQL error
- ❌ RBAC test expectations don't match actual API behavior

### Current Error (serial_no)

```
'error': '(\'42S22\', "[42S22] [Microsoft][ODBC SQL Server Driver][SQL Server]���� \'serial_no\' ��Ч�� (207)"
```

**Analysis from task 10181:**
- Error occurs during order creation in `load_tool_master_map` or `check_tools_available`
- Test tool `T000001` may not exist in `Tooling_ID_Main` table
- When tool doesn't exist, fallback logic kicks in but query might still fail

### RBAC Test Expectation Mismatch

| Test | Expected | Actual | Issue |
|------|----------|--------|-------|
| #8 TEAM_LEADER->order:create | 201 ALLOW | 400 DENY | Due to serial_no error |
| #9 TEAM_LEADER->order:submit | 404 DENY | 404 ALLOW | 404 means resource not found, not permission |

## Root Cause Investigation Required

### For serial_no Error:
1. Check if `T000001` exists in `Tooling_ID_Main` table
2. If not, either:
   - Use a real tool code that exists in the database, OR
   - Fix the test to properly mock/skip tool validation
3. If yes, investigate why the SQL query fails

### For RBAC Expectations:
1. For non-existent orders, 404 is correct (not a permission issue)
2. Tests need to be adjusted to:
   - Use existing orders for permission checks, OR
   - Accept 404 as valid "DENY" for non-existent resources

## Required Work

### 1. Investigate serial_no Error
- Run a query to check if `T000001` exists in `Tooling_ID_Main`
- If it doesn't exist, find a real tool code from the database to use in tests
- If queries fail, identify the exact SQL that causes the error

### 2. Fix RBAC Test Expectations
- Review RBAC test cases in `api_e2e.py`
- Adjust expectations to match actual API behavior:
  - 404 for non-existent resources is correct (not a permission error)
  - Permission tests should use existing orders

### 3. Update TEST_TOOL Data
- If using a real tool from database, update `TEST_TOOL` in both:
  - `test_runner/api_e2e.py`
  - `test_runner/playwright_e2e.py`

### 4. Verify Fixes
- Run `python test_runner/api_e2e.py` and verify:
  - smoke_03 (order creation) passes
  - RBAC tests pass with correct expectations

## Constraints

- Do NOT modify production database data
- Test tool data must be valid and exist in `Tooling_ID_Main`
- RBAC tests must reflect actual API behavior, not desired behavior
- Follow 8D problem-solving protocol: root cause must be identified before fixing

## Completion Criteria

1. `smoke_03` (order creation) passes with HTTP 201
2. RBAC tests correctly distinguish between:
   - Permission denied (403)
   - Resource not found (404)
   - Successful operations (200/201)
3. All 3 test phases (smoke, workflow, RBAC) execute without SQL errors
4. Score improves from current ~8/24 passing to 16+/24 passing

## References

- `test_runner/api_e2e.py` - Main E2E test file
- `backend/services/tool_io_service.py` - Order creation service
- `backend/database/repositories/order_repository.py` - Order repository with tool validation
- `backend/database/repositories/tool_repository.py` - Tool repository with `load_tool_master_map`
- `promptsRec/archive/🔶_00191_10181_10181_fix_e2e_login_and_rbac_test_failures_done.md` - Previous partial fix
- `logs/prompt_task_runs/run_20260401_211500_10181_fix_e2e_login_and_rbac_test_failures.md` - Previous execution report
