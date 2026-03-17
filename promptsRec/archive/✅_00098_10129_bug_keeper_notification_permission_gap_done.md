Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 126
Goal: Fix keeper notification permission gap in KeeperProcess.vue
Dependencies: None
Execution: RUNPROMPT

---

## Context

During E2E testing, a permission issue was discovered in `frontend/src/pages/tool-io/KeeperProcess.vue`.
The `canNotify` computed property checked only `notification:send_feishu`, but this permission could be missing
for keeper role in some upgraded environments, which blocked transport notification sending after keeper confirmation.

---

## Required References

- `frontend/src/pages/tool-io/KeeperProcess.vue`
- `frontend/src/store/session.js`
- `backend/services/tool_io_service.py`
- `backend/services/rbac_service.py`
- `docs/RBAC_DESIGN.md`

---

## Core Task

Investigate and fix keeper notification permission gap so keeper can send transport notifications after confirmation,
while preserving permission checks and workflow status constraints.

---

## Execution Summary

### Files Modified
- `backend/services/rbac_service.py` - Added keeper Feishu send permission in bootstrap and incremental defaults.
- `frontend/src/pages/tool-io/KeeperProcess.vue` - Updated `canNotify` compatibility check with keeper permission.
- `tests/test_rbac_service.py` - Added regression test for keeper Feishu permission incremental default.
- `docs/RBAC_DESIGN.md` - Synced keeper permission list to include Feishu send permission.

### Fix Details
- Backend bootstrap role-permission seed now includes:
  - `('ROLE_KEEPER', 'notification:send_feishu')`
- Backend incremental defaults now guarantee upgraded envs also receive:
  - `ROLE_KEEPER -> notification:send_feishu`
- Frontend `canNotify` now evaluates with compatibility fallback:
  - `notification:send_feishu OR order:keeper_confirm`
  - existing status gate remains unchanged (`keeper_confirmed`, `partially_confirmed`, `transport_notified`).

### Verification Results
- `python -m pytest tests/test_rbac_service.py -q` -> `6 passed`
- `python -m py_compile backend/services/rbac_service.py` -> passed
- `npm run build` -> passed

### Acceptance Mapping
1. Keeper role has appropriate permission to send transport notifications: fixed in RBAC bootstrap and incremental defaults.
2. `canNotify` evaluates true for keeper flow after confirmation with preserved status gate.
3. Transport notification send path remains backend-protected and available to keeper after permission backfill.
4. Non-keeper roles without required permissions remain restricted by frontend + backend checks.

---

## Run Report

Run report saved to: `logs/prompt_task_runs/run_20260319_141045_126_bug_keeper_notification_permission_gap.md`
