# Human Simulated E2E Test Report

**Date**: 2026-03-19
**Tester**: Claude Code (Human E2E Tester Skill)
**System**: Tooling IO Management System
**Frontend**: Vue 3 + Element Plus + Vite
**Backend**: Flask REST API + SQL Server

---

## Executive Summary

This report documents code-level exploratory testing of the Tooling IO Management System, focusing on verifying fixes for previously identified issues and performing simulated end-to-end workflow testing with real user accounts.

**Overall Assessment**: Significant progress has been made in fixing critical RBAC and UI issues from the previous report. Most high-priority issues have been resolved, but one critical inconsistency remains: the Submit action lacks a confirmation dialog in OrderDetail.vue while OrderList.vue has one. During E2E simulation, RBAC data isolation prevented complete workflow testing across different organizations.

---

## Test Data Constraint

All testing used the following test tooling data as required:

| Field | Value |
|-------|-------|
| Serial Number (序列号) | T000001 |
| Tooling Drawing Number (工装图号) | Tooling_IO_TEST |
| Tool Name (工装名称) | 测试用工装 |
| Model (机型) | 测试机型 |

---

## Simulated User Accounts

| Role | Login Name | Password | User ID | Organization |
|------|------------|----------|---------|--------------|
| Team Leader (班组长) | taidongxu | 123456 | U_8546A79BA76D4FD2 | ORG_DEPT_005 (复材车间) |
| Keeper (保管员) | hutingting | 123456 | U_7954837C515844BA | ORG_DEPT_001 (树脂事业部) |

---

## Phase 1: E2E Workflow Simulation

### Step 1: Team Leader Login (taidongxu)

**API Endpoint**: `POST /api/auth/login`

**Request**:
```json
{
  "login_name": "taidongxu",
  "password": "123456"
}
```

**Response**:
```json
{
  "success": true,
  "token": "eyJ1c2VyX2lkIjoiVV84NTQ2QTc5QkE3NkQ0RkQyIn0.abuWVQ...",
  "user": {
    "user_id": "U_8546A79BA76D4FD2",
    "login_name": "taidongxu",
    "display_name": "太东旭",
    "employee_no": "52073",
    "role_codes": ["team_leader"],
    "permissions": [
      "dashboard:view",
      "order:create",
      "order:list",
      "order:submit",
      "order:view",
      "tool:search"
    ],
    "current_org": {
      "org_id": "ORG_DEPT_005",
      "org_name": "复材车间"
    }
  }
}
```

**Assessment**: ✅ PASS - Login successful

### Step 2: Search Tool T000001

**API Endpoint**: `GET /api/tools/search?keyword=T000001`

**Response**:
```json
{
  "success": true,
  "data": [{
    "tool_id": "T000001",
    "tool_code": "T000001",
    "tool_name": "测试用工装",
    "drawing_no": "Tooling_IO_TEST",
    "spec_model": "测试机型",
    "current_location_text": "A00",
    "available_status": "1-工装完好可用",
    "status_text": ""
  }]
}
```

**Assessment**: ✅ PASS - Tool T000001 found

### Step 3: Create Outbound Order

**API Endpoint**: `POST /api/tool-io-orders`

**Issue Encountered**:
```
Tool T000001 is currently occupied by order TO-OUT-20260319-001 (status: submitted)
```

**Assessment**: ⚠️ BLOCKED - Tool was already occupied by another order in submitted status

### Existing Order Analysis

| Order No | Status | Initiator | Organization |
|----------|--------|-----------|--------------|
| TO-OUT-20260319-001 | submitted | 太东旭 | ORG_DEPT_005 |
| TO-OUT-20260318-005 | draft | Admin | - |
| TO-OUT-20260318-006 | draft | Admin | - |

### Step 4: Access Order Detail

**API Endpoint**: `GET /api/tool-io-orders/TO-OUT-20260319-001`

**Response** (truncated):
```json
{
  "success": true,
  "data": {
    "order_no": "TO-OUT-20260319-001",
    "order_status": "submitted",
    "order_type": "outbound",
    "initiator_id": "U_8546A79BA76D4FD2",
    "initiator_name": "太东旭",
    "items": [{
      "tool_code": "T000001",
      "tool_name": "测试用工装",
      "apply_qty": "1.00",
      "item_status": "pending_check"
    }]
  }
}
```

**Assessment**: ✅ PASS - Order detail retrieved successfully

### Step 5: Keeper Login (hutingting)

**API Endpoint**: `POST /api/auth/login`

