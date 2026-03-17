Primary Executor: Gemini
Task Type: Bug Fix
Priority: P2
Stage: 128
Goal: Fix multiple UI issues in OrderList.vue (dark mode input styles, date picker theming, submit confirmation)
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

During E2E testing, multiple UI issues were discovered in `frontend/src/pages/tool-io/OrderList.vue`. These are all in the same file and can be fixed together:

### Issue 1: mist-input CSS Dark Mode (was prompt 128)

The `mist-input` class (lines 523-547) uses hardcoded RGB colors that don't adapt to dark mode:

```css
.mist-input {
  border: 1px solid rgb(226 232 240);  /* Hardcoded light mode */
  background: rgba(255, 255, 255, 0.92);  /* Hardcoded light mode */
  color: rgb(15 23 42);  /* Hardcoded dark text */
}
.mist-input:focus {
  border-color: rgb(148 163 184);  /* Hardcoded */
  background: rgb(255 255 255);  /* Hardcoded */
}
.mist-input::placeholder {
  color: rgb(148 163 184);  /* Hardcoded */
}
```

### Issue 2: Native Date Inputs (was prompt 129)

Native `<input type="date">` elements (lines 94, 98) don't match the UI theme:

```html
<input v-model="filters.dateFrom" type="date" class="mist-input" />
<input v-model="filters.dateTo" type="date" class="mist-input" />
```

### Issue 3: Submit Without Confirmation (was prompt 130)

The submit action (lines 496-498) submits immediately without confirmation:

```javascript
async function submitCurrentOrder(order) {
  const result = await submitOrder(order.orderNo, buildOperator())
  if (result.success) loadOrders()
}
```

---

## Required References / 必需参考

- `frontend/src/pages/tool-io/OrderList.vue` - File with all issues
- Element Plus DatePicker documentation - el-date-picker component
- Element Plus ElMessageBox documentation
- CSS variables definitions in main.css or Tailwind config

---

## Core Task / 核心任务

Fix three UI issues in OrderList.vue:
1. Replace hardcoded RGB colors in .mist-input class with CSS variables
2. Replace native `<input type="date">` with Element Plus `<el-date-picker>`
3. Add confirmation dialog before order submission

---

## Required Work / 必需工作

### Part A: Fix mist-input Dark Mode

1. **Inspect OrderList.vue** to find the mist-input CSS (lines 523-547)

2. **Replace hardcoded colors with CSS variables**:
```css
.mist-input {
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--foreground);
}
.mist-input:focus {
  border-color: var(--ring);
  box-shadow: 0 0 0 3px var(--ring);
  background: var(--card);
}
.mist-input::placeholder {
  color: var(--muted-foreground);
}
```

3. **Check if mist-input is used elsewhere** - fix will cascade

### Part B: Replace Native Date Inputs

1. **Replace native `<input type="date">`** with Element Plus DatePicker:
```html
<el-date-picker
  v-model="filters.dateFrom"
  type="date"
  placeholder="选择日期"
  class="w-full"
/>
<el-date-picker
  v-model="filters.dateTo"
  type="date"
  placeholder="选择日期"
  class="w-full"
/>
```

2. **Verify date format** sent to API remains correct

### Part C: Add Submit Confirmation

1. **Add ElMessageBox.confirm** before submit:
```javascript
async function submitCurrentOrder(order) {
  await ElMessageBox.confirm(
    `确认提交单据 ${order.orderNo} 吗？提交后将进入保管员审核流程。`,
    '提交单据',
    { type: 'warning' }
  )
  const result = await submitOrder(order.orderNo, buildOperator())
  if (result.success) loadOrders()
}
```

2. **Import ElMessageBox** if not already imported

---

## Constraints / 约束条件

- Do NOT change the v-model bindings (filters.dateFrom, filters.dateTo)
- Do NOT change the submitOrder API call
- Do NOT change border-radius (1rem) or padding for mist-input
- Maintain the 2.75rem min-height for mist-input
- Keep the transition effects

---

## Completion Criteria / 完成标准

### Part A: mist-input Dark Mode
1. **Acceptance Test A1**: mist-input uses CSS variables instead of hardcoded RGB
2. **Acceptance Test A2**: mist-input is visible in light mode
3. **Acceptance Test A3**: mist-input is visible in dark mode
4. **Acceptance Test A4**: Focus state works in both modes

### Part B: Date Picker
5. **Acceptance Test B1**: Native `<input type="date">` replaced with `<el-date-picker>`
6. **Acceptance Test B2**: Both date filters work correctly
7. **Acceptance Test B3**: Date picker matches UI theme in light and dark modes
8. **Acceptance Test B4**: Filtering by date range still works

### Part C: Submit Confirmation
9. **Acceptance Test C1**: Confirmation dialog appears before submission
10. **Acceptance Test C2**: Dialog shows the order number
11. **Acceptance Test C3**: Submission only proceeds if user confirms
12. **Acceptance Test C4**: Clicking "取消" cancels without error

### General
13. **Acceptance Test G1**: `npm run build` passes without errors
