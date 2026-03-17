Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 110
Goal: Fix keeper cannot see submitted orders due to data scope filtering
Dependencies: None
Execution: RUNPROMPT

---

## Context

**问题**：订单 TO-OUT-20260319-001 状态为 `submitted`，但保管员看不到它。

**根本原因**：
- 订单 `org_id = ORG_DEPT_005`，但 `keeper_id = NULL`（未指定保管员）
- `order_matches_scope()` 函数对 `ASSIGNED` 范围的用户要求 `keeper_id` 或 `transport_assignee_id` 匹配
- 由于 `keeper_id = NULL`，即使保管员在同一组织，也看不到该订单

**期望行为**：
- 已提交（`submitted`）或部分确认（`partially_confirmed`）状态的订单，应该对**同组织的所有保管员**可见
- 这类订单的可见性不应依赖于 `keeper_id` 是否被指定

---

## Required References

- `backend/services/rbac_data_scope_service.py` - `order_matches_scope()` 函数
- `backend/database/repositories/order_repository.py` - `get_pending_keeper_orders()` 函数

---

## Core Task

修改 `order_matches_scope()` 函数逻辑，对于已提交或部分确认状态的订单，如果用户是同一组织的 `keeper` 角色，应能看见该订单。

---

## Required Work

1. 在 `order_matches_scope()` 中增加特殊处理：
   - 如果订单状态是 `submitted` 或 `partially_confirmed`
   - 且用户角色包含 `keeper`
   - 且用户在同一组织（`org_ids` 包含 `order_org_id`）
   - 则返回 `True`（允许访问）

2. 建议的实现方式：
   ```python
   def order_matches_scope(order: Dict, scope_context: Dict) -> bool:
       # 现有逻辑...
       if scope_context.get("all_access"):
           return True

       order_status = str(order.get("order_status") or order.get("单据状态") or "").strip().lower()
       user_roles = scope_context.get("user_roles", [])
       is_keeper = any(r.get("role_code") == "keeper" for r in user_roles)

       # 已提交或部分确认的订单，对同组织 keeper 可见
       if order_status in ("submitted", "partially_confirmed") and is_keeper:
           order_org_id = str(order.get("org_id") or order.get(ORDER_ORG_COLUMN) or "").strip()
           org_ids = set(scope_context.get("org_ids", []))
           if org_ids and order_org_id in org_ids:
               return True

       # 现有逻辑继续...
   ```

3. 需要在 `scope_context` 中返回 `user_roles` 信息

---

## Constraints

- 保持其他数据范围逻辑不变
- 不影响管理员的 `all_access` 权限
- 不影响班组长（team_leader）的可见性

---

## Completion Criteria

1. 后端语法检查通过：
   ```powershell
   python -m py_compile backend/services/rbac_data_scope_service.py backend/database/repositories/order_repository.py
   ```

2. 功能测试：
   - 订单状态为 `submitted`，`org_id = ORG_DEPT_005`
   - 保管员用户在同一组织
   - 验证保管员能看到该订单
