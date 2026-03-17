# Bug Fix: Systemic Service Layer Interface Mismatches

**Primary Executor**: Claude Code
**Task Type**: Bug Fix
**Priority**: P0
**Stage**: 10148
**Goal**: Fix 10 critical function call/signature mismatches across backend service layer
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context

系统发现 **10 个严重的服务层接口不匹配问题**，这些问题导致核心工作流（订单提交、驳回、取消、确认、审计日志）功能完全失效或数据损坏。

这些 Bug 不是代码演进过程中引入的，而是 `order_workflow_service.py`、`tool_io_service.py`、`rbac_data_scope_service.py` 等文件**同时创建时**函数签名与调用方式就不一致。

---

## Required References

必须检查以下文件的完整函数签名和所有调用点：

### 接口定义层
- `database.py` - 所有 `*_order`, `*_tool` 函数的原始签名
- `backend/database/repositories/order_repository.py` - OrderRepository 方法签名
- `backend/database/repositories/tool_repository.py` - ToolRepository 方法签名

### 服务调用层
- `backend/services/order_workflow_service.py` - 所有外部函数调用
- `backend/services/tool_io_service.py` - 所有外部函数调用
- `backend/services/rbac_data_scope_service.py` - build_order_scope_sql 及所有调用
- `backend/services/audit_log_service.py` - write_order_audit_log 签名

### 运行时服务
- `backend/services/tool_io_runtime.py` - get_order_detail_runtime, keeper_confirm_runtime 等

---

## Core Task

修复以下 10 个接口不匹配问题：

### Issue 1: `order_workflow_service.py:submit_order` → `submit_tool_io_order`
**问题**: 参数数量不匹配
- **函数签名**: `submit_tool_io_order(order_no: str, operator_id: str, operator_name: str, operator_role: str)`
- **错误调用**: `submit_tool_io_order(order_no, payload)` - 只传 2 个参数，第二个是 Dict

### Issue 2: `order_workflow_service.py:reject_order` → `reject_tool_io_order`
**问题**: 参数数量不匹配 (5 vs 4) + 顺序错误
- **函数签名**: `reject_tool_io_order(order_no, operator_id, operator_name, reason)`
- **错误调用**: 传了 5 个参数，顺序完全打乱

### Issue 3: `order_workflow_service.py:write_order_audit_log`
**问题**: 参数名称错误
- **函数签名**: `write_order_audit_log(*, order_no, operation_type, operator_user_id, operator_name, operator_role, previous_status, new_status, remark, item_id)`
- **错误调用**: 使用了 `operation` (应为 `operation_type`)、`operator_id` (应为 `operator_user_id`)、`detail` (应为 `remark`)

### Issue 4: `order_workflow_service.py` 多处 → `get_order_detail_runtime`
**问题**: 多传 current_user 参数
- **函数签名**: `get_order_detail_runtime(order_no: str)`
- **错误调用**: `get_order_detail_runtime(order_no, current_user)` - 多传了 current_user

### Issue 5: `order_workflow_service.py:keeper_confirm` → `keeper_confirm_runtime`
**问题**: 参数数量不匹配 (2 vs 7)
- **函数签名**: `keeper_confirm_runtime(order_no, keeper_id, keeper_name, confirm_data, operator_id, operator_name, operator_role)`
- **错误调用**: `keeper_confirm_runtime(order_no, actor)` - 只传 2 个参数

### Issue 6: `order_workflow_service.py` → `get_order_logs_runtime`
**问题**: 多传 current_user 参数
- **函数签名**: `get_order_logs_runtime(order_no: str)`
- **错误调用**: `get_order_logs_runtime(order_no, current_user)`

### Issue 7: `order_workflow_service.py` → `list_pending_keeper_orders`
**问题**: 多传 current_user 参数
- **函数签名**: `list_pending_keeper_orders(keeper_id: str | None = None)`
- **错误调用**: `list_pending_keeper_orders(keeper_id, current_user)`

### Issue 8: `tool_io_service.py:reject_order` → `reject_tool_io_order`
**问题**: 参数顺序完全错误
- **函数签名**: `reject_tool_io_order(order_no, operator_id, operator_name, reason)`
- **错误调用**: 传入 `payload.get("reject_reason")` 作为 operator_id，`payload.get("operator_id")` 作为 operator_name 等

### Issue 9: `tool_io_service.py:cancel_order` → `cancel_tool_io_order`
**问题**: 参数语义错误
- **函数签名**: `cancel_tool_io_order(order_no, operator_id, operator_name, reason)`
- **错误调用**: 第四个参数传入 `operator_role` 而非 `reason`，且没有提取取消原因

### Issue 10: `order_query_service.py:list_orders` → `build_order_scope_sql`
**问题**: 参数类型错误
- **函数签名**: `build_order_scope_sql(scope_context: Dict)`
- **错误调用**: `build_order_scope_sql(scope_context.get("role_codes", []), scope_context.get("user_id", ""), scope_context.get("org_ids", []))`
- **修复**: 直接传入 `scope_context` Dict，而非三个独立的值

---

## Required Work

1. **全面扫描**: 检查 `backend/services/` 下所有文件，找出所有调用 `database.py`、`tool_io_runtime.py`、`audit_log_service.py` 中函数的代码
2. **交叉验证**: 对每个调用，对比函数签名与实际传入的参数
3. **统一修复**: 根据函数签名修正每个调用
4. **验证修复**: 使用 `python -m py_compile` 验证语法正确性
5. **检查遗漏**: 确保没有其他类似问题被遗漏

### 修复原则

- **最小修改**: 只修参数传递，不改变函数签名
- **保持语义**: 确保修复后参数值传递给正确的形参
- **向后兼容**: 确保 API 行为不变，只修复内部调用错误

---

## Constraints

1. **不修改被调用函数的签名** - 只能修改调用处的参数
2. **不引入新功能** - 只修复接口不匹配
3. **不破坏现有测试** - 如果有测试依赖当前行为，先记录
4. **使用英文变量名** - 代码中禁止使用拼音
5. **UTF-8 编码** - 所有修改文件使用 UTF-8 无 BOM 编码

---

## Completion Criteria

1. 所有 10 个问题的调用处已修正
2. `python -m py_compile backend/services/order_workflow_service.py` 通过
3. `python -m py_compile backend/services/tool_io_service.py` 通过
4. `python -m py_compile backend/services/order_query_service.py` 通过
5. `python -m py_compile backend/services/audit_log_service.py` 通过（如有修改）
6. 创建修复报告 `logs/prompt_task_runs/run_[时间戳]_10148_bug_service_layer_interface_mismatches.md`

---

## Bug 分类

| 问题 # | 严重程度 | 影响功能 |
|--------|----------|----------|
| 1 | P0 | 订单提交 |
| 2 | P0 | 订单驳回 |
| 3 | P0 | 审计日志 |
| 4 | P0 | 订单详情查询 |
| 5 | P0 | 保管员确认 |
| 6 | P1 | 日志查询 |
| 7 | P1 | 待确认列表 |
| 8 | P0 | 订单驳回 |
| 9 | P1 | 订单取消 |
| 10 | P0 | RBAC 订单列表（管理员无权限）|
