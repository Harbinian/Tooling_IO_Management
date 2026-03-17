Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 123
Goal: Fix corrupted Chinese characters in SettingsPage.vue
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

SettingsPage.vue 页面中的中文字符串出现 UTF-8 编码损坏（乱码），导致：
1. 页面无法加载，500 错误
2. Vue 编译器报错："Unterminated string constant"

错误位置：
- Line 283-287: `roleMap` 中的角色名称
- Line 293-305: `formatPermission` 中的权限名称映射

## Required References / 必需参考

1. `frontend/src/pages/settings/SettingsPage.vue` - 问题文件
2. 项目中其他 Vue 文件的中文翻译参考

## Core Task / 核心任务

修复 SettingsPage.vue 中损坏的中文字符串，恢复正确的 UTF-8 中文显示。

## Required Work / 必需工作

1. **修复 roleMap 字符串** (Line 283-287):
   - `admin: '绠＄悊鍛?` → `admin: '管理员'`
   - `keeper: '淇濈?锝?'` → `keeper: '保管员'`
   - `team_leader: '鐝?闀?'` → `team_leader: '班组长'`
   - `initiator: '鍙戣捣浜?'` → `initiator: '发起人'`

2. **修复 formatPermission 映射** (Line 293-305):
   - `'dashboard:view': '浠?タ?'` → `'dashboard:view': '查看仪表盘'`
   - `'order:list': '璁?崟?'` → `'order:list': '订单列表'`
   - `'order:create': '鍒涘?'` → `'order:create': '创建订单'`
   - `'order:view': '鍗?'` → `'order:view': '查看详情'`
   - 其他类似修复

3. **检查文件编码**:
   - 确保文件保存为 UTF-8 编码
   - 使用正确的中文字符

## Constraints / 约束条件

- 只修复损坏的中文字符串
- 不改变代码逻辑
- 保持英文变量名和函数名

## Completion Criteria / 完成标准

- [ ] 中文字符串正确显示
- [ ] Settings 页面可以正常加载
- [ ] 前端构建通过: `cd frontend && npm run build`
- [ ] 手动验证页面各 Tab 正常切换
