# 10177_fix_order_delete_and_cancel_permission

## Context

班组长（TEAM_LEADER）发现自己无法删除自己创建的草稿订单，且已提交（submitted）的订单无法撤回。

**问题1：删除自己创建的草稿被拒绝**
- 班组长 hutingting (user_id: `U_7954837C515844BA`) 尝试删除 `TO-OUT-20260401-001`（draft状态）
- 但该订单的 `initiator_id` 是 `U_8546A79BA76D4FD2`（另一个用户）
- 当前实现检查 `initiator_id != operator_id`，导致删除被拒绝

**问题2：已提交订单的取消权限不清晰**
- `cancel_order` 当前只阻止 `completed/rejected/cancelled` 状态的取消
- 用户要求：已提交（submitted）且保管员尚未给出结论前，可以取消；**保管员确认（keeper_confirmed）后，不允许取消**

---

## Required References

- `backend/routes/order_routes.py` - 删除 API 路由（已修改，但有 bug）
- `backend/database/repositories/order_repository.py` - `delete_order` 和 `cancel_order` 的核心逻辑
- `docs/RBAC_PERMISSION_MATRIX.md` - RBAC 权限矩阵
- `docs/RBAC_INIT_DATA.md` - RBAC 初始数据

---

## Core Task

修复两个问题：

### 问题1 Fix（补充）：班组长删除权限

当前 `delete_order` repository 检查 `initiator_id != operator_id`，但传入的 `operator_id` 可能与订单的 `initiator_id` 不匹配。需要确认 `operator_id` 的来源是否正确。

**期望行为**：
- 班组长（TEAM_LEADER）可以删除**自己创建的**草稿订单
- SYS_ADMIN 可以删除任意订单

**需要检查**：
1. `operator_id` 在 delete API 路由层是否正确传入
2. `build_actor_payload` 是否正确提取 `user_id` 作为 `operator_id`
3. 订单的 `initiator_id` 是否与创建者的 `user_id` 一致

### 问题2：取消订单业务规则修正

**当前行为**：`cancel_order` 允许取消任何非 `completed/rejected/cancelled` 状态的订单，包括 `keeper_confirmed`。

**期望行为**：
- `draft` → 可以取消
- `submitted` → 可以取消（保管员尚未处理）
- `keeper_confirmed` → **不允许取消**（保管员已给出结论）
- `partially_confirmed` → **不允许取消**
- `transport_notified` → **不允许取消**
- `transport_in_progress` → **不允许取消**
- `transport_completed` → **不允许取消**
- `final_confirmation_pending` → **不允许取消**
- `completed/rejected/cancelled` → 保持现状（已不允许）

**修改文件**：
- `backend/database/repositories/order_repository.py` 的 `cancel_order` 函数
- 在状态检查处添加 `keeper_confirmed` 及之后状态的拦截

---

## Required Work

### Step 1: 诊断 delete_order 问题

1. 读取 `backend/routes/order_routes.py` 的 `api_tool_io_order_delete` 函数
2. 读取 `backend/routes/common.py` 的 `build_actor_payload` 函数
3. 确认 `operator_id` 是否正确传递
4. 查询数据库确认订单的 `initiator_id` 与 `user_id` 的关系

### Step 2: 修复 cancel_order 业务规则

在 `order_repository.py` 的 `cancel_order` 函数（line 883-891）中修改状态检查：

**修改前**：
```python
if current_status in ['completed', 'rejected', 'cancelled']:
    return {'success': False, 'error': f'当前状态不允许取消，当前状态：{current_status}'}
```

**修改后**：
```python
if current_status in ['keeper_confirmed', 'partially_confirmed', 'transport_notified',
                       'transport_in_progress', 'transport_completed',
                       'final_confirmation_pending', 'completed', 'rejected', 'cancelled']:
    return {'success': False, 'error': f'当前状态不允许取消，当前状态：{current_status}'}
```

### Step 3: 验证

1. 运行 `python -m py_compile backend/database/repositories/order_repository.py backend/routes/order_routes.py` 确认语法正确
2. 确认取消逻辑对 `submitted` 状态有效，对 `keeper_confirmed` 及之后状态无效

### Step 4: 更新 RBAC 文档

更新 `docs/RBAC_PERMISSION_MATRIX.md` 的变更日志，记录：
- 取消订单的状态限制规则

---

## Constraints

- 只修改 `cancel_order` 的状态检查逻辑和 `delete_order` 的诊断
- 不修改 `delete_order` 的业务规则（保持只能删除自己创建的草稿）
- 不修改其他工作流逻辑
- 使用中文字段名常量（通过 `ORDER_COLUMNS` 等）

---

## Completion Criteria

1. `cancel_order` 在 `keeper_confirmed` 及之后状态返回错误
2. `cancel_order` 对 `submitted` 状态允许取消
3. 班组长删除自己创建的草稿订单的功能正常（如果诊断发现问题一并修复）
4. Python 语法检查通过
5. 文档已更新
