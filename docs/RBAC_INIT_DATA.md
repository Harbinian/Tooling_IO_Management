# RBAC Initial Data
Tooling IO Management System

---

# 1 Overview

This document provides the initial data required to bootstrap the RBAC system.

It inserts:

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

System roles:

- sys_admin
- auditor

SQL

    INSERT INTO sys_role (role_id, role_code, role_name, role_type)
    VALUES
    ('ROLE_TEAM_LEADER', 'team_leader', 'Team Leader', 'business'),
    ('ROLE_KEEPER', 'keeper', 'Keeper', 'business'),
    ('ROLE_PLANNER', 'planner', 'Planner', 'business'),
    ('ROLE_SYS_ADMIN', 'sys_admin', 'System Administrator', 'system'),
    ('ROLE_AUDITOR', 'auditor', 'Auditor', 'system')

---

# 3 Initial Permissions

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
    ('order:create', 'Create Order', 'order', 'create'),
    ('order:view', 'View Order', 'order', 'view'),
    ('order:list', 'List Orders', 'order', 'list'),
    ('order:submit', 'Submit Order', 'order', 'submit'),
    ('order:keeper_confirm', 'Keeper Confirm Order', 'order', 'keeper_confirm'),
    ('order:final_confirm', 'Final Confirm Order', 'order', 'final_confirm'),
    ('order:cancel', 'Cancel Order', 'order', 'cancel'),
    ('notification:view', 'View Notification', 'notification', 'view'),
    ('notification:create', 'Create Notification', 'notification', 'create'),
    ('notification:send_feishu', 'Send Feishu Notification', 'notification', 'send_feishu'),
    ('log:view', 'View System Log', 'log', 'view'),
    ('admin:user_manage', 'Manage Users', 'admin', 'user_manage'),
    ('admin:role_manage', 'Manage Roles', 'admin', 'role_manage')

---

# 4 Role Permission Mapping

This section assigns permissions to roles.

---

## Team Leader

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
    ('ROLE_TEAM_LEADER', 'notification:view')

---

## Keeper

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

## Planner

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

## System Administrator

Administrator has all permissions.

SQL

    INSERT INTO sys_role_permission_rel (role_id, permission_code)
    SELECT 'ROLE_SYS_ADMIN', permission_code
    FROM sys_permission

---

## Auditor

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

# 5 Role Data Scope

Defines which data each role can access.

Scope types:

ALL  
ORG  
ORG_AND_CHILDREN  
SELF  
ASSIGNED  

---

## Team Leader

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_TEAM_LEADER', 'SELF'),
    ('ROLE_TEAM_LEADER', 'ORG')

---

## Keeper

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_KEEPER', 'ORG'),
    ('ROLE_KEEPER', 'ASSIGNED')

---

## Planner

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_PLANNER', 'ORG'),
    ('ROLE_PLANNER', 'ORG_AND_CHILDREN')

---

## System Administrator

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_SYS_ADMIN', 'ALL')

---

## Auditor

SQL

    INSERT INTO sys_role_data_scope_rel (role_id, scope_type)
    VALUES
    ('ROLE_AUDITOR', 'ALL')

---

# End of Document