**Response**:
```json
{
  "success": true,
  "user": {
    "user_id": "U_7954837C515844BA",
    "login_name": "hutingting",
    "role_codes": ["keeper"],
    "permissions": [
      "dashboard:view",
      "notification:send_feishu",
      "order:keeper_confirm",
      "order:list",
      "order:transport_execute",
      "tool:status_update"
    ],
    "current_org": {
      "org_id": "ORG_DEPT_001",
      "org_name": "树脂事业部"
    }
  }
}
```

**Assessment**: ✅ PASS - Keeper login successful

### Step 6: Keeper Access Pending Orders

**API Endpoint**: `GET /api/tool-io-orders/pending-keeper`

**Response**:
```json
{
  "success": true,
  "data": []
}
```

**Assessment**: ❌ ISSUE - RBAC Data Isolation prevents cross-org order access

**Root Cause**: Order TO-OUT-20260319-001 belongs to ORG_DEPT_005, but Keeper hutingting belongs to ORG_DEPT_001. The RBAC data scope filtering prevents the keeper from seeing orders outside their organization.

---

## Phase 2: RBAC Behavior Verification

### Permission Checks in OrderDetail.vue

**Location**: `frontend/src/pages/tool-io/OrderDetail.vue:389-398`

```javascript
const canSubmit = computed(() => session.hasPermission('order:submit') && order.value.orderStatus === 'draft')
const canCancel = computed(
  () => session.hasPermission('order:cancel') && ['draft', 'rejected'].includes(order.value.orderStatus)
)
const canFinalConfirm = computed(() => {
  return Boolean(finalConfirmState.value.available)
})
const canDelete = computed(() => {
  return session.isAdmin() || session.hasPermission('order:delete')
})
```

**Assessment**: ✅ PASS - All permission checks now use proper `session.hasPermission()` method instead of hardcoded role comparisons.

### KeeperProcess Permission Logic

**Location**: `frontend/src/pages/tool-io/KeeperProcess.vue:602-612`

```javascript
const canReview = computed(
  () =>
    session.hasPermission('order:keeper_confirm') &&
    ['submitted', 'partially_confirmed'].includes(selectedOrder.value.orderStatus)
)

const canNotify = computed(
  () =>
    (session.hasPermission('notification:send_feishu') || session.hasPermission('order:keeper_confirm')) &&
    ['keeper_confirmed', 'partially_confirmed', 'transport_notified'].includes(selectedOrder.value.orderStatus)
)
```

**Assessment**: ✅ PASS - `canNotify` now includes fallback permission check.

---

## Phase 3: Workflow Component Usage

### OrderDetail.vue Uses WorkflowStepper Component

**Location**: `frontend/src/pages/tool-io/OrderDetail.vue:136-141`

```vue
<WorkflowStepper
  :current-status="order.orderStatus"
  :order-type="order.orderType"
  :show-header="false"
  :custom-labels="workflowCustomLabels"
/>
```

**Assessment**: ✅ PASS - Previously had inline implementation, now properly uses the shared component with custom labels for special states.

### OrderCreate.vue Missing Workflow Preview

**Location**: `frontend/src/pages/tool-io/OrderCreate.vue`

**Issue**: No workflow stepper component found in OrderCreate.vue.

**Assessment**: ❌ ISSUE - Order creation page does not show workflow preview to users, making it unclear what happens after submission.

---

## Phase 4: Confirmation Dialog Consistency

### OrderList.vue Confirmation Dialogs

**Location**: `frontend/src/pages/tool-io/OrderList.vue:509-527`

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

### OrderDetail.vue Confirmation Dialogs

**Location**: `frontend/src/pages/tool-io/OrderDetail.vue:493-539`

| Action | Has Confirmation | Issue |
|--------|-----------------|-------|
| submitCurrentOrder | ❌ NO | **INCONSISTENT** - No confirmation before submit |
| cancelCurrentOrder | ✅ YES | Line 499 |
| finalConfirmCurrentOrder | ✅ YES | Line 505 |
| deleteCurrentOrder | ✅ YES | Lines 511-521 |

**Critical Issue**: `OrderDetail.vue:493-496` does NOT have a confirmation dialog:

```javascript
async function submitCurrentOrder() {
  const result = await submitOrder(props.orderNo, operatorPayload())
  if (result.success) loadOrder()
}
```

---

## Phase 5: Theme System Improvements

### SettingsPage.vue Theme Initialization

**Location**: `frontend/src/pages/settings/SettingsPage.vue:358-367`

```javascript
function initTheme() {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
  } else {
    isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme(isDarkMode.value)
}
```

**Assessment**: ✅ IMPROVED - Now checks system preference on first load.

---

## Phase 6: CSS Variable Adoption

### MainLayout.vue Scrollbar

**Location**: `frontend/src/layouts/MainLayout.vue:216-233`

```css
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: hsl(var(--muted-foreground) / 0.3);
  border-radius: 10px;
}
```

**Assessment**: ✅ FIXED - Now uses CSS variables.

