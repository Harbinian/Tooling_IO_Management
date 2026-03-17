# Prompt: Fix reject_order Function Missing operator_role Parameter

**Primary Executor**: Claude Code
**Task Type**: Bug Fix (P1 Critical)
**Priority**: P1
**Stage**: 10157
**Goal**: Fix TypeError in reject_order by adding missing operator_role parameter
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context

During E2E testing, the reject order API was found to be completely non-functional for all roles. The `reject_order` function in `tool_io_service.py` calls `reject_tool_io_order` but omits the required `operator_role` parameter, causing a TypeError.

**Error observed**:
```
TypeError: reject_order() missing 1 required positional argument: 'operator_role'
```

**Affected operation**: `POST /api/tool-io-orders/<order_no>/reject`

**Impact**: No role (including SYS_ADMIN) can reject orders - this completely blocks the order rejection workflow.

---

## Required References

- `backend/services/tool_io_service.py` - The file with the bug (lines 573-581)
- `database.py` - The database function signature for `reject_tool_io_order`
- `backend/services/tool_io_service.py` - Where `reject_order` is defined
- `backend/routes/order_routes.py` - The API route that calls `reject_order`

---

## Core Task

Fix the missing `operator_role` parameter in the `reject_order` function call to `reject_tool_io_order`.

---

## Required Work

1. **Read the current code** at `backend/services/tool_io_service.py:573-581`:

   ```python
   result = reject_tool_io_order(
       order_no,
       payload.get("operator_id", ""),
       payload.get("operator_name", ""),
       payload.get("reject_reason", ""),
   )  # Missing: operator_role
   ```

2. **Check the database function signature** in `database.py` to confirm the expected parameter order:

   ```python
   def reject_tool_io_order(order_no: str, reject_reason: str, operator_id: str, operator_name: str, operator_role: str) -> dict:
   ```

   Note: `reject_reason` comes BEFORE the operator fields in the database function!

3. **Fix the function call** by adding `payload.get("operator_role", "")` as the 5th argument

4. **Verify the fix** by testing the reject API

---

## Constraints

- Only modify `backend/services/tool_io_service.py`
- Do NOT change the database function signature
- Ensure parameter order matches what the database function expects
- The `operator_role` comes from `build_actor_payload()` which should populate it from the authenticated user

---

## Completion Criteria

1. The `reject_order` function in `tool_io_service.py` passes `operator_role` to `reject_tool_io_order`
2. The parameter order matches the database function signature
3. `POST /api/tool-io-orders/<order_no>/reject` no longer raises TypeError
4. Orders can be successfully rejected with rejection reason persisted

---

## Bug Investigation Required

Before making any changes, you MUST:

1. Read `backend/services/tool_io_service.py:573-591` to see the full `reject_order` function
2. Read `database.py` to confirm the exact signature of `reject_tool_io_order` and parameter order
3. Check how `build_actor_payload` populates the `operator_role` field
4. Verify the fix by comparing parameter order between service call and database function
