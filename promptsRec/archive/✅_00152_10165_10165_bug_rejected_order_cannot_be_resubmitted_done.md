# Bug Fix: Rejection-Resubmit Workflow Broken for Cancelled Orders

**Primary Executor**: Codex
**Task Type**: Bug Fix
**Priority**: P1 (HIGH)
**Stage**: 10165
**Goal**: Allow team leader to resubmit cancelled orders by resetting them to draft
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context / 上下文

E2E 测试发现拒绝-重提交工作流失效：

测试场景：
- taidongxu (TEAM_LEADER) 创建订单 TO-OUT-20260326-019
- taidongxu 提交订单，状态变为 submitted
- hutingting (KEEPER) 取消订单，状态变为 cancelled
- taidongxu 尝试重新提交订单
- 错误: "当前状态不允许提交：cancelled"

根本原因：`reset_order_to_draft()` 函数只允许从 `rejected` 状态重置，不允许从 `cancelled` 状态重置。

```python
# order_repository.py 第 811 行
if current_status != 'rejected':
    return {'success': False, 'error': f'只有被驳回的订单可以重置为草稿，当前状态：{current_status}'}
```

---

## Required References / 必需参考

1. `backend/database/repositories/order_repository.py` - `reset_order_to_draft()` 方法
2. `backend/database/repositories/order_repository.py` - `submit_order()` 方法
3. `backend/database/repositories/order_repository.py` - `cancel_order()` 方法
4. `backend/database/schema/column_names.py` - 中文字段名常量
5. `docs/DB_SCHEMA.md` - 数据库 Schema 文档

---

## Core Task / 核心任务

修复订单状态机，允许保管员取消的订单也能被发起人重置为草稿重新提交。

问题分析：
- `cancel_order()` 和 `reject_order()` 都将订单状态改为不可提交状态
- `cancel_order()` 设置状态为 `cancelled`
- `reject_order()` 设置状态为 `rejected`
- `reset_order_to_draft()` 只接受 `rejected` 状态

---

## Required Work / 必需工作

1. **调查根本原因**
   - 检查 `cancel_order()` 和 `reject_order()` 的区别
   - 确认 `cancel_reason` 和 `reject_reason` 字段的使用
   - 检查前端是否有取消订单的 UI 操作

2. **修复方案选择**:
   - **方案A**: 扩展 `reset_order_to_draft()` 同时接受 `cancelled` 和 `rejected` 状态
   - **方案B**: 在 `cancel_order()` 中将状态设置为 `rejected` 而不是 `cancelled`，并存储 cancel_reason 到 reject_reason
   - **方案C**: 创建一个新的 `reopen_order()` 函数专门处理取消订单的重开

3. **实施修复**（推荐方案A）:
   - 修改 `reset_order_to_draft()` 检查条件同时包含 `cancelled` 和 `rejected`
   - 确保只有订单发起人（initiator）才能重置自己的订单
   - 清空 cancel_reason/reject_reason 字段

4. **验证**
   - taidongxu 可以将已取消的订单重置为草稿
   - 重置后可以重新编辑和提交订单
   - 非发起人不能重置他人订单

---

## Constraints / 约束条件

- 只有订单发起人可以重置自己的订单
- 必须验证操作者身份
- 使用 `column_names.py` 中的常量引用中文字段名
- 所有 SQL 必须使用参数化查询
- 不得修改 API 接口契约
- 确保审计日志正确记录重置操作

---

## Completion Criteria / 完成标准

1. taidongxu 可以将已取消（cancelled）的订单重置为草稿
2. 重置后订单状态变为 `draft`，reject_reason/cancel_reason 被清空
3. 团队负责人可以编辑并重新提交重置后的订单
4. 只有订单发起人可以重置订单，非发起人操作被拒绝
5. 审计日志记录了重置操作的完整信息
