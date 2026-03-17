Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P0
Stage: 114
Goal: Fix missing role protection on transport workflow endpoints
Dependencies: None
Execution: RUNPROMPT

---

## Context

Code review identified that transport-related API endpoints (`transport-start`, `transport-complete`, `assign-transport`) lack role-based permission checks. Any authenticated user can currently trigger transport state transitions. This is a permission vulnerability.

The RBAC model defines only 3 roles (admin, team_leader, keeper) but the workflow requires transport operations to be restricted.

## Required References

- `backend/services/rbac_service.py` — current role and permission definitions
- `backend/services/tool_io_service.py` — transport workflow functions
- `backend/routes/order_routes.py` — transport API endpoints
- `AI_RBAC_MODEL.md` — current RBAC documentation
- `AI_WORKFLOW_STATE_MACHINE.md` — workflow state definitions

## Core Task

Add transport-related permissions and enforce them on all transport API endpoints. Either create a new `transport_operator` role or assign transport permissions to an existing role based on business requirements.

## Required Work

1. Inspect `rbac_service.py` to understand current permission registration mechanism
2. Add new permission codes:
   - `order:assign_transport`
   - `order:transport_start`
   - `order:transport_complete`
3. Decide role assignment (options):
   - Option A: Create `transport_operator` role with transport permissions
   - Option B: Assign transport permissions to `keeper` role (if keeper handles transport)
   - Document the decision in code comments
4. Add permission checks in `order_routes.py` for:
   - `POST /api/tool-io-orders/{order_no}/assign-transport`
   - `POST /api/tool-io-orders/{order_no}/transport-start`
   - `POST /api/tool-io-orders/{order_no}/transport-complete`
5. Update `AI_RBAC_MODEL.md` to reflect new permissions

## Constraints

- Do NOT modify the workflow state machine logic
- Do NOT change existing role permissions for admin/team_leader/keeper
- Do NOT break existing API response format
- Follow existing permission check patterns in the codebase

## Acceptance Tests

- Unauthenticated request to transport endpoints returns 401
- Authenticated user WITHOUT transport permission receives 403
- Authenticated user WITH transport permission can execute transport operations
- Admin role can still perform all transport operations
- Existing keeper and team_leader workflows are unaffected

## Completion Criteria

- [ ] Transport permission codes added to RBAC system
- [ ] All 3 transport endpoints enforce permission checks
- [ ] At least one role is assigned transport permissions
- [ ] AI_RBAC_MODEL.md updated
- [ ] No regression in existing order workflow
