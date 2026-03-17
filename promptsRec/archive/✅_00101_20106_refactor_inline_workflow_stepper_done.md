Primary Executor: Claude Code
Task Type: Refactoring
Priority: P1
Stage: 204
Goal: Refactor OrderDetail.vue to use WorkflowStepper.vue component
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, a code duplication issue was discovered. The `frontend/src/pages/tool-io/OrderDetail.vue` has an inline workflow step implementation (lines 386-459) that duplicates the logic in `frontend/src/components/workflow/WorkflowStepper.vue`. This creates maintenance risk and potential inconsistency.

**Duplicated code location**: `frontend/src/pages/tool-io/OrderDetail.vue:386-459`
**Reference component**: `frontend/src/components/workflow/WorkflowStepper.vue`

The inline implementation handles:
- workflowOrder array
- workflowSteps computed property
- stepState function
- stepClass function
- stepDotClass function
- All status handling (draft, submitted, keeper_confirmed, partially_confirmed, etc.)

**Problems with duplication**:
1. If workflow changes, both files must be updated
2. Risk of inconsistency between the two implementations
3. Harder to maintain and test
4. Violates DRY principle

---

## Required References / 必需参考

- `frontend/src/pages/tool-io/OrderDetail.vue` - File with duplicated workflow logic
- `frontend/src/components/workflow/WorkflowStepper.vue` - Reusable component
- Check if WorkflowStepper supports all statuses used in OrderDetail

---

## Core Task / 核心任务

Refactor OrderDetail.vue to use the WorkflowStepper.vue component instead of inline workflow implementation, while preserving all existing behavior and handling special statuses.

---

## Required Work / 必需工作

1. **Inspect WorkflowStepper.vue** to understand:
   - Props it accepts (currentStatus, orderType, showHeader, etc.)
   - Events it emits (previous, next)
   - Whether it supports all statuses in OrderDetail (partially_confirmed, transport_notified, final_confirmation_pending)

2. **Inspect OrderDetail.vue inline workflow** (lines 386-459) to identify:
   - What statuses are handled
   - What additional logic exists
   - Any differences from WorkflowStepper behavior

3. **Compare the two implementations**:
   - Check if WorkflowStepper can handle all cases
   - Identify any gaps that need to be addressed in WorkflowStepper

4. **Option A - Update WorkflowStepper to be more flexible**:
   - If WorkflowStepper needs additional props to handle all cases
   - Add necessary props (e.g., showPartialConfirmation, customStatusMapping)

5. **Option B - Create a compatible wrapper**:
   - If WorkflowStepper cannot be modified, create a local wrapper

6. **Replace inline code with WorkflowStepper component**:
```vue
<WorkflowStepper
  :current-status="order.orderStatus"
  :order-type="order.orderType"
  :show-header="true"
  step-title="流程进度"
/>
```

7. **Remove duplicated code** from OrderDetail.vue

8. **Test thoroughly** - ensure all statuses display correctly

---

## Constraints / 约束条件

- Do NOT change any backend logic
- Preserve exact same visual output
- Preserve all workflow states (draft, submitted, partially_confirmed, etc.)
- Do NOT break existing functionality
- All existing permissions remain unchanged

---

## Completion Criteria / 完成标准

1. **Acceptance Test 1**: OrderDetail.vue uses `<WorkflowStepper>` component
2. **Acceptance Test 2**: All 6 workflow steps display correctly
3. **Acceptance Test 3**: partially_confirmed status shows "部分确认" correctly
4. **Acceptance Test 4**: transport_notified status shows correctly
5. **Acceptance Test 5**: final_confirmation_pending status shows correctly
6. **Acceptance Test 6**: rejected and cancelled states show correctly
7. **Acceptance Test 7**: Step number and current step highlighting work
8. **Acceptance Test 8**: Next role display works (e.g., "下一步: 保管员")
9. **Acceptance Test 9**: Inline workflow code is removed from OrderDetail.vue
10. **Acceptance Test 10**: `npm run build` passes without errors
