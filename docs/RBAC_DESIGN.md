# RBAC 设计规范
# RBAC Design Specification
工装出入库管理系统

---

# 1. 概述 / Overview

本文档定义了工装出入库管理系统的基于角色的访问控制 (RBAC) 模型。

This document defines the Role-Based Access Control (RBAC) model used by the Tooling IO Management System.

RBAC 模型回答三个基本问题：

The RBAC model answers three fundamental questions:

1. 用户是谁？/ Who is the user?
2. 用户可以执行什么操作？/ What actions can the user perform?
3. 用户可以访问什么数据范围？/ What data scope can the user access?

系统结合了以下要素：/ The system combines:

- 用户身份 / User identity
- 角色 / Roles
- 权限 / Permissions
- 数据范围 / Data scope

这实现了操作级授权和数据级隔离。

This allows both operation-level authorization and data-level isolation.

---

# 2. 设计原则 / Design Principles

## 基于角色的授权 / Role-Based Authorization

权限分配给角色，而不是直接分配给用户。

Permissions are assigned to roles rather than directly to users.

用户通过角色分配获得权限。

Users obtain permissions through role assignments.

---

## 身份与授权分离 / Separation of Identity and Authorization

身份验证确定用户身份。

Authentication determines the user identity.

授权决定用户可以做什么。

Authorization determines what the user is allowed to do.

---

## 最小权限原则 / Least Privilege

用户仅获得其职责所需的权限。

Users receive only the permissions required for their responsibilities.

---

## 数据范围控制 / Data Scope Control

权限控制操作。

Permissions control actions.

数据范围控制用户可以访问哪些数据。

Data scope controls which data the user is allowed to access.

---

# 3. 核心模型 / Core Model

RBAC 架构包含四个核心实体：

The RBAC architecture includes four core entities:

- 用户 / User
- 组织 / Organization
- 角色 / Role
- 权限 / Permission

此外，数据范围层定义可访问记录的范围。

Additionally, a data scope layer defines the range of accessible records.

---

# 4. 用户模型 / User Model

用户代表已认证的系统身份。

Users represent authenticated system identities.

## 表: users / Table: users

| 字段 / Field | 描述 / Description |
|------|-------------|
| user_id | 主键 / Primary key |
| login_name | 登录用户名 / Login username |
| display_name | 显示名称 / Display name |
| password_hash | 密码哈希 / Password hash |
| status | 启用或禁用 / Active or disabled |
| default_org_id | 默认组织 / Default organization |
| created_at | 创建时间戳 / Creation timestamp |
| updated_at | 最后更新时间戳 / Last update timestamp |

说明：/ Notes:

- login_name 用于身份验证。/ login_name is used during authentication.
- display_name 显示在界面和操作日志中。/ display_name appears in UI and operation logs.

---

# 5. 组织模型 / Organization Model

组织代表企业层级结构。

Organizations represent the enterprise hierarchy.

## 表: organizations / Table: organizations

| 字段 / Field | 描述 / Description |
|------|-------------|
| org_id | 主键 / Primary key |
| org_name | 组织名称 / Organization name |
| org_type | 组织类型 / Organization type |
| parent_org_id | 父组织 / Parent organization |
| status | 启用或禁用 / Active or disabled |

组织类型示例：/ Example organization types:

- company / 公司
- factory / 工厂
- workshop / 车间
- team / 班组
- warehouse / 仓库
- project_group / 项目组

层级结构示例：/ Example hierarchy:

公司 / Company
└ 工厂 / Factory
  └ 车间 / Workshop
    └ 班组 / Team

---

# 6. 角色模型 / Role Model

角色代表权限集合。

Roles represent sets of permissions.

## 表: roles / Table: roles

| 字段 / Field | 描述 / Description |
|------|-------------|
| role_id | 主键 / Primary key |
| role_code | 唯一标识符 / Unique identifier |
| role_name | 显示名称 / Display name |
| role_type | 业务角色或系统角色 / Business or system role |
| status | 启用或禁用 / Active or disabled |

---

# 7. 权限模型 / Permission Model

权限代表系统中的原子操作。

Permissions represent atomic actions within the system.

命名规范：/ Naming convention:

资源:操作 / resource:action

示例：/ Examples:

order:create / 订单:创建
order:view / 订单:查看
order:list / 订单:列表
order:submit / 订单:提交
order:keeper_confirm / 订单:保管员确认
order:final_confirm / 订单:最终确认
order:cancel / 订单:取消

tool:search / 工装:搜索
tool:view / 工装:查看
tool:location_view / 工装:库位查看

notification:view / 通知:查看
notification:create / 通知:创建
notification:send_feishu / 通知:发送飞书

