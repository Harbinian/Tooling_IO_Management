# RBAC 权限矩阵 / RBAC Permission Matrix

> **最后更新**: 2026-03-27
> **维护者**: 每次新增 API 权限注解时必须同步更新此文档
> **权威来源**: `docs/RBAC_INIT_DATA.md`

---

## 角色定义 / Role Definitions

| 角色 ID | 角色名称 | 类型 | 说明 |
|---------|---------|------|------|
| `ROLE_SYS_ADMIN` | 系统管理员 | system | 系统管理员，拥有所有权限 |
| `ROLE_TEAM_LEADER` | 班组长 | business | 创建订单、出库最终确认 |
| `ROLE_KEEPER` | 保管员 | business | 确认明细、拒绝订单、入库最终确认 |
| `ROLE_PLANNER` | 计划员 | business | 计划员，可创建和提交工装订单 |
| `ROLE_PRODUCTION_PREP` | 生产准备工 | business | 运输工装，负责运输执行 |
| `ROLE_AUDITOR` | 审计员 | system | 审计员，查看日志和报表 |

---

## 权限清单 / Permission Catalog

**权威来源**: `docs/RBAC_INIT_DATA.md` 第4节

| 权限代码 | 权限名称 | 资源 | 操作 |
|---------|---------|------|------|
| `dashboard:view` | View Dashboard | dashboard | view |
| `tool:search` | Search Tools | tool | search |
| `tool:view` | View Tool Details | tool | view |
| `tool:location_view` | View Tool Location | tool | location_view |
| `order:create` | Create Order | order | create |
| `order:view` | View Order | order | view |
| `order:list` | List Orders | order | list |
| `order:submit` | Submit Order | order | submit |
| `order:keeper_confirm` | Keeper Confirm | order | keeper_confirm |
| `order:final_confirm` | Final Confirm | order | final_confirm |
| `order:cancel` | Cancel Order | order | cancel |
| `order:delete` | Delete Order | order | delete |
| `order:transport_execute` | Execute Transport | order | transport_execute |
| `notification:view` | View Notification | notification | view |
| `notification:create` | Create Notification | notification | create |
| `notification:send_feishu` | Send Feishu | notification | send_feishu |
| `log:view` | View System Log | log | view |
| `admin:user_manage` | Manage Users | admin | user_manage |
| `admin:role_manage` | Manage Roles | admin | role_manage |

---

## 角色-权限矩阵 / Role-Permission Matrix

**权威来源**: `docs/RBAC_INIT_DATA.md` 第5节

| 权限 | SYS_ADMIN | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|------|-----------|-------------|--------|---------|-----------------|---------|
| `dashboard:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `tool:search` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `tool:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `tool:location_view` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `order:create` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `order:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `order:list` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `order:submit` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `order:keeper_confirm` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `order:final_confirm` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `order:cancel` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `order:delete` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `order:transport_execute` | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `notification:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `notification:create` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `notification:send_feishu` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `log:view` | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| `admin:user_manage` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `admin:role_manage` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 角色数据范围 / Role Data Scope

**权威来源**: `docs/RBAC_INIT_DATA.md` 第6节

| 角色 | 数据范围 | 说明 |
|------|---------|------|
| TEAM_LEADER | SELF, ORG | 可访问自己创建和本组织的订单 |
| KEEPER | ORG, ASSIGNED | 可访问本组织及分配的订单 |
| PLANNER | ORG, ORG_AND_CHILDREN | 可访问本组织及子组织的订单 |
| PRODUCTION_PREP | SELF, ORG | 可访问自己负责和本组织的运输任务 |
| AUDITOR | ALL | 可访问所有数据 |
| SYS_ADMIN | ALL | 可访问所有数据 |

---

## API 端点权限映射 / API Endpoint Permission Map

### 订单路由 (order_routes.py)

| API 端点 | 方法 | 所需权限 | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|---------|------|---------|-------------|--------|---------|-----------------|---------|
| `/api/tool-io-orders` | GET | `order:list` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `/api/tool-io-orders` | POST | `order:create` | ✅ | ❌ | ✅ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>` | GET | `order:view` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `/api/tool-io-orders/<order_no>/submit` | POST | `order:submit` | ✅ | ❌ | ✅ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/keeper-confirm` | POST | `order:keeper_confirm` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/final-confirm` | POST | `order:final_confirm` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/final-confirm-availability` | GET | `order:view` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `/api/tool-io-orders/<order_no>/assign-transport` | POST | `order:keeper_confirm` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/transport-start` | POST | `order:transport_execute` | ❌ | ✅ | ❌ | ✅ | ❌ |
| `/api/tool-io-orders/<order_no>/transport-complete` | POST | `order:transport_execute` | ❌ | ✅ | ❌ | ✅ | ❌ |
| `/api/tool-io-orders/<order_no>/report-transport-issue` | POST | `order:transport_execute` | ❌ | ✅ | ❌ | ✅ | ❌ |
| `/api/tool-io-orders/<order_no>/transport-issues` | GET | `order:view` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `/api/tool-io-orders/<order_no>/resolve-transport-issue` | POST | `order:keeper_confirm` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/reject` | POST | `order:cancel` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/cancel` | POST | `order:cancel` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>` | DELETE | `order:delete` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/logs` | GET | `order:view` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `/api/tool-io-orders/<order_no>/notification-records` | GET | `notification:view` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `/api/tool-io-orders/pending-keeper` | GET | `order:keeper_confirm` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/pre-transport` | GET | `order:transport_execute` | ❌ | ❌ | ❌ | ✅ | ❌ |
| `/api/tool-io-orders/<order_no>/generate-keeper-text` | GET | `notification:create` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/generate-transport-text` | GET | `notification:create` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/notify-transport` | POST | `notification:send_feishu` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/api/tool-io-orders/<order_no>/notify-keeper` | POST | `notification:send_feishu` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `/api/notifications` | GET | `notification:view` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `/api/notifications/<id>/read` | POST | `notification:view` | ✅ | ✅ | ✅ | ❌ | ✅ |

### 工装路由 (tool_routes.py)

| API 端点 | 方法 | 所需权限 | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|---------|------|---------|-------------|--------|---------|-----------------|---------|
| `/api/tools/search` | GET | `tool:search` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `/api/tools/batch-query` | POST | `tool:view` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `/api/tools/batch-status` | PATCH | `tool:status_update` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/tools/status-history/<code>` | GET | `tool:view` | ✅ | ✅ | ✅ | ✅ | ❌ |

