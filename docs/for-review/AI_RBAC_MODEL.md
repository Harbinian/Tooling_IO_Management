# AI Review: RBAC Model

## Overview

Role-Based Access Control (RBAC) system for the Tooling IO Management System.

## Roles

| Role ID | Role Name | Type | Description |
|---------|-----------|------|-------------|
| ROLE_SYS_ADMIN | 系统管理员 | system | Full system access |
| ROLE_TEAM_LEADER | 班组长 | business | Create orders, final confirm outbound |
| ROLE_KEEPER | 保管员 | business | Confirm items, reject, final confirm inbound |
| ROLE_PLANNER | 计划员 | business | Create and submit orders |
| ROLE_PRODUCTION_PREP | 生产准备工 | business | Execute transport operations |
| ROLE_AUDITOR | 审计员 | system | View logs and reports |

## Permissions

### Dashboard Permissions

| Permission Code | Description |
|----------------|-------------|
| dashboard:view | View dashboard |

### Tool Permissions

| Permission Code | Description |
|----------------|-------------|
| tool:search | Search tools |
| tool:view | View tool details |
| tool:location_view | View tool location |
| tool:status_update | Update tool status |

### Order Permissions

| Permission Code | Description |
|----------------|-------------|
| order:list | View order list |
| order:view | View order details |
| order:create | Create new order |
| order:submit | Submit order for approval |
| order:keeper_confirm | Confirm order items as keeper |
| order:final_confirm | Final confirmation |
| order:reject | Reject order |
| order:cancel | Cancel order |
| order:delete | Delete order |
| order:transport_execute | Execute transport operations |

### Notification Permissions

| Permission Code | Description |
|----------------|-------------|
| notification:view | View notifications |
| notification:create | Create notifications |
| notification:send_feishu | Send Feishu notifications |

### Admin Permissions

| Permission Code | Description |
|----------------|-------------|
| admin:user_manage | Manage users |
| admin:role_manage | Manage roles |

### Log Permissions

| Permission Code | Description |
|----------------|-------------|
| log:view | View system logs |

## Role-Permission Mapping

| Permission | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR | SYS_ADMIN |
|------------|-------------|--------|---------|-----------------|---------|-----------|
| dashboard:view | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| tool:search | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| tool:view | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| tool:location_view | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| tool:status_update | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| order:create | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ |
| order:list | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| order:view | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| order:submit | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ |
| order:keeper_confirm | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| order:final_confirm | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| order:cancel | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| order:delete | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| order:transport_execute | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ |
| notification:view | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| notification:create | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| notification:send_feishu | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| log:view | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |
| admin:user_manage | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| admin:role_manage | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

## Data Scope

| Role | Data Scope | Description |
|------|------------|-------------|
| TEAM_LEADER | SELF, ORG | Own orders + org orders |
| KEEPER | ORG, ASSIGNED | Org orders + assigned orders |
| PLANNER | ORG, ORG_AND_CHILDREN | Org + child org orders |
| PRODUCTION_PREP | SELF, ORG | Own transport + org tasks |
| AUDITOR | ALL | All data |
| SYS_ADMIN | ALL | All data |

## Key Files

| File | Purpose |
|------|---------|
| backend/services/rbac_service.py | Core RBAC logic |
| backend/services/rbac_data_scope_service.py | Data scope filtering |
| backend/database/schema/column_names.py | Column name constants |

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

### sys_role (Roles)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| role_id | NVARCHAR(64) | Role identifier |
| role_code | NVARCHAR(50) | Unique code |
| role_name | NVARCHAR(100) | Display name |
| role_type | NVARCHAR(20) | business/system |
| status | NVARCHAR(20) | active/disabled |

### sys_permission (Permissions)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| permission_code | NVARCHAR(100) | Unique permission identifier |
| permission_name | NVARCHAR(100) | Display name |
| resource_name | NVARCHAR(50) | Resource name |
| action_name | NVARCHAR(50) | Action name |

### sys_role_permission_rel (Role-Permission)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| role_id | NVARCHAR(64) | Role reference |
| permission_code | NVARCHAR(100) | Permission reference |

### sys_user_role_rel (User-Role)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| user_id | NVARCHAR(64) | User reference |
| role_id | NVARCHAR(64) | Role reference |
| is_primary | BIT | Is primary role |
| status | NVARCHAR(20) | active/disabled |

### sys_org (Organizations)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| org_id | NVARCHAR(64) | Organization identifier |
| org_name | NVARCHAR(100) | Display name |
| org_type | NVARCHAR(50) | company/warehouse/workshop/etc |
| parent_org_id | NVARCHAR(64) | Parent organization |
| status | NVARCHAR(20) | active/disabled |