dashboard:view / 仪表盘:查看

log:view / 日志:查看

admin:user_manage / 管理员:用户管理
admin:role_manage / 管理员:角色管理

## 表: permissions / Table: permissions

| 字段 / Field | 描述 / Description |
|------|-------------|
| permission_code | 唯一权限标识符 / Unique permission identifier |
| permission_name | 显示名称 / Display name |
| resource | 资源名称 / Resource name |
| action | 允许的操作 / Allowed action |

---

# 8. 数据范围模型 / Data Scope Model

权限控制操作。

Permissions control actions.

数据范围决定用户可以访问哪些记录。

Data scope determines which records a user can access.

支持的数据范围类型：/ Supported data scope types:

| 范围 / Scope | 含义 / Meaning |
|------|--------|
| ALL | 访问所有记录 / Access to all records |
| ORG | 访问当前组织 / Access to current organization |
| ORG_AND_CHILDREN | 访问组织及子组织 / Access to organization and sub-organizations |
| SELF | 访问用户本人记录 / Access to user-owned records |
| ASSIGNED | 访问被分配的记录 / Access to assigned records |
| CUSTOM | 自定义范围 / Custom-defined scope |

---

# 9. 关系表 / Relationship Tables

## 用户-角色关系 / User-Role Relation

表: user_role_rel / Table: user_role_rel

| 字段 / Field | 描述 / Description |
|------|-------------|
| id | 主键 / Primary key |
| user_id | 用户引用 / User reference |
| role_id | 角色引用 / Role reference |
| org_id | 组织引用 / Organization reference |
| is_primary | 主角色标志 / Primary role flag |

用户可以在不同组织中拥有多个角色。

A user may have multiple roles in different organizations.

---

## 角色-权限关系 / Role-Permission Relation

表: role_permission_rel / Table: role_permission_rel

| 字段 / Field | 描述 / Description |
|------|-------------|
| id | 主键 / Primary key |
| role_id | 角色引用 / Role reference |
| permission_code | 权限引用 / Permission reference |

---

## 角色数据范围关系 / Role Data Scope Relation

表: role_data_scope_rel / Table: role_data_scope_rel

| 字段 / Field | 描述 / Description |
|------|-------------|
| id | 主键 / Primary key |
| role_id | 角色引用 / Role reference |
| scope_type | 数据范围类型 / Data scope type |
| scope_value | 可选范围定义 / Optional scope definition |

---

# 10. 默认业务角色 / Default Business Roles

## 班组长 / Team Leader

职责：/ Responsibilities:

- 创建工装使用订单 / Create tool usage orders
- 提交订单 / Submit orders
- 确认出库完成 / Confirm outbound completion

权限：/ Permissions:

dashboard:view / 仪表盘:查看
tool:search / 工装:搜索
tool:view / 工装:查看
order:create / 订单:创建
order:view / 订单:查看
order:list / 订单:列表
order:submit / 订单:提交
order:final_confirm / 订单:最终确认

数据范围：/ Data scope:

SELF 或 ORG / SELF or ORG

---

## 保管员 / Keeper

职责：/ Responsibilities:

- 管理工装库存 / Manage tool storage
- 确认入库和出库操作 / Confirm inbound and outbound operations

权限：/ Permissions:

dashboard:view / 仪表盘:查看
tool:search / 工装:搜索
tool:view / 工装:查看
tool:location_view / 工装:库位查看
order:view / 订单:查看
order:list / 订单:列表
order:keeper_confirm / 订单:保管员确认
order:final_confirm / 订单:最终确认
notification:view / 通知:查看

数据范围：/ Data scope:

ORG 或 ASSIGNED / ORG or ASSIGNED

---

## 计划员 / Planner

职责：/ Responsibilities:

- 为项目规划创建订单 / Create orders for project planning

权限：/ Permissions:

dashboard:view / 仪表盘:查看
tool:search / 工装:搜索
tool:view / 工装:查看
order:create / 订单:创建
order:view / 订单:查看
order:list / 订单:列表
order:submit / 订单:提交

数据范围：/ Data scope:

ORG 或 ORG_AND_CHILDREN / ORG or ORG_AND_CHILDREN

---

## 系统管理员 / System Administrator

职责：/ Responsibilities:

- 管理用户 / Manage users
- 管理角色 / Manage roles
- 维护系统 / Maintain the system

权限：/ Permissions:

ALL / 所有权限 / All permissions

数据范围：/ Data scope:

ALL / 所有数据 / ALL

---

## 审计员 / Auditor

职责：/ Responsibilities:

- 审查系统活动 / Review system activity
- 检查操作日志 / Inspect operation logs

