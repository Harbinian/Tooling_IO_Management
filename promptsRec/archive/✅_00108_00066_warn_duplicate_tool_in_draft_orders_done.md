Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 048
Goal: Warn user when creating draft order with tools already in other draft orders
Dependencies: None
Execution: RUNPROMPT

---

## Context

当前问题：用户可以创建多个包含同一工装的草稿订单，但最终只能提交其中一个。这导致用户可能创建无效的草稿订单，浪费操作时间。

期望行为：在创建草稿订单时，如果检测到该工装已被其他草稿订单包含，应该给出警告提示，但不阻止创建。

---

## Required References

- `backend/database/repositories/tool_repository.py` - `check_tools_available()` 函数
- `backend/database/repositories/order_repository.py` - `create_order()` 函数
- `backend/services/tool_io_service.py` - `create_order()` service 函数

---

## Core Task

修改创建订单逻辑，当用户创建包含某工装的草稿订单时，检查该工装是否已被其他草稿订单包含。如果是，给出警告信息但不阻止创建。

---

## Required Work

1. 在 `tool_repository.py` 中新增函数 `check_tools_in_draft_orders(tool_codes)`，查询指定工装是否存在于其他草稿订单中

2. 修改 `order_repository.py` 的 `create_order()` 函数：
   - 调用 `check_tools_in_draft_orders()` 检查工装
   - 如果发现工装已在其他草稿订单中，在返回结果中增加警告信息
   - 不阻止订单创建，只提供警告

3. 返回结构扩展：
   ```python
   {
     "success": True,
     "order_no": "...",
     "warning": "工装 T000001 已在草稿订单 TO-OUT-20260318-006 中"  # 如果有冲突
   }
   ```

---

## Constraints

- 不阻止用户创建订单，只提供警告
- 警告信息应清晰指出哪些工装在哪些草稿订单中
- 保持现有事务处理逻辑不变

---

## Completion Criteria

1. 后端语法检查通过：
   ```powershell
   python -m py_compile backend/database/repositories/tool_repository.py backend/database/repositories/order_repository.py backend/services/tool_io_service.py
   ```

2. 功能测试：
   - 创建包含 T000001 的草稿订单 A
   - 再创建包含 T000001 的草稿订单 B
   - 验证订单 B 创建成功但返回警告信息

3. 前端需同步更新以显示警告信息（由 Gemini 负责）