### 组织路由 (org_routes.py)

| API 端点 | 方法 | 所需权限 | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|---------|------|---------|-------------|--------|---------|-----------------|---------|
| `/api/orgs` | GET | `dashboard:view` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/api/orgs/tree` | GET | `dashboard:view` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/api/orgs/<id>` | GET | `dashboard:view` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/api/orgs` | POST | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/orgs/<id>` | PUT | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |

### 系统路由 (system_routes.py)

| API 端点 | 方法 | 所需权限 | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|---------|------|---------|-------------|--------|---------|-----------------|---------|
| `/api/system/diagnostics/recent-errors` | GET | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/system/diagnostics/notification-failures` | GET | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/db/test` | GET | `dashboard:view` | ✅ | ✅ | ✅ | ✅ | ✅ |

### 管理路由 (admin_user_routes.py)

| API 端点 | 方法 | 所需权限 | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|---------|------|---------|-------------|--------|---------|-----------------|---------|
| `/api/admin/roles` | GET | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/admin/users` | GET | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/admin/users/<id>` | GET | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/admin/users` | POST | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/admin/users/<id>` | PUT | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/admin/users/<id>/roles` | PUT | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/admin/users/<id>/status` | PUT | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/admin/users/<id>/password-reset` | PUT | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |

### 反馈路由 (feedback_routes.py)

| API 端点 | 方法 | 所需权限 | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|---------|------|---------|-------------|--------|---------|-----------------|---------|
| `/api/feedback/all` | GET | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/feedback/<id>/status` | PUT | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/feedback/<id>/reply` | POST | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `/api/feedback/<id>/replies` | GET | `admin:user_manage` | ❌ | ❌ | ❌ | ❌ | ❌ |

### 仪表盘路由 (dashboard_routes.py)

| API 端点 | 方法 | 所需权限 | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|---------|------|---------|-------------|--------|---------|-----------------|---------|
| `/api/dashboard/metrics` | GET | `order:list` | ✅ | ✅ | ✅ | ❌ | ✅ |

---

## 变更日志 / Changelog

| 日期 | 变更内容 | 变更人 |
|------|---------|--------|
| 2026-03-27 | 移除 KEEPER 的 `order:transport_execute` 权限，修复保管员能看到预知运输菜单但无权限访问的问题 | Claude Code |
| 2026-03-27 | 调整 `GET /api/tool-io-orders/<order_no>/transport-issues` 权限为 `order:view`，修复 OrderDetail 页面非保管员角色加载 403 | Codex |
| 2026-03-27 | 添加 dashboard:view 权限给 PRODUCTION_PREP (修复 bug #10168 - fengliang 登录后无限重定向) | Claude Code |
| 2026-03-25 | 新增准备工预知运输列表 API 权限映射 (`GET /api/tool-io-orders/pre-transport`) | Codex |
| 2026-03-25 | 新增运输异常上报/查询/处理 API 权限映射 (`report-transport-issue`, `transport-issues`, `resolve-transport-issue`) | Codex |
| 2026-03-25 | 全面同步 RBAC_PERMISSION_MATRIX.md 与 RBAC_INIT_DATA.md，添加 ROLE_PRODUCTION_PREP, 修正 PLANNER/AUDITOR 权限 | Claude Code |
| 2026-03-24 | 新建文档，同步 RBAC 权限矩阵 | Claude Code |
| 2026-03-24 | 添加 notification:view 权限给 KEEPER (修复 bug #10133) | Claude Code |
| 2026-03-24 | 添加 notification:create 权限给 KEEPER (修复 bug #10134) | Claude Code |

---

## 维护规则 / Maintenance Rules

### 新增 API 时的强制步骤

1. 在 `order_routes.py` 等文件添加 `@require_permission` 注解
2. **立即在此矩阵中更新** 对应端点的权限列
3. 检查该权限是否已分配给需要的角色
4. 如需新增/修改角色权限，更新 `rbac_service.py` 中的 `_ensure_incremental_permission_defaults` 函数
5. **重要**: 如需修改权威权限定义，必须同时更新 `docs/RBAC_INIT_DATA.md`

### 权限命名规范

- 格式: `<resource>:<action>`
- 示例: `order:submit`, `notification:view`
- 禁止: 混合大小写、中划线等非标准写法

### 权威来源优先级

1. `docs/RBAC_INIT_DATA.md` - 权威数据来源
2. `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵和 API 映射
3. `backend/services/rbac_service.py` - 运行时实现
4. `backend/routes/*.py` - API 路由权限注解
