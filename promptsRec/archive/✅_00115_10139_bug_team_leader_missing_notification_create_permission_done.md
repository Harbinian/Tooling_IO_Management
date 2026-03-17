Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10139
Goal: Fix 403 FORBIDDEN error when team_leader calls generate-keeper-text API
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

太东旭（team_leader角色）在提交订单后查看订单详情时，点击生成保管员通知文本功能，`/api/tool-io-orders/TO-OUT-20260324-005/generate-keeper-text` 接口返回 403 FORBIDDEN 错误。

**前端日志**：
```
:8150/api/tool-io-orders/TO-OUT-20260324-005/generate-keeper-text:1 Failed to load resource: the server responded with a status of 403 (FORBIDDEN)
```

**根本原因**：`ROLE_TEAM_LEADER` 在数据库 `sys_role_permission_rel` 表中缺少 `notification:create` 权限，导致权限检查失败返回 403。

---

## Required References / 必需参考

1. `docs/RBAC_INIT_DATA.md` - 已更新，包含权限定义和 SQL 模板
2. `docs/RBAC_DESIGN.md` - RBAC 设计文档
3. `backend/routes/order_routes.py:380` - API 路由定义，使用 `@require_permission("notification:create")`
4. `backend/services/auth_service.py:266` - `require_permission` 函数实现
5. `database.py` - 数据库连接和查询方法

---

## Core Task / 核心任务

在数据库 `sys_role_permission_rel` 表中为 `ROLE_TEAM_LEADER` 添加 `notification:create` 权限记录，解决 403 权限拒绝错误。

---

## Required Work / 必需工作

### 1. 调查阶段

1.1 检查 `sys_role_permission_rel` 表，确认 `ROLE_TEAM_LEADER` 当前持有的权限列表：
```sql
SELECT permission_code FROM sys_role_permission_rel WHERE role_id = 'ROLE_TEAM_LEADER';
```

1.2 确认 `notification:create` 权限是否存在于 `sys_permission` 表：
```sql
SELECT permission_code, permission_name FROM sys_permission WHERE permission_code = 'notification:create';
```

1.3 检查当前数据库中是否已存在该权限分配记录：
```sql
SELECT 1 FROM sys_role_permission_rel
WHERE role_id = 'ROLE_TEAM_LEADER' AND permission_code = 'notification:create';
```

### 2. 修复阶段

2.1 如果 `notification:create` 权限记录不存在，执行插入：
```sql
INSERT INTO sys_role_permission_rel (role_id, permission_code)
SELECT 'ROLE_TEAM_LEADER', 'notification:create'
WHERE NOT EXISTS (
    SELECT 1 FROM sys_role_permission_rel
    WHERE role_id = 'ROLE_TEAM_LEADER' AND permission_code = 'notification:create'
);
```

2.2 验证插入成功：
```sql
SELECT permission_code FROM sys_role_permission_rel WHERE role_id = 'ROLE_TEAM_LEADER';
-- 确认列表中包含 'notification:create'
```

### 3. 验证阶段

3.1 语法检查相关后端文件：
```powershell
python -m py_compile backend/services/auth_service.py backend/routes/order_routes.py
```

3.2 如果系统有权限缓存，需要重启后端服务使新权限生效

3.3 确认太东旭（team_leader）用户可以正常调用 `generate-keeper-text` API

---

## Constraints / 约束条件

1. **只执行必要的数据库修改**：只添加缺失的权限记录，不修改其他权限
2. **幂等性**：使用 `WHERE NOT EXISTS` 确保重复执行不会导致错误
3. **不修改代码**：此问题不需要修改后端代码，权限配置已在数据库中
4. **不修改文档**：文档 `docs/RBAC_INIT_DATA.md` 已由架构师更新
5. **保留审计追踪**：操作应记录在操作日志中

---

## Completion Criteria / 完成标准

1. `sys_role_permission_rel` 表中 `ROLE_TEAM_LEADER` 拥有 `notification:create` 权限
2. 太东旭（team_leader角色）调用 `/api/tool-io-orders/{order_no}/generate-keeper-text` 返回 200 而非 403
3. 太东旭调用 `/api/tool-io-orders/{order_no}/generate-transport-text` 也返回 200
4. 其他角色（keeper, admin）的权限不受影响
5. 相关权限的用户（如 keeper）仍然可以正常使用通知生成功能
