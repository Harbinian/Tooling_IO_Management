Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 047
Goal: Filter admin order list to exclude draft orders
Dependencies: None
Execution: RUNPROMPT

---

## Context

系统管理员在订单列表中应该只看到**已提交及后续状态**的订单，而不包括草稿订单（因为管理员无需创建申请）。

当前行为：
- 管理员拥有 `all_access=True`，能看到所有订单（包括草稿）
- `_is_order_accessible()` 对管理员返回 `True`，不过滤任何订单

期望行为：
- 管理员应该只能看到 `order_status != 'draft'` 的订单
- 非管理员（班组长、保管员）不受影响，仍按现有逻辑可见

---

## Required References

- `backend/services/tool_io_service.py` - `list_orders()` 和 `_is_order_accessible()` 函数
- `backend/services/rbac_data_scope_service.py` - `order_matches_scope()` 和 `resolve_order_data_scope()` 函数
- `docs/RBAC_DESIGN.md` - 角色数据范围定义

---

## Core Task

修改后端权限逻辑，使管理员在订单列表中只能看到已提交及后续状态的订单。

---

## Required Work

1. 在 `tool_io_service.py` 的 `_is_order_accessible()` 函数中，对拥有 `all_access=True` 的管理员用户增加状态过滤

2. 修改逻辑：
   - 先检查数据范围权限（保持现有逻辑）
   - 如果用户是管理员（`all_access=True`），额外过滤掉草稿订单
   - 管理员不能看草稿订单，但可以看到其他所有状态的订单

3. 验证非管理员用户不受影响

---

## Constraints

- 保持现有数据范围权限检查逻辑不变
- 只对管理员（`all_access=True`）增加额外的状态过滤
- 不修改其他角色的可见性行为

---

## Completion Criteria

1. 后端语法检查通过：
   ```powershell
   python -m py_compile backend/services/tool_io_service.py backend/services/rbac_data_scope_service.py
   ```

2. 管理员账户测试：
   - 登录管理员账户
   - 创建草稿订单和已提交订单
   - 验证订单列表中不显示草稿订单，但显示已提交订单

3. 非管理员账户测试：
   - 登录班组长/保管员账户
   - 验证仍能看到自己有权限的订单，不受影响
