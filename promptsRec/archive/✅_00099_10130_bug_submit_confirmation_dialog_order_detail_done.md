# 131_bug_submit_confirmation_dialog_order_detail.md

Primary Executor: Gemini
Task Type: Bug Fix
Priority: P1
Stage: 131
Goal: Add confirmation dialog to submit action in OrderDetail.vue for UX consistency
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, a critical UX inconsistency was discovered in the OrderDetail.vue component:

**问题描述 / Problem Description**:
- `OrderList.vue` has a confirmation dialog before submitting orders (line 509-520)
- `OrderDetail.vue` does NOT have a confirmation dialog for the same submit action (line 493-496)
- This creates inconsistent user experience where the same operation behaves differently depending on the page

**业务影响 / Business Impact**:
- Users expect consistent behavior across the application
- Submit is a critical state transition that should require explicit user confirmation
- Without confirmation, users may accidentally submit orders

---

## Required References / 必需参考

1. **OrderList.vue:509-520** - Reference implementation with confirmation dialog:
```javascript
async function submitCurrentOrder(order) {
  await ElMessageBox.confirm(
    `确认提交单据 ${order.orderNo} 吗？提交后将进入保管员审核流程。`,
    '提交单据',
    { confirmButtonText: '提交', cancelButtonText: '取消', type: 'warning' }
  )
  const result = await submitOrder(order.orderNo, buildOperator())
  if (result.success) loadOrders()
}
```

2. **OrderDetail.vue:493-496** - Current broken implementation:
```javascript
async function submitCurrentOrder() {
  const result = await submitOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}
```

3. **Session API for operator payload** - Use `operatorPayload()` to build the operator object (same as used in other actions like `cancelCurrentOrder`, `finalConfirmCurrentOrder`)

4. **WorkflowStepper component**: `frontend/src/components/workflow/WorkflowStepper.vue` - Available for workflow preview if needed

---

## Core Task / 核心任务

Fix the `submitCurrentOrder` function in `OrderDetail.vue` to add a confirmation dialog before executing the submit action, matching the behavior in `OrderList.vue`.

**关键变更 / Key Changes**:
1. Add `ElMessageBox.confirm()` before calling `submitOrder()`
2. Use the same confirmation message format as OrderList.vue
3. Use `operatorPayload()` to build the operator (consistent with other actions in the file)
4. On success, call `loadOrder()` to refresh the order detail (already done)

---

## Required Work / 必需工作

1. **Read OrderDetail.vue** to locate the `submitCurrentOrder` function (around line 493-496)
2. **Read OrderList.vue** to see the confirmation dialog pattern (around line 509-520)
3. **Modify OrderDetail.vue**:
   - Import `ElMessageBox` if not already imported
   - Add confirmation dialog with message: `确认提交单据 ${props.orderNo} 吗？提交后将进入保管员审核流程。`
   - Title: `提交单据`
   - Options: `{ confirmButtonText: '提交', cancelButtonText: '取消', type: 'warning' }`
4. **Verify** the fix matches OrderList.vue behavior

---

## Constraints / 约束条件

1. **DO NOT** change any backend API calls or logic
2. **DO NOT** modify other actions (cancel, finalConfirm, delete) - they already have confirmations
3. **DO NOT** add any new dependencies
4. **MUST** use existing `ElMessageBox` import from Element Plus
5. **MUST** preserve existing error handling and success flow
6. **MUST** use the same message format as OrderList.vue for consistency

---

## Completion Criteria / 完成标准

1. ✅ `OrderDetail.vue` `submitCurrentOrder` function now shows a confirmation dialog before submission
2. ✅ Confirmation message matches: `确认提交单据 ${orderNo} 吗？提交后将进入保管员审核流程。`
3. ✅ Dialog has `提交` (confirm) and `取消` (cancel) buttons
4. ✅ Dialog type is `warning` (yellow/warning style)
5. ✅ On cancel, no submission occurs
6. ✅ On confirm, submission proceeds with `submitOrder()` call
7. ✅ On success, `loadOrder()` is called to refresh the view
8. ✅ Behavior matches `OrderList.vue` implementation
9. ✅ No other actions are modified
10. ✅ Frontend builds successfully: `cd frontend && npm run build`
