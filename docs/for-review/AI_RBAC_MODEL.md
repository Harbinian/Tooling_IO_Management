# AI Review: RBAC Model

## Overview

Role-Based Access Control (RBAC) system for the Tooling IO Management System.

## Roles

| Role ID | Role Name | Description |
|---------|-----------|-------------|
| admin | 管理员 | Full system access |
| team_leader | 班组长 | Create orders, final confirm outbound |
| keeper | 仓库管理员 | Confirm items, reject, final confirm inbound |

## Permissions

### Dashboard Permissions

| Permission Code | Description |
|----------------|-------------|
| dashboard:view | View dashboard |

### Order Permissions

| Permission Code | Description |
|----------------|-------------|
| order:list | View order list |
| order:view | View order details |
| order:create | Create new order |
| order:edit | Edit own orders |
| order:submit | Submit order for approval |
| order:keeper_confirm | Confirm order items as keeper |
| order:final_confirm | Final confirmation |
| order:reject | Reject order |
| order:cancel | Cancel order |

### Admin Permissions

| Permission Code | Description |
|----------------|-------------|
| admin:user_manage | Manage users |
| admin:role_manage | Manage roles |

## Permission Codes

From `backend/services/rbac_service.py`:

```
admin:user_manage
admin:role_manage
dashboard:view
order:list
order:view
order:create
order:edit
order:submit
order:keeper_confirm
order:final_confirm
order:reject
order:cancel
```

## Key Functions

### rbac_service.py

| Function | Purpose |
|----------|---------|
| ensure_rbac_tables() | Create RBAC tables |
| _bootstrap_initial_data() | Seed initial roles and permissions |
| load_user_roles() | Get user's roles |
| load_permissions_for_role_ids() | Get permissions for role IDs |
| resolve_user_permissions() | Get all permissions for user |
| has_permission() | Check if user has permission |
| build_permission_context() | Build permission context |

## Data Scope

### Organization-Based Filtering

- Users are associated with organizations
- Orders are scoped to organizations
- RBAC data scope service filters by user's default organization

### Key Files

| File | Purpose |
|------|---------|
| backend/services/rbac_service.py | Core RBAC logic |
| backend/services/rbac_data_scope_service.py | Data scope filtering |

## Frontend Permission Check

In `frontend/src/router/index.js`:

```javascript
if (to.meta.permission && !session.hasPermission(to.meta.permission)) {
  return { name: 'dashboard' }
}
```

In `frontend/src/store/session.js`:
- `hasPermission(permission)` method checks if user has permission
- Permissions loaded on session initialization

## Table Structure

### RBAC_角色 (Roles)

| Column | Type | Description |
|--------|------|-------------|
| 角色ID | NVARCHAR | Primary key |
| 角色名称 | NVARCHAR | Display name |
| 角色描述 | NVARCHAR | Description |

### RBAC_权限 (Permissions)

| Column | Type | Description |
|--------|------|-------------|
| 权限ID | NVARCHAR | Primary key |
| 权限名称 | NVARCHAR | Display name |
| 所属模块 | NVARCHAR | Module (admin/dashboard/order) |
| 权限代码 | NVARCHAR | Unique permission code |

### RBAC_角色权限 (Role-Permission)

| Column | Type | Description |
|--------|------|-------------|
| 角色ID | NVARCHAR | Foreign key to role |
| 权限ID | NVARCHAR | Foreign key to permission |

### RBAC_用户角色 (User-Role)

| Column | Type | Description |
|--------|------|-------------|
| 用户ID | NVARCHAR | User identifier |
| 角色ID | NVARCHAR | Role identifier |
| 组织ID | NVARCHAR | Organization scope |
