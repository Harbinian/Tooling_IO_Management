# 10198: permissions.js 和 roles.js 缺少 unwrap() 导致前端调用 .filter() 失败

## 头部信息

**Primary Executor**: Codex
**Task Type**: Bug Fix
**Priority**: P1
**Stage**: 10198
**Goal**: 修复 permissions.js 和 roles.js 缺少 unwrap() 导致 PermissionManagementPage 和 RoleManagementPage 运行时错误
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context / 上下文

前端 `PermissionManagementPage.vue` 和 `RoleManagementPage.vue` 在加载权限/角色数据时崩溃，错误为 `TypeError: permissions.value.filter is not a function`。

**根本原因**: `client.js` 的响应拦截器直接返回完整的 Axios `response` 对象（包含 headers、status、data 等），而不是返回 `response.data`。`permissions.js` 和 `roles.js` 的 API 函数没有提取 `response.data`，导致调用方拿到的是 Axios response 对象而非数组。

`orders.js` 的 API 函数正确使用了 `unwrap()` 辅助函数提取 `response.data`，因此没有这个问题。

---

## Required References / 必需参考

### 代码文件
- `frontend/src/api/client.js` — Axios 客户端配置（响应拦截器返回完整 response）
- `frontend/src/api/orders.js` — **正确的 API 模式参考**，包含 `unwrap()` 函数定义和使用示例
- `frontend/src/api/permissions.js` — 需要修复
- `frontend/src/api/roles.js` — 需要修复

### API 端点
- `GET /admin/permissions` — 返回 permissions 数组
- `GET /admin/roles` — 返回 roles 数组

---

## D1: 团队分工

- **Reviewer**: reviewer agent
- **Coder**: Codex
- **Architect**: (本 bug 简单，无需额外架构设计)

---

## D2: 问题描述 (5W2H)

| 维度 | 内容 |
|------|------|
| **What** | `permissions.value.filter is not a function` 运行时错误 |
| **Where** | `PermissionManagementPage.vue:37` (filteredPermissions computed) |
| **When** | 页面挂载时调用 `loadPermissions()` 之后 |
| **Who** | 所有访问权限管理页面的用户 |
| **Why** | `permissions.value` 是 Axios response 对象，不是数组 |
| **How** | `getPermissions()` 返回 `client.get()` 的完整 response，未提取 `.data` |
| **How Many** | 影响 PermissionManagementPage 和 RoleManagementPage 两个页面 |

---

## D3: 临时遏制措施 (Containment)

**临时修复**: 无需临时措施（问题简单，可直接实施永久修复）

**防退化**: 修复后 PermissionManagementPage 和 RoleManagementPage 必须能正常加载和筛选数据

---

## D4: 根因分析 (5 Whys)

1. **Why**: `permissions.value.filter()` 报错 `filter is not a function`
2. **Why**: `permissions.value` 是 Axios response 对象 `{data: [...], status: 200, ...}`，不是数组
3. **Why**: `loadPermissions()` 调用 `permissionsApi.getPermissions()` 直接赋值
4. **Why**: `permissions.js` 的 `getPermissions()` 返回 `client.get('/admin/permissions', { params })` 原始响应
5. **Why**: `client.js` 响应拦截器返回完整 response 对象，而 `orders.js` 正确使用了 `unwrap()` 提取 `.data`

**根因**: `permissions.js` 和 `roles.js` 缺少 `unwrap()` 辅助函数来提取 Axios response 的 `.data` 部分

---

## D5: 永久对策 + 防退化宣誓

### 修复方案

1. 在 `permissions.js` 中添加 `unwrap()` 辅助函数
2. 在 `roles.js` 中添加 `unwrap()` 辅助函数
3. 将两个文件中的所有 API 函数返回值从 `client.get()/post()/put()/delete()` 改为 `unwrap(client.get()/...)`

### 防退化宣誓

- `permissions.js` 必须与 `orders.js` 保持相同的 API 返回模式
- `roles.js` 必须与 `orders.js` 保持相同的 API 返回模式
- 前端组件（`PermissionManagementPage.vue`、`RoleManagementPage.vue`）无需修改

---

## D6: 实施验证 (Implementation)

### 修改文件

1. **`frontend/src/api/permissions.js`**
   - 添加 `function unwrap(response) { return response.data }`
   - 将所有 `client.get/post/put/delete(...)` 包裹在 `unwrap()` 中

2. **`frontend/src/api/roles.js`**
   - 添加 `function unwrap(response) { return response.data }`
   - 将所有 `client.get/post/put/delete(...)` 包裹在 `unwrap()` 中

### 验证方式

1. 语法检查: `cd frontend && node --check src/api/permissions.js src/api/roles.js`（如支持）
2. 浏览器访问 `/admin/permissions`，确认页面正常加载且筛选功能正常
3. 浏览器访问 `/admin/roles`，确认角色列表正常显示

---

## D7: 预防复发 (Prevention)

- `permissions.js` 和 `roles.js` 已添加 `unwrap()` 模式，与 `orders.js` 保持一致
- 后续所有新增 API 模块必须参考 `orders.js` 的 `unwrap()` 模式

---

## D8: 归档复盘 (Documentation)

待修复完成后记录归档。

---

## Constraints / 约束条件

1. **不得修改**: `client.js`、`PermissionManagementPage.vue`、`RoleManagementPage.vue`
2. **仅修改**: `permissions.js`、`roles.js`
3. **必须参考**: `orders.js` 的 `unwrap()` 模式
4. **不得引入新依赖**: 仅使用原生 JavaScript/Node.js

---

## Completion Criteria / 完成标准

- [ ] `permissions.js` 添加了 `unwrap()` 函数
- [ ] `permissions.js` 所有 API 函数返回值都通过 `unwrap()` 提取 `.data`
- [ ] `roles.js` 添加了 `unwrap()` 函数
- [ ] `roles.js` 所有 API 函数返回值都通过 `unwrap()` 提取 `.data`
- [ ] 浏览器访问 `/admin/permissions` 页面正常加载，筛选功能正常（无 `filter is not a function` 错误）
- [ ] 浏览器访问 `/admin/roles` 页面正常加载，角色列表正常显示
- [ ] 前端代码无新增 ESLint/语法错误
