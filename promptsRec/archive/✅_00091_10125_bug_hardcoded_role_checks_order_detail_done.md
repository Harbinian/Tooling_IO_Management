Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 125
Goal: Fix hardcoded role checks in OrderDetail.vue to use permission-based checks
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, a critical RBAC issue was discovered in `frontend/src/pages/tool-io/OrderDetail.vue`. The page uses hardcoded role checks (`session.role === 'initiator'`) instead of proper permission-based checks. This means users with correct permissions may not see the action buttons they need.

**Location of issue**: `frontend/src/pages/tool-io/OrderDetail.vue:462, 463-464`

```javascript
const canSubmit = computed(() => session.role === 'initiator' && order.value.orderStatus === 'draft')
const canCancel = computed(
  () => session.role === 'initiator' && ['draft', 'rejected'].includes(order.value.orderStatus)
)
```

The `session.role` is mapped from legacy role codes via `mapLegacyRole()` in `session.js:23-35` and becomes `'initiator'` for team_leader, planner, and sys_admin roles. However, checking `session.role === 'initiator'` is fragile because:
1. It depends on internal role mapping logic
2. It doesn't check actual permissions
3. If role mapping changes, permissions break silently

---

## Required References / 必需参考

- `frontend/src/pages/tool-io/OrderDetail.vue` - File with hardcoded role checks
- `frontend/src/store/session.js` - Session store with `hasPermission()` method
- `frontend/src/pages/tool-io/OrderList.vue` - Reference for correct permission-based checks
- `docs/RBAC_DESIGN.md` - RBAC permission design

---

## Core Task / 核心任务

Replace hardcoded role checks in OrderDetail.vue with proper permission-based checks using `session.hasPermission()`.

---

## Required Work / 必需工作

1. **Inspect OrderDetail.vue** to find all hardcoded role checks:
   - Line ~462: `canSubmit` - should check `order:submit` permission
   - Line ~463-464: `canCancel` - should check `order:cancel` permission

2. **Compare with OrderList.vue** to see correct pattern:
   - OrderList.vue uses `session.hasPermission('order:submit')` correctly

3. **Replace hardcoded checks** with permission-based checks:
   - `canSubmit`: `session.hasPermission('order:submit') && order.value.orderStatus === 'draft'`
   - `canCancel`: `session.hasPermission('order:cancel') && ['draft', 'rejected'].includes(order.value.orderStatus)`

4. **Verify no other pages have similar issues** - check OrderCreate.vue if it exists

5. **Test the changes** by verifying:
   - Submit button appears for users with `order:submit` permission
   - Cancel button appears for users with `order:cancel` permission

---

## Constraints / 约束条件

- Do NOT change `session.role` or `mapLegacyRole()` logic - only fix OrderDetail.vue
- Preserve the same status conditions (draft, rejected, etc.)
- Do NOT change any backend code
- Do NOT modify WorkflowStepper.vue or other components

---

## Completion Criteria / 完成标准

1. **Acceptance Test 1**: OrderDetail.vue uses `session.hasPermission('order:submit')` instead of `session.role === 'initiator'`
2. **Acceptance Test 2**: OrderDetail.vue uses `session.hasPermission('order:cancel')` instead of `session.role === 'initiator'`
3. **Acceptance Test 3**: canDelete uses correct permission check (if applicable)
4. **Acceptance Test 4**: No hardcoded `session.role === 'initiator'` remains in OrderDetail.vue
5. **Acceptance Test 5**: The changes compile without errors (`npm run build` passes)

---

## Execution Summary

### Files Modified
- `frontend/src/pages/tool-io/OrderDetail.vue` - Replaced hardcoded role checks with permission-based checks

### Changes Made

**Before (Lines 462, 464):**
```javascript
const canSubmit = computed(() => session.role === 'initiator' && order.value.orderStatus === 'draft')
const canCancel = computed(
  () => session.role === 'initiator' && ['draft', 'rejected'].includes(order.value.orderStatus)
)
```

**After:**
```javascript
const canSubmit = computed(() => session.hasPermission('order:submit') && order.value.orderStatus === 'draft')
const canCancel = computed(
  () => session.hasPermission('order:cancel') && ['draft', 'rejected'].includes(order.value.orderStatus)
)
```

### Verification Results
| Criteria | Status |
|----------|--------|
| `canSubmit` uses `session.hasPermission('order:submit')` | ✅ Verified |
| `canCancel` uses `session.hasPermission('order:cancel')` | ✅ Verified |
| No `session.role === 'initiator'` remains in OrderDetail.vue | ✅ Verified |
| `npm run build` passes | ✅ Verified |

### Additional Checks
- OrderCreate.vue was checked for similar issues: **None found**
- Build completed successfully with no errors

---

## Run Report

Run report saved to: `logs/prompt_task_runs/run_20260319_000000_125_bug_hardcoded_role_checks_order_detail.md`
