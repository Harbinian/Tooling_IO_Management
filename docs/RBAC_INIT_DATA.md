# RBAC Initial Data
Tooling IO Management System

---

# 1 Overview

This document provides the initial data required to bootstrap the RBAC system.

It inserts:

- default organizations
- default roles
- default permissions
- role-permission mappings
- role data scopes

This script should be executed **after the RBAC tables are created**.

Execution order:

1. RBAC_DATABASE_SCHEMA.md
2. RBAC_INIT_DATA.md

---

# 2 Initial Roles

Default roles used by the system.

Roles include both business roles and system roles.

Business roles:

- team_leader
- keeper
- planner
- production_prep_worker

System roles:

- sys_admin
- auditor

SQL

    INSERT INTO sys_role (role_id, role_code, role_name, role_type)
    VALUES
    ('ROLE_TEAM_LEADER', 'team_leader', '班组长', 'business'),
    ('ROLE_KEEPER', 'keeper', '保管员', 'business'),
    ('ROLE_PLANNER', 'planner', '计划员', 'business'),
    ('ROLE_PRODUCTION_PREP', 'production_prep_worker', '生产准备工', 'business'),
    ('ROLE_SYS_ADMIN', 'sys_admin', '系统管理员', 'system'),
    ('ROLE_AUDITOR', 'auditor', '审计员', 'system')

---

# 3 Initial Organizations

Default organizations for the system.

Organization structure:

```
Company
├── 物资保障部 (Material Support Department)
├── 项目管理部 (Project Management Department)
├── 质量管理部 (Quality Management Department)
└── 复材车间 (Composite Materials Workshop)
```

SQL

    INSERT INTO sys_org (org_id, org_name, org_code, org_type, parent_org_id, sort_no, status, created_at, created_by)
    VALUES
    ('ORG_COMPANY', '昌兴复材', 'TOOL_MFG', 'company', NULL, 1, 'active', SYSDATETIME(), 'bootstrap'),
    ('ORG_MATERIAL', '物资保障部', 'MATERIAL', 'warehouse', 'ORG_COMPANY', 10, 'active', SYSDATETIME(), 'bootstrap'),
    ('ORG_PROJECT', '项目管理部', 'PROJECT', 'project_group', 'ORG_COMPANY', 20, 'active', SYSDATETIME(), 'bootstrap'),
    ('ORG_QUALITY', '质量管理部', 'QUALITY', 'company', 'ORG_COMPANY', 30, 'active', SYSDATETIME(), 'bootstrap'),
    ('ORG_COMPOSITE', '复材车间', 'COMPOSITE', 'workshop', 'ORG_COMPANY', 40, 'active', SYSDATETIME(), 'bootstrap');

Organization descriptions:

| org_id | org_name | org_type | Description |
|--------|----------|----------|-------------|
| ORG_COMPANY | 昌兴复材 | company | Root company |
| ORG_MATERIAL | 物资保障部 | warehouse | Material support & warehousing |
| ORG_PROJECT | 项目管理部 | project_group | Project management |
| ORG_QUALITY | 质量管理部 | company | Quality management |
| ORG_COMPOSITE | 复材车间 | workshop | Composite materials workshop |

---

# 4 Initial Permissions

Permission naming rule:

resource:action

Examples:

dashboard:view  
tool:search  
order:create  

SQL

    INSERT INTO sys_permission (permission_code, permission_name, resource_name, action_name)
    VALUES
    ('dashboard:view', 'View Dashboard', 'dashboard', 'view'),
    ('tool:search', 'Search Tools', 'tool', 'search'),
    ('tool:view', 'View Tool', 'tool', 'view'),
    ('tool:location_view', 'View Tool Location', 'tool', 'location_view'),
    ('tool:status_update', 'Update Tool Status', 'tool', 'status_update'),
    ('order:create', 'Create Order', 'order', 'create'),
    ('order:view', 'View Order', 'order', 'view'),
    ('order:list', 'List Orders', 'order', 'list'),
    ('order:submit', 'Submit Order', 'order', 'submit'),
    ('order:keeper_confirm', 'Keeper Confirm Order', 'order', 'keeper_confirm'),
    ('order:final_confirm', 'Final Confirm Order', 'order', 'final_confirm'),
    ('order:cancel', 'Cancel Order', 'order', 'cancel'),
    ('order:delete', 'Delete Order', 'order', 'delete'),
    ('order:transport_execute', 'Execute Transport', 'order', 'transport_execute'),
    ('notification:view', 'View Notification', 'notification', 'view'),
    ('notification:create', 'Create Notification', 'notification', 'create'),
    ('notification:send_feishu', 'Send Feishu Notification', 'notification', 'send_feishu'),
    ('log:view', 'View System Log', 'log', 'view'),
    ('admin:user_manage', 'Manage Users', 'admin', 'user_manage'),
    ('admin:role_manage', 'Manage Roles', 'admin', 'role_manage')

