# Bug Fix: Transport Workflow Broken for Cross-Organization Orders

**Primary Executor**: Codex
**Task Type**: Bug Fix
**Priority**: P0 (CRITICAL)
**Stage**: 10164
**Goal**: Fix transport operator access to orders assigned to them when order is from different organization
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context / 上下文

E2E 测试发现运输工作流在跨组织订单场景下完全失效：

测试场景：
- taidongxu (TEAM_LEADER, DEPT_005) 创建并提交订单
- hutingting (KEEPER, DEPT_001) 确认订单并分配运输
- fengliang (PRODUCTION_PREP, DEPT_001) 被指定为运输操作员
- fengliang 调用 `GET /api/tool-io-orders/pre-transport` 返回空列表
- fengliang 调用 `POST /api/tool-io-orders/{order_no}/transport-start` 返回 "order not found"

根本原因：运输操作员（fengliang）属于 DEPT_001，但订单的 `org_id` 是 DEPT_005。`get_pre_transport_orders()` 只按 `org_ids` 过滤，没有检查用户是否是订单指定的运输接收人。

---

## Required References / 必需参考

1. `backend/database/repositories/order_repository.py` - `get_pre_transport_orders()` 方法
2. `backend/services/tool_io_service.py` - `get_pre_transport_orders()` 函数
3. `backend/services/rbac_data_scope_service.py` - `order_matches_scope()` 函数
4. `backend/database/schema/column_names.py` - 中文字段名常量
5. `docs/ARCHITECTURE.md` - 架构文档

---

## Core Task / 核心任务

修复 `get_pre_transport_orders()` 使运输操作员能够看到分配给他们的订单，即使订单来自不同组织。

当前问题逻辑：
- `OrderRepository.get_pre_transport_orders()` 只按 `org_ids` 过滤
- 没有检查 `transport_assignee_id` (运输人ID)

---

## Required Work / 必需工作

1. **调查根本原因**
   - 检查 `OrderRepository.get_pre_transport_orders()` 的完整 SQL 查询
   - 检查 `tool_io_service.get_pre_transport_orders()` 如何调用 repository
   - 确认订单中存储运输人ID的字段名

2. **修复方案**
   - 在 SQL 查询中添加 `transport_assignee_id = current_user_id` 条件
   - 确保这个条件与 org_ids 条件是 OR 关系（能看到自己组织的 OR 分配给自己的）
   - 或者在 repository 返回结果后用 `order_matches_scope()` 过滤

3. **实施修复**
   - 修改 `OrderRepository.get_pre_transport_orders()` 添加 assignee 过滤
   - 或修改 `tool_io_service.get_pre_transport_orders()` 添加 scope 检查
   - 确保 SQL 使用参数化查询

4. **验证**
   - fengliang 调用 `GET /api/tool-io-orders/pre-transport` 可以看到分配给他的订单
   - fengliang 调用 `POST /api/tool-io-orders/{order_no}/transport-start` 可以成功启动运输
   - 其他运输操作员看不到不属于自己的订单

---

## Constraints / 约束条件

- 不得破坏组织数据隔离（运输操作员不能看到所有跨组织订单）
- 只应显示分配给当前用户的订单
- 使用 `column_names.py` 中的常量引用中文字段名
- 所有 SQL 必须使用参数化查询
- 不得修改 API 接口契约

---

## Completion Criteria / 完成标准

1. fengliang (PRODUCTION_PREP, DEPT_001) 调用 `GET /api/tool-io-orders/pre-transport` 可以看到分配给他的跨组织订单
2. fengliang 可以成功调用 `POST /api/tool-io-orders/{order_no}/transport-start` 启动运输
3. 其他运输操作员不能看到未分配给他们的订单
4. 运输工作流可以正常完成
