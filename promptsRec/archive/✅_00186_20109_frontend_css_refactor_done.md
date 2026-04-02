# Prompt: 前端CSS重构 - 硬编码颜色修复

Primary Executor: Gemini
Task Type: Refactoring
Priority: P1
Stage: Prompt Number
Goal: 修复前端硬编码颜色问题，改为CSS变量
Dependencies: None
Execution: RUNPROMPT

---

## Context

代码审查报告 `review-reports/CODE_REVIEW_REPORT_20260401.md` 发现6个P1/P2前端CSS问题：

| # | 问题 | 位置 |
|---|------|------|
| 1 | WorkflowStepper.vue 硬编码颜色 | WorkflowStepper.vue:305-308 |
| 2 | OrderDetail.vue 硬编码按钮颜色 | OrderDetail.vue:48,56,64,364 |
| 3 | ReportTransportIssueDialog.vue 硬编码 | ReportTransportIssueDialog.vue:55 |
| 4 | ResolveIssueDialog.vue 硬编码 | ResolveIssueDialog.vue:40 |
| 5 | Button.vue dark-outline variant | Button.vue:23 |
| 6 | DashboardOverview.vue 硬编码 | DashboardOverview.vue:103 |
| 7 | SettingsPage.vue 缺少系统主题监听 | SettingsPage.vue |
| 8 | 删除确认消息不一致 | OrderList.vue, OrderDetail.vue |

---

## Required References

- `frontend/src/components/workflow/WorkflowStepper.vue`
- `frontend/src/pages/tool-io/OrderDetail.vue`
- `frontend/src/components/tool-io/ReportTransportIssueDialog.vue`
- `frontend/src/components/tool-io/ResolveIssueDialog.vue`
- `frontend/src/components/ui/Button.vue`
- `frontend/src/pages/dashboard/DashboardOverview.vue`
- `frontend/src/pages/settings/SettingsPage.vue`
- `frontend/src/pages/tool-io/OrderList.vue`
- `.claude/rules/04_frontend.md` - 前端开发规范
- `frontend/src/assets/main.css` 或 CSS 变量定义文件

---

## Core Task

### 修复1-6: 硬编码颜色 → CSS变量

**替换规则**:

| 禁止 | 替代方案 |
|------|---------|
| `text-white` | `text-primary-foreground` |
| `bg-emerald-500` | `bg-primary` 或 CSS 变量 |
| `bg-rose-500` | `bg-destructive` |
| `bg-amber-500` | `bg-warning` |
| `bg-white text-slate-900` | `bg-background text-foreground` |

**具体修复**:

1. **WorkflowStepper.vue:305-308**
   ```javascript
   // 修改前
   if (state === 'complete') return 'bg-emerald-500 text-white'

   // 修改后
   if (state === 'complete') return 'bg-primary text-primary-foreground'
   ```

2. **OrderDetail.vue:48,56,64,364**
   ```vue
   <!-- 修改前 -->
   class="bg-emerald-500 text-white"
   class="bg-rose-500 text-white"

   <!-- 修改后 -->
   class="bg-primary text-primary-foreground"
   class="bg-destructive text-primary-foreground"
   ```

3. **ReportTransportIssueDialog.vue:55**
   ```vue
   <!-- 修改前 -->
   class="bg-amber-500 text-white"

   <!-- 修改后 -->
   class="bg-warning text-primary-foreground"
   ```

4. **ResolveIssueDialog.vue:40**
   ```vue
   <!-- 修改前 -->
   class="bg-emerald-500 text-white"

   <!-- 修改后 -->
   class="bg-primary text-primary-foreground"
   ```

5. **Button.vue:23** - dark-outline variant
   - 检查并替换 variant 定义中的 `text-white`

6. **DashboardOverview.vue:103**
   ```vue
   <!-- 修改前 -->
   class="bg-white text-slate-900"

   <!-- 修改后 -->
   class="bg-background text-foreground"
   ```

### 修复7: SettingsPage.vue 系统主题监听

**问题**: 没有监听系统主题变化，用户手动选择后不响应系统变化。

**修复要求**:
```javascript
// 添加 userManualOverride 标志
let userManualOverride = false

onMounted(() => {
  initTheme()

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!userManualOverride) {
      isDarkMode.value = e.matches
      applyTheme(e.matches)
    }
  })
})

function toggleTheme(value) {
  userManualOverride = true  // 用户手动选择后不再响应系统
  // ... 原有逻辑
}
```

### 修复8: 删除确认消息统一

**问题**: OrderList.vue 和 OrderDetail.vue 删除确认消息不一致。

**统一格式**:
```javascript
// 两者都应使用
`确认删除单据 ${orderNo} 吗？删除后不可恢复。`
```

---

## Required Work

1. **检查CSS变量定义** - 确认 `bg-primary`, `text-primary-foreground`, `bg-destructive`, `bg-warning`, `bg-background`, `text-foreground` 已定义

2. **修复所有硬编码颜色** - 按上表情形逐一替换

3. **添加主题监听** - 在 SettingsPage.vue 添加系统主题变化监听

4. **统一删除消息** - OrderList.vue 和 OrderDetail.vue 使用相同格式

---

## Constraints

- **严禁使用硬编码颜色** - 必须使用 CSS 变量
- **保持 UI 一致性** - 相同操作在不同页面表现一致
- **不破坏现有功能** - 只改样式，不改行为
- **UTF-8 编码** - 所有文件操作

---

## Completion Criteria

1. 所有硬编码颜色已替换为 CSS 变量
2. SettingsPage.vue 正确监听系统主题变化
3. 删除确认消息格式统一
4. `npm run build` 成功无错误
5. 视觉上与修改前保持一致（仅颜色语义化）