权限：/ Permissions:

order:view / 订单:查看
order:list / 订单:列表
log:view / 日志:查看
notification:view / 通知:查看

数据范围：/ Data scope:

ALL 或 ORG_AND_CHILDREN / ALL or ORG_AND_CHILDREN

---

# 11. 权限执行层 / Permission Enforcement Layers

RBAC 在三个层面执行。/ RBAC is enforced at three layers.

## 前端层 / Frontend Layer

控制界面可见性。/ Controls UI visibility.

示例：/ Examples:

- 如果缺少权限，隐藏"创建订单"按钮。/ Hide "Create Order" button if permission is missing.
- 如果没有保管员权限，隐藏保管员工作区。/ Hide Keeper workspace if keeper permission is absent.

前端检查改善可用性，但不是安全边界。/ Frontend checks improve usability but are not security boundaries.

---

## API 层 / API Layer

控制对后端端点的访问。/ Controls access to backend endpoints.

示例：/ Example:

POST /api/tool-io-orders
必需权限: order:create / Required permission: order:create

POST /api/tool-io-orders/{id}/keeper-confirm
必需权限: order:keeper_confirm / Required permission: order:keeper_confirm

POST /api/notifications/{id}/send-feishu
必需权限: notification:send_feishu / Required permission: notification:send_feishu

---

## 数据层 / Data Layer

控制用户可以查询或修改哪些记录。/ Controls which records users may query or modify.

示例：/ Examples:

班组长：/ Team leader:

- 查看自己的订单 / View own orders
- 查看组织订单 / View organization orders

保管员：/ Keeper:

- 查看分配的仓库订单 / View assigned warehouse orders

管理员：/ Administrator:

- 查看所有记录 / View all records

---

# 12. 权限矩阵 / Permission Matrix

| 功能 / Capability | 班组长 / Team Leader | 保管员 / Keeper | 计划员 / Planner | 管理员 / Admin | 审计员 / Auditor |
|-------------|------------|--------|--------|-------|---------|
| 仪表盘查看 / Dashboard View | ✓ | ✓ | ✓ | ✓ | ✓ |
| 工装搜索 / Tool Search | ✓ | ✓ | ✓ | ✓ | ✓ |
| 创建订单 / Create Order | ✓ | | ✓ | ✓ | |
| 提交订单 / Submit Order | ✓ | | ✓ | ✓ | |
| 订单列表 / Order List | ✓ | ✓ | ✓ | ✓ | ✓ |
| 订单详情 / Order Detail | ✓ | ✓ | ✓ | ✓ | ✓ |
| 保管员确认 / Keeper Confirmation | | ✓ | | ✓ | |
| 最终确认 / Final Confirmation | ✓ | ✓ | | ✓ | |
| 通知查看 / Notification View | ✓ | ✓ | ✓ | ✓ | ✓ |
| 发送飞书 / Send Feishu | | ✓ | | ✓ | |
| 查看日志 / View Logs | | ✓ | | ✓ | ✓ |
| 用户管理 / User Management | | | | ✓ | |

---

# 13. 实施阶段 / Implementation Phases

## 第一阶段 / Phase 1

初始 RBAC 实现：/ Initial RBAC implementation:

- 用户表 / User table
- 角色表 / Role table
- 用户-角色关系 / User-role relation
- 权限枚举 / Permission enumeration
- 登录认证 / Login authentication
- API 级权限检查 / API-level permission checks

数据范围简化为：/ Data scope simplified to:

SELF / 本人数据
ORG / 组织数据
ALL / 所有数据

---

## 第二阶段 / Phase 2

高级 RBAC 能力：/ Advanced RBAC capabilities:

- 组织层级 / Organization hierarchy
- 自定义数据范围 / Custom data scope
- 角色管理界面 / Role management interface
- 用户管理界面 / User management interface
- 权限分配界面 / Permission assignment UI

---

# 14. 与认证的关系 / Relationship with Authentication

认证确定：/ Authentication determines:

用户是谁。/ Who the user is.

RBAC 决定：/ RBAC determines:

用户可以做什么。/ What the user can do.

组织结构决定：/ Organization structure determines:

用户可以访问哪些数据。/ Which data the user can access.

它们共同构成完整的访问控制框架。

Together they form the complete access control framework.

---

# 15. 未来改进 / Future Improvements

未来改进可能包括：/ Future improvements may include:

- 飞书 SSO 集成 / Feishu SSO integration
- 自动组织同步 / Automatic organization synchronization
- 权限管理界面 / Permission management UI
- 扩展审计日志 / Expanded audit logging
- 企业级身份联邦 / Enterprise-level identity federation

---

# 文档结束 / End of Document
