# 10133_bug_keeper_notification_view_permission

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10133
Goal: Fix KEEPER role missing notification:view permission causing 403 on notification-records API
Dependencies: None
Execution: RUNPROMPT

---

## Context

### 问题描述

**用户**: 胡婷婷 (KEEPER 角色)
**API**: `GET /api/tool-io-orders/{order_no}/notification-records`
**错误**: HTTP 403 FORBIDDEN

用户可以成功访问：
- `GET /tool-io-orders/{order_no}` - 订单详情 ✅
- `GET /tool-io-orders/{order_no}/logs` - 操作日志 ✅

但无法访问：
- `GET /tool-io-orders/{order_no}/notification-records` - 通知记录 ❌ 403

### 根本原因

`backend/services/rbac_service.py` 中 KEEPER 角色权限配置不完整：

```python
# 第221-227行 ROLE_KEEPER 权限分配
('ROLE_KEEPER', 'dashboard:view'),
('ROLE_KEEPER', 'order:view'),
('ROLE_KEEPER', 'order:list'),
('ROLE_KEEPER', 'order:keeper_confirm'),
('ROLE_KEEPER', 'notification:send_feishu')  # ✅ 有发送权限
# ❌ 缺少: ('ROLE_KEEPER', 'notification:view')
```

同时 `notification:view` 权限定义为：
```python
('notification:view', 'View Notification', 'notification', 'view'),
```

API 端点需要 `notification:view` 权限：
```python
# order_routes.py:315-316
@order_bp.route("/api/tool-io-orders/<order_no>/notification-records", methods=["GET"])
@require_permission("notification:view")
```

---

## Required References

1. `backend/services/rbac_service.py` - RBAC 权限配置 (Line ~195-227)
2. `backend/routes/order_routes.py` - notification-records API (Line ~315-325)
3. `docs/RBAC_DESIGN.md` - RBAC 权限设计文档
4. `docs/API_SPEC.md` - API 权限规格 (notification:view)

---

## Core Task

为 KEEPER 角色添加 `notification:view` 权限，使其能够访问通知记录 API。

**涉及文件**:
- `backend/services/rbac_service.py` - 添加角色权限关联

**受影响 API**:
- `GET /api/tool-io-orders/<order_no>/notification-records` - 需要 `notification:view` 权限

---

## Required Work

1. **检查 rbac_service.py** 中 `_ensure_role_permission_rel` 函数调用位置
2. **为 ROLE_KEEPER 添加** `notification:view` 权限关联
3. **验证** 其他角色（TEAM_LEADER, ADMIN）已有此权限
4. **确认修改** 符合 RBAC 设计文档中的权限矩阵

### 权限矩阵（来自 RBAC_DESIGN.md）

| 角色 | notification:view | notification:send_feishu |
|------|-------------------|---------------------------|
| TEAM_LEADER | ❓ | ❓ |
| KEEPER | ❌ (需修复) | ✅ |
| ADMIN | ✅ | ✅ |

---

## Constraints

1. **只修改必要的权限配置**，不要修改其他角色权限
2. **不要修改 API 路由** 或 `require_permission` 装饰器
3. **遵循现有代码风格** - 使用 `db.execute_query` 和 `_ensure_role_permission_rel` 函数
4. **验证事务处理** - 如果 `_ensure_role_permission_rel` 有事务包装，确保正确

---

## Completion Criteria

- [ ] `GET /api/tool-io-orders/{order_no}/notification-records` 对 KEEPER 角色返回 200
- [ ] KEEPER 角色在数据库 `sys_role_permission_rel` 表中拥有 `notification:view` 权限
- [ ] 其他已有 `notification:view` 权限的角色（ADMIN, TEAM_LEADER）不受影响
- [ ] 语法检查通过: `python -m py_compile backend/services/rbac_service.py`
