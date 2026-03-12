Primary Executor: Codex
Task Type: Testing
Priority: P1
Stage: 302
Goal: Create RBAC permission enforcement tests for all API endpoints
Dependencies: 100 (transport permissions must be added first)
Execution: RUNPROMPT

---

## Context

The RBAC system defines permissions but code review could not verify that all endpoints actually enforce them. Missing enforcement means any authenticated user could perform privileged operations.

## Required References

- `backend/services/rbac_service.py` — permission definitions
- `backend/routes/order_routes.py` — order endpoints
- `backend/routes/admin_user_routes.py` — admin endpoints
- `backend/routes/dashboard_routes.py` — dashboard endpoints
- `AI_API_CONTRACT_SUMMARY.md` — all endpoints
- `AI_RBAC_MODEL.md` — role-permission mapping

## Core Task

Write tests that verify every protected API endpoint correctly enforces its required permission.

## Required Work

1. Inspect all route files to identify which endpoints have permission checks
2. Create `tests/test_rbac_enforcement.py`
3. For each protected endpoint, test:
   - Request without token → 401
   - Request with valid token but wrong role → 403
   - Request with correct role → 200 (or appropriate success code)
4. Test specifically:
   - `order:create` — only team_leader and admin
   - `order:keeper_confirm` — only keeper and admin
   - `order:final_confirm` — role depends on order type
   - `admin:user_manage` — only admin
   - Transport endpoints — per new permissions from prompt 100
5. Document any endpoints found WITHOUT permission checks (as failing tests or comments)

## Constraints

- Use pytest framework
- Do NOT modify production code (test-only changes)
- If an endpoint is found unprotected, write the test as a known failure with clear comment

## Acceptance Tests

- All permission-protected endpoints have corresponding tests
- Tests correctly distinguish 401 (no auth) vs 403 (wrong role)
- Any unprotected endpoints are flagged

## Completion Criteria

- [ ] `tests/test_rbac_enforcement.py` created
- [ ] All order workflow endpoints tested for permission enforcement
- [ ] All admin endpoints tested for permission enforcement
- [ ] Transport endpoints tested (depends on prompt 100)
- [ ] Test report clearly shows protection status of each endpoint
- [ ] All tests pass with `pytest -v`
