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

## 表: sys_user / Table: sys_user

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
- 注意：旧文档曾使用 `users` 表名，实际表名为 `sys_user`。/ Note: Old documentation used `users`, actual table name is `sys_user`.

---

# 5. 组织模型 / Organization Model

组织代表企业层级结构。

Organizations represent the enterprise hierarchy.

## 表: sys_org / Table: sys_org

| 字段 / Field | 描述 / Description |
|------|-------------|
| org_id | 主键 / Primary key |
| org_name | 组织名称 / Organization name |
| org_type | 组织类型 / Organization type |
| parent_org_id | 父组织 / Parent organization |
| status | 启用或禁用 / Active or disabled |

注意：旧文档曾使用 `organizations` 表名，实际表名为 `sys_org`。/ Note: Old documentation used `organizations`, actual table name is `sys_org`.

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
notification:send_feishu / 通知:发送飞书

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

# 13. 跨部门工作流设计规范 / Cross-Department Workflow Design

## 13.1 核心设计原则 / Core Design Principles

### 原则一：申请人全程可见 / Applicant Always Sees Full Workflow

**规则**：订单申请人始终可以查看自己创建的订单的完整流程，无论订单跨越多少个部门。

**实现**：申请人（`initiator_id`）始终具有对自己订单的访问权限（SELF 范围），不受组织边界限制。

```
申请人 ──创建──▶ 订单 ──提交──▶ 部门A保管员确认 ──部门B运输 ──▶ 完成
   │                                      │
   └──────────── 全程可见 ─────────────────┘
```

### 原则二：业务流是部门到部门 / Business Flow is Department-to-Department

**规则**：工作流的传递是基于组织（部门），而非基于角色。

**含义**：
- 当订单需要跨部门处理时，目标是目的部门的所有相关角色，而非特定个人
- 部门内的角色可以自动分配（如同部门的所有保管员都可以处理）
- 具体的执行角色由目的部门内部决定

```
部门A                           部门B
  │                               │
  │  订单流转到"物资保障部"         │
  │ ─────────────────────────────▶ │
  │                               │
  │                    部门内自动分配
  │                    (所有保管员可见)
  │                    (具体由谁处理由部门决定)
```

### 原则三：特定业务可配置自动分配 / Specific Business Auto-Assignment

**规则**：某些业务流程可以配置为自动分配到部门内的所有可执行角色。

**示例**：工装出入库业务
- 提交订单时，自动通知目的部门的所有保管员
- 任何保管员都可以确认订单
- 第一个确认的保管员被正式分配

**注意**：其它业务流程的自动分配规则需要和需求方确认后再实现。

---

## 13.2 数据范围与跨部门访问 / Data Scope & Cross-Department Access

### 标准数据范围类型 / Standard Data Scope Types

| 范围类型 | 代码 | 含义 |
|---------|------|------|
| 本人 | SELF | 访问用户自己创建的记录 |
| 组织 | ORG | 访问当前用户所在组织的记录 |
| 组织及子组织 | ORG_AND_CHILDREN | 访问组织及所有子组织的记录 |
| 被分配 | ASSIGNED | 访问被分配给自己的记录 |
| 全部 | ALL | 访问所有记录（仅管理员） |

### 跨部门访问控制矩阵 / Cross-Department Access Control Matrix

| 订单状态 | 申请人 | 同部门保管员 | 跨部门保管员 | 运输人 |
|---------|--------|-------------|-------------|--------|
| submitted | ✅ 可见 | ✅ 可见 | ✅ 可见（自动分配） | ❌ |
| keeper_confirmed | ✅ 可见 | ❌ | ✅ 可见（被分配的） | ❌ |
| transport_notified | ✅ 可见 | ❌ | ✅ 可见（被分配的） | ✅ 可见 |
| completed | ✅ 可见 | ❌ | ✅ 可见（被分配的） | ✅ 可见 |

---

## 13.3 工装出入库业务跨部门流程 / Tool IO Cross-Department Workflow