---

# 5 Role Permission Mapping

This section assigns permissions to roles.

---

## 班组长 (Team Leader)

Permissions

dashboard:view
tool:search
tool:view
order:create
order:view
order:list
order:submit
order:final_confirm
notification:view
notification:create

SQL

    INSERT INTO sys_role_permission_rel (role_id, permission_code)
    VALUES
    ('ROLE_TEAM_LEADER', 'dashboard:view'),
    ('ROLE_TEAM_LEADER', 'tool:search'),
    ('ROLE_TEAM_LEADER', 'tool:view'),
    ('ROLE_TEAM_LEADER', 'order:create'),
    ('ROLE_TEAM_LEADER', 'order:view'),
    ('ROLE_TEAM_LEADER', 'order:list'),
    ('ROLE_TEAM_LEADER', 'order:submit'),
    ('ROLE_TEAM_LEADER', 'order:final_confirm'),
    ('ROLE_TEAM_LEADER', 'notification:view'),
    ('ROLE_TEAM_LEADER', 'notification:create')

---

## 保管员 (Keeper)

Permissions

dashboard:view  
tool:search  
tool:view  
tool:location_view  
order:view  
order:list  
order:keeper_confirm  
order:final_confirm  
notification:view  
notification:create  
notification:send_feishu  
log:view  

SQL

    INSERT INTO sys_role_permission_rel (role_id, permission_code)
    VALUES
    ('ROLE_KEEPER', 'dashboard:view'),
    ('ROLE_KEEPER', 'tool:search'),
    ('ROLE_KEEPER', 'tool:view'),
    ('ROLE_KEEPER', 'tool:location_view'),
    ('ROLE_KEEPER', 'order:view'),
    ('ROLE_KEEPER', 'order:list'),
    ('ROLE_KEEPER', 'order:keeper_confirm'),
    ('ROLE_KEEPER', 'order:final_confirm'),
    ('ROLE_KEEPER', 'notification:view'),
    ('ROLE_KEEPER', 'notification:create'),
    ('ROLE_KEEPER', 'notification:send_feishu'),
    ('ROLE_KEEPER', 'log:view')

---

## 计划员 (Planner)

Permissions

dashboard:view  
tool:search  
tool:view  
order:create  
order:view  
order:list  
order:submit  
notification:view  

SQL

    INSERT INTO sys_role_permission_rel (role_id, permission_code)
    VALUES
    ('ROLE_PLANNER', 'dashboard:view'),
    ('ROLE_PLANNER', 'tool:search'),
    ('ROLE_PLANNER', 'tool:view'),
    ('ROLE_PLANNER', 'order:create'),
    ('ROLE_PLANNER', 'order:view'),
    ('ROLE_PLANNER', 'order:list'),
    ('ROLE_PLANNER', 'order:submit'),
    ('ROLE_PLANNER', 'notification:view')

---

## 生产准备工 (Production Prep Worker)

Production preparation workers are responsible for transporting tooling between locations. They belong to the Material Support Department (物资保障部).

Permissions

dashboard:view
tool:search
tool:view
tool:location_view
order:transport_execute

SQL

    INSERT INTO sys_role_permission_rel (role_id, permission_code)
    VALUES
    ('ROLE_PRODUCTION_PREP', 'dashboard:view'),
    ('ROLE_PRODUCTION_PREP', 'tool:search'),
    ('ROLE_PRODUCTION_PREP', 'tool:view'),
    ('ROLE_PRODUCTION_PREP', 'tool:location_view'),
    ('ROLE_PRODUCTION_PREP', 'order:transport_execute')

---

## 系统管理员 (System Administrator)

Administrator has all permissions.

SQL

    INSERT INTO sys_role_permission_rel (role_id, permission_code)
    SELECT 'ROLE_SYS_ADMIN', permission_code
    FROM sys_permission

---

## 审计员 (Auditor)

Permissions

dashboard:view  
order:view  
order:list  
notification:view  
log:view  