### OrderList.vue mist-input

**Location**: `frontend/src/pages/tool-io/OrderList.vue:544-570`

**Assessment**: ✅ FIXED - Now uses CSS variables.

---

## Issues Fixed Since Previous Report

| Issue | Previous Status | Current Status | Evidence |
|-------|----------------|----------------|----------|
| Hardcoded Role Checks in OrderDetail.vue | CRITICAL | **FIXED** | `OrderDetail.vue:389-398` now uses `session.hasPermission()` |
| OrderDetail uses inline workflow | CRITICAL | **FIXED** | `OrderDetail.vue:136-141` now uses `<WorkflowStepper>` component |
| Dark mode scrollbar hardcoded colors | HIGH | **FIXED** | `MainLayout.vue:226-231` now uses CSS variables |
| mist-input class hardcoded colors | HIGH | **FIXED** | `OrderList.vue:545-569` uses CSS variables |
| KeeperProcess canNotify permission | HIGH | **FIXED** | `KeeperProcess.vue:608-612` has fallback |
| Submit action no confirmation | MEDIUM | **PARTIALLY FIXED** | `OrderList.vue:509-520` has confirmation, `OrderDetail.vue:493-496` does NOT |
| Theme sync with system | MEDIUM | **IMPROVED** | `SettingsPage.vue:358-367` checks `prefers-color-scheme` on init |

---

## Critical Issues Summary

### Priority: CRITICAL

1. **Submit Action Missing Confirmation in OrderDetail.vue**
   - Location: `OrderDetail.vue:493-496`
   - Impact: Inconsistent user experience
   - Fix: Add `ElMessageBox.confirm()` before `submitOrder()` call

### Priority: HIGH

2. **RBAC Data Isolation Blocks Cross-Org Workflow Testing**
   - Location: System-wide RBAC implementation
   - Impact: Cannot complete full E2E workflow with test users in different organizations
   - Root Cause: Orders belong to ORG_DEPT_005, Keeper belongs to ORG_DEPT_001
   - Note: This is expected behavior for production, but limits E2E testing scope

### Priority: MEDIUM

3. **OrderCreate.vue Missing Workflow Preview**
   - Location: `OrderCreate.vue`
   - Impact: Users don't know what happens after order creation
   - Fix: Add `<WorkflowStepper>` component showing the workflow steps

4. **Theme Toggle Doesn't Sync with System After Initial Load**
   - Location: `SettingsPage.vue:348-367`
   - Impact: If user changes system theme while app is running, app doesn't update
   - Fix: Add `window.matchMedia` listener for theme changes

---

## E2E Simulation Summary

| Step | Action | User | Result | Notes |
|------|--------|------|--------|-------|
| 1 | Login | taidongxu (Team Leader) | ✅ PASS | Token received |
| 2 | Search Tool | taidongxu | ✅ PASS | T000001 found |
| 3 | Create Order | taidongxu | ⚠️ BLOCKED | Tool already occupied |
| 4 | View Order Detail | taidongxu | ✅ PASS | TO-OUT-20260319-001 accessible |
| 5 | Login | hutingting (Keeper) | ✅ PASS | Token received |
| 6 | Access Pending Orders | hutingting | ❌ FAIL | RBAC data isolation |

---

## Recommendations

### Immediate (Before Release)

1. Add confirmation dialog to `OrderDetail.vue.submitCurrentOrder()` function (CRITICAL)
2. Consider adding workflow preview to OrderCreate.vue

### Short Term (Next Sprint)

1. Add system theme change listener to SettingsPage.vue for live theme sync
2. Create test users in the same organization for E2E testing

### Long Term (Future Releases)

1. Add breadcrumb navigation for orientation
2. Implement notification center UI for internal notifications

---

## Test Report Metadata

- **Report Format Version**: 1.2
- **Testing Method**: Code-level exploratory review + API simulation
- **Previous Report**: `HUMAN_SIMULATED_E2E_TEST_REPORT_20260319_000000.md`
- **Files Reviewed**:
  - `frontend/src/pages/tool-io/OrderDetail.vue`
  - `frontend/src/pages/tool-io/OrderList.vue`
  - `frontend/src/pages/tool-io/OrderCreate.vue`
  - `frontend/src/pages/settings/SettingsPage.vue`
  - `frontend/src/layouts/MainLayout.vue`
  - `frontend/src/components/workflow/WorkflowStepper.vue`
  - `frontend/src/pages/tool-io/KeeperProcess.vue`
- **Backend**: SQL Server + Flask REST API (localhost:8151)
- **Frontend**: Vue 3 + Element Plus + Vite

---

*Generated by Claude Code Human E2E Tester Skill*
*Report Location: test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260319_141935.md*
