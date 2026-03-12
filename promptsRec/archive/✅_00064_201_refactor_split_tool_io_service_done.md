Primary Executor: Claude Code
Task Type: Refactoring
Priority: P1
Stage: 201
Goal: Split tool_io_service.py into focused service modules
Dependencies: 301 (tests must exist before refactoring)
Execution: RUNPROMPT

---

## Context

`tool_io_service.py` currently handles order CRUD, workflow state transitions, notification dispatch, and dashboard statistics. This violates single responsibility principle and makes the file difficult to maintain and test.

## Required References

- `backend/services/tool_io_service.py` — current monolithic service
- `backend/routes/order_routes.py` — all call sites
- `backend/routes/dashboard_routes.py` — dashboard call sites
- `AI_BACKEND_STRUCTURE.md` — current architecture documentation

## Core Task

Split `tool_io_service.py` into 3 focused modules while preserving all existing behavior.

## Required Work

1. Inspect `tool_io_service.py` to catalog all public functions and their callers
2. Create the following new files:
   - `backend/services/order_workflow_service.py` — state transition logic (submit, confirm, reject, cancel, transport operations)
   - `backend/services/order_query_service.py` — CRUD and query operations (create, list, get_detail)
   - `backend/services/dashboard_service.py` — dashboard statistics
3. Update all import references in:
   - `backend/routes/order_routes.py`
   - `backend/routes/dashboard_routes.py`
   - Any other files that import from `tool_io_service`
4. Keep `tool_io_service.py` as a thin re-export facade (optional, for backward compatibility) or remove it entirely
5. Update `AI_BACKEND_STRUCTURE.md`

## Constraints

- ZERO functional changes — all API behavior must remain identical
- Do NOT change function signatures
- Do NOT modify database queries
- Do NOT change route paths or response formats
- Run existing tests after refactoring to verify no regression

## Acceptance Tests

- All existing tests in `tests/` pass without modification
- All API endpoints return identical responses before and after
- No circular imports
- Each new file has a clear, single responsibility

## Completion Criteria

- [ ] `order_workflow_service.py` created with all state transition functions
- [ ] `order_query_service.py` created with CRUD functions
- [ ] `dashboard_service.py` created with stats functions
- [ ] All route files updated to use new imports
- [ ] All existing tests pass
- [ ] `AI_BACKEND_STRUCTURE.md` updated
- [ ] No circular import errors on startup