### 流程图 / Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         工装出入库跨部门协同流程                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  班组长 (部门A)                    保管员 (部门B)                 运输人      │
│  taidongxu                        hutingting                     transport   │
│  ORG_DEPT_005                     ORG_DEPT_001                              │
│       │                                │                               │      │
│       │  1. 创建订单                    │                               │      │
│       │───────────────────────────────▶│                               │      │
│       │                                │                               │      │
│       │  2. 提交订单                    │                               │      │
│       │  (自动分配给部门B所有保管员)      │                               │      │
│       │───────────────────────────────▶│  3. 确认订单                  │      │
│       │                                │──────────────────────────────▶│      │
│       │                                │                               │      │
│       │  4. 查看完整流程                │                               │      │
│       │  • 保管员: hutingting ✓        │                               │      │
│       │  • 运输人: xxx ✓              │                               │      │
│       │  • 当前状态: transport_notified│                               │      │
│       │◀──────────────────────────────│                               │      │
│       │                                │                               │      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 关键实现 / Key Implementation

#### 部门自动分配 / Department Auto-Assignment

当订单提交时：

```python
# submit_order 函数中的部门自动分配逻辑
def submit_order(order_no, payload, current_user):
    # ...
    # 查找订单目的部门的所有保管员
    from backend.services.rbac_data_scope_service import load_keeper_ids_for_org_ids
    order_org_id = order.get("org_id")
    all_keepers = load_keeper_ids_for_org_ids([order_org_id])

    # 向每个保管员发送通知
    for keeper_info in all_keepers:
        _emit_internal_notification(
            KEEPER_CONFIRM_REQUIRED,
            order=order,
            target_user_id=keeper_info["user_id"],
            target_role="keeper",
            metadata={"auto_assigned": True}  # 标记为部门自动分配
        )
```

#### 跨部门访问判断 / Cross-Department Access Logic

```python
def order_matches_scope(order, scope_context):
    # ...

    # 1. 申请人始终可以访问自己的订单（无论组织）
    if initiator_id == current_user_id:
        return True

    # 2. 任何保管员都可以查看 submitted 订单（部门自动分配）
    if is_keeper and order_status == "submitted":
        return True

    # 3. 被分配的保管员可以继续访问
    if is_keeper and keeper_id == current_user_id:
        return True

    # 4. 被分配的运输人可以访问
    if transport_user_id == current_user_id:
        return True

    # ...
```

---

## 13.4 开发新跨部门流程的检查清单 / Checklist for New Cross-Department Workflows

开发新的跨部门业务流时，必须确认以下设计要点：

### 必确认项 / Must Confirm

- [ ] 申请人的访问权限是否覆盖完整流程？
- [ ] 业务流的传递是基于"部门"还是"角色"？
- [ ] 是否需要自动分配到部门内的所有执行角色？
- [ ] 如果需要自动分配，分配规则是什么？
- [ ] 跨部门访问时的数据隔离如何保证？

### 标准实现 / Standard Implementation

| 场景 | 实现方式 |
|------|---------|
| 申请人查看自己创建的订单 | `initiator_id == current_user_id` |
| 部门内角色自动分配 | `load_keeper_ids_for_org_ids()` + 通知 |
| 跨部门角色确认 | `keeper_id == current_user_id` |
| 申请人查看完整流程 | 始终允许（通过 SELF 或 initator_id 检查） |

### 注意事项 / Notes

> ⚠️ **重要**：开发新的跨部门业务流程时，必须先和需求方确认自动分配规则。不同的业务流程可能有不同的分配逻辑，不能简单复用工装出入库的自动分配逻辑。

---

## 13.5 数据库字段要求 / Database Field Requirements

跨部门工作流需要以下关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| initiator_id | 用户ID | 申请人ID，用于申请人访问控制 |
| keeper_id | 用户ID | 保管员ID，用于确认后访问控制 |
| transport_assignee_id | 用户ID | 运输人ID，用于运输阶段访问控制 |
| org_id | 组织ID | 订单所属部门，用于部门级访问控制 |

---

# 14. 实施阶段 / Implementation Phases

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

# 15. 与认证的关系 / Relationship with Authentication

认证确定：/ Authentication determines:

用户是谁。/ Who the user is.

RBAC 决定：/ RBAC determines:

用户可以做什么。/ What the user can do.

组织结构决定：/ Organization structure determines:

用户可以访问哪些数据。/ Which data the user can access.

它们共同构成完整的访问控制框架。

Together they form the complete access control framework.

---

# 16. 未来改进 / Future Improvements

未来改进可能包括：/ Future improvements may include:

- 飞书 SSO 集成 / Feishu SSO integration
- 自动组织同步 / Automatic organization synchronization
- 权限管理界面 / Permission management UI
- 扩展审计日志 / Expanded audit logging
- 企业级身份联邦 / Enterprise-level identity federation

---

# 文档结束 / End of Document
