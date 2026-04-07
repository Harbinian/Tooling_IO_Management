# RBAC 管理页面 - 前端页面实现

Primary Executor: Gemini
Task Type: Feature Development
Priority: P0
Stage: Prompt 2/2
Goal: 实现前端 RBAC 管理页面（角色管理、权限管理、角色-权限分配）
Dependencies: 00091 (后端 API 扩展必须先完成)
Execution: RUNPROMPT

---

## Context

系统需要提供图形化的 RBAC 管理界面。本提示词负责实现前端页面和 API 封装。

**技术栈**: Vue 3 + 自定义组件体系（Button/Card/Input/Select 等）+ Vite
**前端目录**: `E:\CA001\Tooling_IO_Management\frontend`
**端口**: 前端 8150
**工作目录**: `E:\CA001\Tooling_IO_Management`

**重要**: 依赖后端 API 完成（提示词 00091），后端 API 定义如下：

### 后端 API 端点（必须对接）

#### 角色 API
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/roles` | GET | 获取角色列表 |
| `/api/admin/roles` | POST | 创建角色 |
| `/api/admin/roles/<role_id>` | PUT | 更新角色 |
| `/api/admin/roles/<role_id>` | DELETE | 删除角色 |
| `/api/admin/roles/<role_id>/permissions` | GET | 获取角色已有权限 |
| `/api/admin/roles/<role_id>/permissions` | PUT | 分配权限给角色 |

#### 权限 API
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/admin/permissions` | GET | 获取权限列表 |
| `/api/admin/permissions` | POST | 创建权限 |
| `/api/admin/permissions/<permission_code>` | PUT | 更新权限 |
| `/api/admin/permissions/<permission_code>` | DELETE | 删除权限 |

---

## Required References

### 核心文件

| 文件 | 说明 |
|------|------|
| `frontend/src/pages/admin/UserAdminPage.vue` | **必须参考**的现有 admin 页面（使用自定义组件，非 Element Plus） |
| `frontend/src/api/adminUsers.js` | 参考现有 API 封装模式 |
| `frontend/src/api/client.js` | API 客户端封装 |
| `frontend/src/store/session.js` | 权限检查 `hasPermission()` |
| `frontend/src/router/index.js` | 路由配置（扁平子路由格式：`path: 'admin/roles'`） |
| `frontend/src/debug/debugIds.js` | DEBUG_ID 定义（使用 `DEBUG_IDS.ADMIN.*` 对象树） |
| `frontend/src/layouts/MainLayout.vue` | 系统菜单入口（**不是** AdminLayout.vue） |

### 规则文件（强制遵守）

| 文件 | 关键规则 |
|------|---------|
| `04_frontend.md` | 前端开发规范（DEBUG_ID、自定义组件使用） |
| `00_core.md` | UTF-8 编码 |

---

## Core Task

### 1. 新建 `frontend/src/api/roles.js`

角色 API 封装：

```javascript
import client from './client'

export default {
  getAdminRoles() {
    return client.get('/admin/roles')
  },
  createRole(payload) {
    return client.post('/admin/roles', payload)
  },
  updateRole(roleId, payload) {
    return client.put(`/admin/roles/${roleId}`, payload)
  },
  deleteRole(roleId) {
    return client.delete(`/admin/roles/${roleId}`)
  },
  getRolePermissions(roleId) {
    return client.get(`/admin/roles/${roleId}/permissions`)
  },
  assignPermissions(roleId, payload) {
    return client.put(`/admin/roles/${roleId}/permissions`, payload)
  }
}
```

### 2. 新建 `frontend/src/api/permissions.js`

权限 API 封装：

```javascript
import client from './client'

export default {
  getPermissions(params) {
    return client.get('/admin/permissions', { params })
  },
  createPermission(payload) {
    return client.post('/admin/permissions', payload)
  },
  updatePermission(code, payload) {
    return client.put(`/admin/permissions/${code}`, payload)
  },
  deletePermission(code) {
    return client.delete(`/admin/permissions/${code}`)
  }
}
```

### 3. 新建 `frontend/src/pages/admin/RoleManagementPage.vue`

角色管理页面：

- **路由**: `/admin/roles`
- **功能**: 角色列表、新建角色、编辑角色、删除角色、分配权限
- **表格列**: 角色代码、角色名称、角色类型、状态、操作
- **操作按钮**: 编辑、删除、分配权限

**必须参考**: `UserAdminPage.vue` 的自定义组件体系（Button/Card/Input/Select/Table 等，**不是** Element Plus 组件如 el-table、el-dialog）

**约束**:
- system 类型角色（sys_admin, auditor）不可删除，显示禁用删除按钮
- 使用 `v-debug-id` 属性，格式为 `DEBUG_IDS.ADMIN.U_ADMIN_ROLE_*`（如 `U_ADMIN_ROLE_CREATE_BTN`）
- 参考 UserAdminPage.vue 的确认消息格式

### 4. 新建 `frontend/src/pages/admin/PermissionManagementPage.vue`

权限管理页面：

- **路由**: `/admin/permissions`
- **功能**: 权限列表、新建权限、编辑权限、删除权限
- **表格列**: 权限代码、权限名称、资源、操作、状态

**必须参考**: UserAdminPage.vue 的自定义组件体系

**约束**:
- 使用 `v-debug-id` 属性，格式为 `DEBUG_IDS.ADMIN.U_ADMIN_PERM_*`（如 `U_ADMIN_PERM_CREATE_BTN`）

### 5. 新建 `frontend/src/pages/admin/RolePermissionAssignment.vue`

角色-权限分配页面：

- **路由**: `/admin/roles/:roleId/permissions`
- **功能**: 左侧角色列表，右侧权限复选框矩阵
- **角色列表**: 显示所有角色，点击选择
- **权限矩阵**: 按资源分组显示权限复选框
- **保存**: 批量保存权限分配
- **显示**: 当前角色的已有权限（回显）

