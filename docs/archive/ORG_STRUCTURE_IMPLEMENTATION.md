# 组织结构模块实现 / Organization Structure Implementation

## 概述 / Overview

本次实现补充了第一版组织结构模块，用于支撑:

- `sys_org` 组织主数据维护
- 组织树查询
- 用户默认组织与当前组织上下文解析
- 角色分配中的组织上下文解释
- 后续 RBAC data scope 扩展

## Schema 使用 / Schema Usage

组织结构严格使用既有 RBAC schema 中的:

- `sys_org`
- `sys_user.default_org_id`
- `sys_user_role_rel.org_id`

未引入第二套组织模型。

## 后端实现 / Backend

组织服务位于:

- `backend/services/org_service.py`

核心能力:

- `ensure_org_tables()`
- `list_organizations()`
- `get_organization()`
- `get_org_tree()`
- `create_organization()`
- `update_organization()`
- `get_descendant_org_ids()`
- `get_role_assignments_with_org_context()`
- `resolve_user_org_context()`

## API 列表 / API List

- `GET /api/orgs`
- `GET /api/orgs/tree`
- `GET /api/orgs/{org_id}`
- `POST /api/orgs`
- `PUT /api/orgs/{org_id}`

权限约定:

- 查询接口使用 `dashboard:view`
- 创建/更新接口使用 `admin:user_manage`

## 组织树逻辑 / Organization Tree Logic

树构建基于 `parent_org_id`。

支持类型:

- `company`
- `factory`
- `workshop`
- `team`
- `warehouse`
- `project_group`

返回结构包含:

- 组织基础字段
- `children`

## 用户-组织关系 / User-Organization Relationship

当前用户组织上下文来源:

1. `sys_user.default_org_id`
2. `sys_user_role_rel.org_id`

认证成功后，当前用户上下文会附带:

- `default_org`
- `current_org`
- `role_orgs`

`current_org` 优先取首个带组织上下文的有效角色，否则回退到 `default_org`。

## 角色-组织上下文 / Role-Organization Context

同一用户可以在不同组织拥有不同角色。

服务通过 `get_role_assignments_with_org_context()` 解析:

- `role_id`
- `role_code`
- `role_name`
- `org_id`
- `org_name`
- `org_type`
- `org_status`

这为后续按组织解析权限与数据范围提供基础。

## Data Scope 预备 / Future Data Scope Notes

本任务未直接实现业务数据过滤，但已提供:

- 当前用户组织解析
- 组织树后代解析
- 角色关联组织上下文

后续 `ORG` / `ORG_AND_CHILDREN` scope 可直接复用这些能力。

## 校验规则 / Validation Rules

已实现:

- `org_id` 唯一
- `parent_org_id` 存在性校验
- 禁止 self-parent
- 禁止简单层级环
- disabled 组织仍可查询

## 初始化指导 / Initialization Guidance

可使用以下示例 SQL 初始化最小组织树:

```sql
INSERT INTO sys_org (org_id, org_name, org_code, org_type, parent_org_id, sort_no, status, created_at, created_by)
VALUES
('ORG_COMPANY', '昌兴复材', 'TOOL_MFG', 'company', NULL, 1, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_MATERIAL', '物资保障部', 'MATERIAL', 'warehouse', 'ORG_COMPANY', 10, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_PROJECT', '项目管理部', 'PROJECT', 'project_group', 'ORG_COMPANY', 20, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_QUALITY', '质量管理部', 'QUALITY', 'company', 'ORG_COMPANY', 30, 'active', SYSDATETIME(), 'bootstrap'),
('ORG_COMPOSITE', '复材车间', 'COMPOSITE', 'workshop', 'ORG_COMPANY', 40, 'active', SYSDATETIME(), 'bootstrap');
```

之后可通过:

- `sys_user.default_org_id`
- `sys_user_role_rel.org_id`

把用户与组织上下文绑定。