SQL

    INSERT INTO sys_role_permission_rel (role_id, permission_code)
    VALUES
    ('ROLE_AUDITOR', 'dashboard:view'),
    ('ROLE_AUDITOR', 'order:view'),
    ('ROLE_AUDITOR', 'order:list'),
    ('ROLE_AUDITOR', 'notification:view'),
    ('ROLE_AUDITOR', 'log:view')

---

# 6 Role Data Scope

Defines which data each role can access.

Scope types:

ALL  
ORG  
ORG_AND_CHILDREN  
SELF  
ASSIGNED  

---

## 班组长 (Team Leader)

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_TEAM_LEADER', 'SELF'),
    ('ROLE_TEAM_LEADER', 'ORG')

---

## 保管员 (Keeper)

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_KEEPER', 'ORG'),
    ('ROLE_KEEPER', 'ASSIGNED')

---

## 计划员 (Planner)

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_PLANNER', 'ORG'),
    ('ROLE_PLANNER', 'ORG_AND_CHILDREN')

---

## 生产准备工 (Production Prep Worker)

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_PRODUCTION_PREP', 'SELF'),
    ('ROLE_PRODUCTION_PREP', 'ORG')

---

## 系统管理员 (System Administrator)

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_SYS_ADMIN', 'ALL')

---

## 审计员 (Auditor)

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_AUDITOR', 'ALL')

---

# 7 Cross-Organization Workflow

This section documents the cross-organization order processing workflow.

## 7.1 Workflow Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    跨组织协同流程                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  班组长创建订单                                                            │
│  (ORG_DEPT_005)                                                          │
│       │                                                                  │
│       ▼                                                                  │
│  提交订单 ──▶ 部门自动分配: 通知所有保管员                                    │
│       │                    (ORG_DEPT_001 所有 keeper)                     │
│       │                                                                  │
│       ▼                                                                  │
│  保管员(hutingting) ──▶ 确认订单 ──▶ 指派运输人                            │
│  (ORG_DEPT_001)           │                  │                            │
│       │                   │                  ▼                            │
│       │                   │            运输人确认 ──▶ 完成                 │
│       │                   │            (ORG_DEPT_XXX)                   │
│       │                   ▼                                             │
│       └─────> 班组长可查看:                                              │
│               • 保管员确认状态                                            │
│               • 运输人指派                                                │
│               • 运输完成状态                                               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 7.2 Data Access Rules by Role

| 角色 | 可访问的订单 | 说明 |
|------|-------------|------|
| 班组长 | 自己创建的订单 (SELF) + 同组织订单 (ORG) | 始终可查看自己订单的完整流程 |
| 保管员 | 同组织待确认订单 (submitted/partially_confirmed) + 被分配订单 (keeper_id) | 可跨组织确认订单 |
| 运输人 | 被分配的运输订单 (transport_assignee_id) | 只能看到分配给自己的订单 |

## 7.3 Key Implementation Details

### 部门自动分配 (Department Auto-Assignment)

When an order is submitted:
1. System finds ALL keepers in the order's organization
2. Sends `KEEPER_CONFIRM_REQUIRED` notification to each keeper
3. Any keeper in the org can confirm the order

### 跨组织确认 (Cross-Organization Confirmation)

When a keeper confirms an order:
1. Keeper's `keeper_id` is set to the confirming keeper's user_id
2. After confirmation, only this specific keeper continues to have access
3. Keeper can then assign a transport person

### 运输指派 (Transport Assignment)

When a keeper assigns transport:
1. `transport_assignee_id` is set to the transport person's user_id
2. Transport person can now see the order
3. Transport person can execute transport workflow

### 班组长监督 (Team Leader Monitoring)

Team leader always sees their own orders regardless of:
- Current order status
- Which keeper confirmed
- Which transport person was assigned
- Organization of the keeper/transport person

## 7.4 Status-Based Visibility Matrix

| 订单状态 | 班组长 | 同组织保管员 | 分配的保管员 | 分配的运输人 |
|---------|--------|-------------|-------------|-------------|
| submitted | ✅ 看自己的 | ✅ 可见 | N/A | N/A |
| keeper_confirmed | ✅ 看自己的 | ❌ | ✅ | ❌ |
| transport_notified | ✅ 看自己的 | ❌ | ✅ | ✅ |
| completed | ✅ 看自己的 | ❌ | ✅ | ✅ |

# End of Document