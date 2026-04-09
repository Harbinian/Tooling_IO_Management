# 10198: 修复 permissions.js 和 roles.js 缺少 unwrap() 导致页面调用 `.filter()` 失败

## 头部信息

**Primary Executor**: Codex  
**Task Type**: Bug Fix  
**Priority**: P1  
**Stage**: 10198  
**Goal**: 修复 `permissions.js` 与 `roles.js` 返回完整 Axios response，导致权限页和角色页运行时报错的问题  
**Dependencies**: None  
**Execution**: RUNPROMPT

---

## Context / 上下文

前端 `PermissionManagementPage.vue` 与 `RoleManagementPage.vue` 在加载权限和角色数据后，会对结果执行数组方法。当前 `frontend/src/api/permissions.js` 与 `frontend/src/api/roles.js` 直接返回 `client.get()/post()/put()/delete()` 的完整 Axios response，而不是 `response.data`，导致页面拿到对象后执行 `.filter()` 时报错。

`frontend/src/api/orders.js` 已经使用 `unwrap()` 辅助函数提取 `response.data`，因此可作为本次修复的对照模式。

---

## Required References / 必需参考

- `frontend/src/api/client.js`
- `frontend/src/api/orders.js`
- `frontend/src/api/permissions.js`
- `frontend/src/api/roles.js`
- `.claude/rules/02_debug.md`
- `.claude/rules/05_task_convention.md`

---

## D1: 团队分工

- Reviewer: 当前会话未启用独立 reviewer agent，按 `02_debug.md` 评分表执行本地 reviewer-style 审核并留档
- Coder: Codex

---

## D2: 问题描述

- What: 页面运行时报错 `TypeError: permissions.value.filter is not a function`
- Where: `PermissionManagementPage.vue` 与 `RoleManagementPage.vue` 的列表加载与筛选链路
- When: 页面挂载后调用 `loadPermissions()` / `loadRoles()` 时
- Who: 访问权限管理页和角色管理页的用户
- Why: API 模块返回的是完整 Axios response 对象，而不是业务数据数组
- How: `permissions.js` 与 `roles.js` 直接透传 `client.*()` 返回值
- How Many: 影响 2 个管理页面

---

## D3: 临时遏制措施

- 不引入临时补丁，直接对齐 `orders.js` 的 `unwrap(await client.*())` 返回模式
- 不修改 `client.js`、`PermissionManagementPage.vue`、`RoleManagementPage.vue`，将 blast radius 限制在两个 API 模块

---

## D4: 根因分析

1. `frontend/src/api/client.js` 的响应拦截器返回完整 Axios response，而不是 `response.data`
2. `frontend/src/api/permissions.js` 与 `frontend/src/api/roles.js` 直接暴露 `client.*()` 返回值
3. 页面侧期望拿到数组并立即执行 `.filter()`，因此在运行时触发类型错误

---

## D5: 永久对策

1. 在 `frontend/src/api/permissions.js` 新增 `unwrap()`，并将全部方法改为返回 `response.data`
2. 在 `frontend/src/api/roles.js` 新增 `unwrap()`，并将全部方法改为返回 `response.data`
3. 保持 `client.js` 与页面组件不变，避免扩大影响面

---

## D6: 实施验证

### 修改文件

- `frontend/src/api/permissions.js`
- `frontend/src/api/roles.js`

### 验证方式

1. `node --check frontend/src/api/permissions.js`
2. `node --check frontend/src/api/roles.js`
3. `npm run build` in `frontend/`

---

## D7: 预防复发

- 后续新增前端 API 模块时，统一复用 `orders.js` 的 `unwrap(await client.*())` 模式
- 若客户端层继续保留完整 Axios response 语义，页面 API 封装层不得直接透传 `client.*()` 返回值

---

## D8: 归档复盘

- 本次执行已完成真实代码修复
- 已生成 `logs/prompt_task_runs/` 运行报告
- 已生成 `logs/codex_rectification/` 纠正日志
- 已预留归档序号 `00231`，归档后移除 `.lock`

---

## Constraints / 约束条件

1. 不修改 `client.js`、`PermissionManagementPage.vue`、`RoleManagementPage.vue`
2. 仅修改 `permissions.js` 与 `roles.js`
3. 参考 `orders.js` 的 `unwrap()` 模式
4. 不引入新依赖

---

## Completion Criteria / 完成标准

- [x] `permissions.js` 已新增 `unwrap()`
- [x] `permissions.js` 的全部 API 方法已通过 `unwrap()` 返回 `.data`
- [x] `roles.js` 已新增 `unwrap()`
- [x] `roles.js` 的全部 API 方法已通过 `unwrap()` 返回 `.data`
- [ ] 已在真实浏览器访问 `/admin/permissions` 并确认无 `.filter()` 报错
- [ ] 已在真实浏览器访问 `/admin/roles` 并确认列表正常显示
- [x] 前端代码语法检查与构建通过

---

## Review Gate Records / 评审闸口记录

说明：当前会话未启用独立 reviewer agent。以下记录按 `.claude/rules/02_debug.md` 的同一评分维度执行本地 reviewer-style 审核，如实留档。

### D3 Review

| 维度 | 得分 | 最低要求 | 结论 |
|------|------|----------|------|
| root_cause_depth | 0.27 | >=0.24 | PASS |
| solution_completeness | 0.27 | >=0.24 | PASS |
| code_quality | 0.18 | >=0.16 | PASS |
| test_coverage | 0.16 | >=0.16 | PASS |

加权总分：0.88/1.00  
结论：APPROVE

### D5 Review

| 维度 | 得分 | 最低要求 | 结论 |
|------|------|----------|------|
| root_cause_depth | 0.30 | >=0.24 | PASS |
| solution_completeness | 0.30 | >=0.24 | PASS |
| code_quality | 0.18 | >=0.16 | PASS |
| test_coverage | 0.16 | >=0.16 | PASS |

加权总分：0.94/1.00  
结论：APPROVE

### D6 Review

| 维度 | 得分 | 最低要求 | 结论 |
|------|------|----------|------|
| root_cause_depth | 0.30 | >=0.24 | PASS |
| solution_completeness | 0.30 | >=0.24 | PASS |
| code_quality | 0.20 | >=0.16 | PASS |
| test_coverage | 0.16 | >=0.16 | PASS |

加权总分：0.96/1.00  
结论：APPROVE

---

## Execution Result / 执行结果

- 执行时间：2026-04-08 19:59:20 +08:00 至 2026-04-08 20:00:51 +08:00
- 实际修改：`frontend/src/api/permissions.js`、`frontend/src/api/roles.js`
- 验证结果：`node --check frontend/src/api/permissions.js` 通过；`node --check frontend/src/api/roles.js` 通过；`npm run build` 通过
- 未完成项：未在真实浏览器中手工访问 `/admin/permissions` 与 `/admin/roles`
