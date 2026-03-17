Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 124
Goal: Fix Textarea rows prop type error in SettingsPage.vue
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

SettingsPage.vue 中的 Textarea 组件报错：
```
Invalid prop: type check failed for prop "rows". Expected Number with value 5, got String with value "5".
```

问题位置: `<Textarea rows="5" ...>` - `rows` 属性应为 Number 类型，但传入了 String。

## Required References / 必需参考

1. `frontend/src/components/ui/Textarea.vue` - Textarea 组件
2. `frontend/src/pages/settings/SettingsPage.vue` - 问题文件

## Core Task / 核心任务

修复 Textarea 组件的 rows prop 类型错误。

## Required Work / 必需工作

1. **检查 Textarea 组件定义**
   - 查看 `rows` prop 的类型定义
   - 确认期望的类型是 Number 还是 String

2. **修复 SettingsPage.vue 中的调用**
   - 如果组件期望 Number: 改为 `:rows="5"` 或 `rows="5"` (Vue 会自动转换)
   - 如果组件期望 String: 保持现状但检查组件定义

3. **验证修复**
   - 前端构建: `cd frontend && npm run build`
   - 运行时无 Vue warning

## Constraints / 约束条件

- 不破坏现有功能
- 遵循 Vue 最佳实践

## Completion Criteria / 完成标准

- [ ] 无 Vue prop type warning
- [ ] 前端构建通过
- [ ] Settings 页面正常加载