**约束**:
- 使用 `v-debug-id` 属性，格式为 `DEBUG_IDS.ADMIN.U_ADMIN_ROLE_PERM_*`
- 权限按 resource_name 分组显示
- 已选择的权限需要回显

### 6. 修改 `frontend/src/router/index.js`

**注意**: 当前使用扁平子路由格式，**不要**创建父路由块。

```javascript
// 在现有 children 数组中添加：
{ path: 'admin/roles', component: () => import('../pages/admin/RoleManagementPage.vue') },
{ path: 'admin/roles/:roleId/permissions', component: () => import('../pages/admin/RolePermissionAssignment.vue') },
{ path: 'admin/permissions', component: () => import('../pages/admin/PermissionManagementPage.vue') }
```

### 7. 修改 `frontend/src/layouts/MainLayout.vue`

在系统管理菜单（sys管理）中添加子菜单入口：

```javascript
// 在 MainLayout.vue 的系统管理菜单区域添加：
{ label: '角色管理', path: '/admin/roles' },
{ label: '权限管理', path: '/admin/permissions' }
```

入口条件：`hasPermission('admin:role_manage')`

### 8. 修改 `frontend/src/debug/debugIds.js`

在 `DEBUG_IDS.ADMIN` 下添加字段（**不是裸字符串**，是对象树；**格式必须为 `{PAGE}-{TYPE}-{NUMBER}`**，参考 `U-CARD-001`、`U-BTN-001`）：

```javascript
ADMIN: {
  // ... 现有字段
  // 格式: U-{PAGE_ABBR}-{TYPE}-{NUMBER}
  // 角色管理页面
  U_ADMIN_ROLE_CARD: 'U-ADMIN-CARD-001',      // 角色列表卡片容器
  U_ADMIN_ROLE_TABLE: 'U-ADMIN-TABLE-001',    // 角色表格
  U_ADMIN_ROLE_CREATE_BTN: 'U-ADMIN-BTN-001', // 新建按钮
  U_ADMIN_ROLE_EDIT_BTN: 'U-ADMIN-BTN-002',   // 编辑按钮
  U_ADMIN_ROLE_DELETE_BTN: 'U-ADMIN-BTN-003', // 删除按钮
  U_ADMIN_ROLE_PERM_BTN: 'U-ADMIN-BTN-004',   // 分配权限按钮
  U_ADMIN_ROLE_FORM_DIALOG: 'U-ADMIN-DIALOG-001', // 角色表单弹窗
  // 权限管理页面
  U_ADMIN_PERM_CARD: 'U-ADMIN-CARD-002',       // 权限列表卡片容器
  U_ADMIN_PERM_TABLE: 'U-ADMIN-TABLE-002',    // 权限表格
  U_ADMIN_PERM_CREATE_BTN: 'U-ADMIN-BTN-005', // 新建按钮
  U_ADMIN_PERM_EDIT_BTN: 'U-ADMIN-BTN-006',   // 编辑按钮
  U_ADMIN_PERM_DELETE_BTN: 'U-ADMIN-BTN-007', // 删除按钮
  U_ADMIN_PERM_FORM_DIALOG: 'U-ADMIN-DIALOG-002', // 权限表单弹窗
  // 角色-权限分配页面
  U_ADMIN_ROLE_PERM_CARD: 'U-ADMIN-CARD-003', // 权限分配页面容器
  U_ADMIN_ROLE_PERM_SAVE_BTN: 'U-ADMIN-BTN-008', // 保存按钮
  U_ADMIN_ROLE_PERM_CHECK: 'U-ADMIN-CHECK-001' // 权限复选框组
}
```

---

## Constraints

1. **UTF-8 编码**: 所有 .vue/.js 文件使用 UTF-8
2. **自定义组件**: **必须参考 UserAdminPage.vue**，使用 Button/Card/Input/Select/Table 等自定义组件，**禁止使用 el-table、el-dialog 等 Element Plus 组件**
3. **DEBUG_ID**: 在 `DEBUG_IDS.ADMIN` 下扩展，**格式必须为 `{PAGE}-{TYPE}-{NUMBER}`（如 `U-ADMIN-CARD-001`、`U-ADMIN-BTN-001`），使用 `U_` 前缀在 JS 中访问（如 `DEBUG_IDS.ADMIN.U_ADMIN_ROLE_CARD`）
4. **API 封装**: 所有 HTTP 调用通过 api 模块，不直接使用 axios
5. **路由格式**: 使用扁平子路由 `path: 'admin/roles'`，**不要**创建父路由块
6. **菜单文件**: 修改 `MainLayout.vue`（**不是** AdminLayout.vue）
7. **权限**: 角色/权限管理页面使用 `admin:role_manage` 权限
8. **无占位符**: 所有代码必须完整可执行

---

## Completion Criteria

- [ ] `frontend/src/api/roles.js` 已创建
- [ ] `frontend/src/api/permissions.js` 已创建
- [ ] `RoleManagementPage.vue` 已创建，包含角色 CRUD 和分配权限入口
- [ ] `PermissionManagementPage.vue` 已创建，包含权限 CRUD
- [ ] `RolePermissionAssignment.vue` 已创建，包含权限分配矩阵
- [ ] 路由已添加（扁平子路由格式）
- [ ] MainLayout.vue 菜单已添加
- [ ] DEBUG_IDS.ADMIN 已扩展（对象树格式）
- [ ] `npm run build` 构建通过
- [ ] 文档同步：更新 `docs/API_SPEC.md`（如有新 API）和 `docs/RBAC_PERMISSION_MATRIX.md`（角色/权限管理说明）
