Primary Executor: Gemini
Task Type: Bug Fix
Priority: P1
Stage: 132
Goal: Fix keeper batch status update payload key from status to new_status
Dependencies: None
Execution: RUNPROMPT

---

## Context

The keeper-side batch tool status update workflow is non-functional. The frontend sends `status` in the request payload, but the backend API `PATCH /api/tools/batch-status` validates `new_status` as a required field. This causes all batch status updates to fail with 400 validation errors.

## Required References

- **Frontend file**: `frontend/src/pages/tool-io/KeeperProcess.vue` line 545
- **Backend file**: `backend/routes/tool_routes.py` lines 71-76
- **Frontend API call**: `frontend/src/api/tool.js` or equivalent batchUpdateToolStatus function
- Backend schema contract: `new_status` is required, must be one of: `in_storage`, `outbounded`, `maintain`, `scrapped`

## Core Task

Fix the payload key mismatch in the keeper batch status update feature.

## Required Work

1. **Inspect the codebase**: Read `frontend/src/pages/tool-io/KeeperProcess.vue` around line 545 to find the `batchUpdateToolStatus` API call
2. **Find the API definition**: Locate the frontend API wrapper for batch status updates (likely in `frontend/src/api/` directory)
3. **Fix the payload**: Change `status` key to `new_status` in the request payload
4. **Verify no other occurrences**: Search for other places where `status` is incorrectly used instead of `new_status` in batch tool status context
5. **Test the fix**: After fixing, verify the change is syntactically correct

## Constraints

- Only change the payload key from `status` to `new_status`
- Do not change backend logic
- Do not modify any other fields in the payload
- Preserve all other parameters: `tool_codes`, `remark`, `operator_id`, `operator_name`, `operator_role`

## Completion Criteria

1. The `batchUpdateToolStatus` call in KeeperProcess.vue sends `new_status` instead of `status`
2. The change is consistent with the backend API contract at `backend/routes/tool_routes.py:71-76`
3. Frontend builds successfully: `cd frontend && npm run build` passes
4. No other instances of the same `status` vs `new_status` bug exist in keeper batch update context
