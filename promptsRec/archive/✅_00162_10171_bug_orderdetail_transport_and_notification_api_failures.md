# Prompt 10171: Bug Fix - OrderDetail.vue Transport-Issues and Notification-Records API Failures

Primary Executor: Codex
Task Type: Bug Fix
Priority: P2
Stage: 10171
Goal: Fix 403 and 404 API errors on OrderDetail.vue page
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

在浏览器控制台检测到 OrderDetail.vue 页面加载时出现两个 API 错误：

1. `GET /api/tool-io-orders/TO-OUT-20260326-026/transport-issues` 返回 403 FORBIDDEN
2. `GET /api/tool-io-orders/TO-OUT-20260326-026/notification-records` 返回 404 NOT FOUND

前端调用来自 `frontend/src/api/orders.js`:
- `getTransportIssues` (line 232)
- `getNotificationRecords` (line 186)

---

## Required References / 必需参考

- `backend/routes/order_routes.py` (lines 281-295 for transport-issues, lines 427-437 for notification-records)
- `backend/services/tool_io_service.py` - `get_notification_records` function
- `backend/services/transport_issue_service.py` - `get_transport_issues` function
- `docs/RBAC_PERMISSION_MATRIX.md` - Permission matrix showing which roles have which permissions
- `backend/services/rbac_service.py` - Permission checking implementation

---

## Core Task / 核心任务

调查并修复 OrderDetail.vue 页面加载时两个 API 端点的失败问题。

### Issue 1: transport-issues 403 FORBIDDEN

- 路由: `GET /api/tool-io-orders/<order_no>/transport-issues`
- 当前权限要求: `@require_permission("order:keeper_confirm")`
- RBAC 矩阵显示: `order:keeper_confirm` 权限仅分配给 KEEPER 和 SYS_ADMIN 角色

**可能原因:**
1. 当前登录用户不是 KEEPER 或 SYS_ADMIN 角色
2. 权限检查逻辑有 bug，导致即使有权限也返回 403
3. 前端请求发送时未正确携带认证信息

**Bug 调查要求:**
- 检查 `rbac_service.py` 中 `@require_permission` 装饰器的实现
- 检查 `get_authenticated_user()` 是否正确返回当前用户
- 验证权限检查是在路由层还是服务层失败
- 检查后端日志获取具体拒绝原因

### Issue 2: notification-records 404 NOT FOUND

- 路由: `GET /api/tool-io-orders/<order_no>/notification-records`
- 当前权限要求: `@require_permission("notification:view")`
- RBAC 矩阵显示: `notification:view` 分配给 TEAM_LEADER, KEEPER, PLANNER, SYS_ADMIN, AUDITOR

**可能原因:**
1. 路由存在但 `get_notification_records` 服务函数返回了 404
2. 服务函数可能查询的表或字段不存在
3. 服务函数内部逻辑错误返回了 404 状态码

**Bug 调查要求:**
- 检查 `tool_io_service.py` 中 `get_notification_records` 函数的完整实现
- 检查该函数查询的数据库表是否存在
- 检查 SQL 查询是否正确
- 验证返回 404 的具体条件

---

## Required Work / 必需工作

1. **Issue 1 (transport-issues 403) 修复:**
   - 如果权限检查有 bug，修复 `rbac_service.py` 中的权限验证逻辑
   - 如果是权限配置缺失，更新 RBAC_INIT_DATA.md 并确保权限正确分配
   - 确保 KEEPER 角色能够访问 transport-issues 端点

2. **Issue 2 (notification-records 404) 修复:**
   - 检查 `get_notification_records` 函数实现
   - 确保查询的表和字段存在
   - 修复导致 404 的根本原因
   - 确保函数正确返回通知记录数据

3. **验证:**
   - 修复后，使用有 KEEPER 角色的用户测试 transport-issues API
   - 修复后，测试 notification-records API 返回正确数据
   - 确保其他角色访问这两个端点的行为符合 RBAC 矩阵

---

## Constraints / 约束条件

1. 禁止直接修改 `column_names.py` 而不更新 `schema_manager.py`
2. 所有 SQL 查询必须使用 `backend/database/schema/column_names.py` 中的常量
3. 如果涉及 RBAC 权限变更，必须同步更新 `docs/RBAC_PERMISSION_MATRIX.md` 和 `docs/RBAC_INIT_DATA.md`
4. 修复必须符合项目的 RBAC 设计，不能绕过权限检查

---

## Completion Criteria / 完成标准

1. `GET /api/tool-io-orders/<order_no>/transport-issues` 对 KEEPER 角色返回 200（而非 403）
2. `GET /api/tool-io-orders/<order_no>/notification-records` 返回 200 和正确的通知记录数据（而非 404）
3. 其他角色的权限行为符合 RBAC_PERMISSION_MATRIX.md 定义
4. 如果有任何 RBAC 配置变更，文档已同步更新
5. 后端语法检查通过: `python -m py_compile backend/routes/order_routes.py backend/services/tool_io_service.py backend/services/transport_issue_service.py`
