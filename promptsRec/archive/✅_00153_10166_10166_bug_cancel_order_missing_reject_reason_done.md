# Bug Fix: reject_reason Not Stored When Keeper Cancels Order

**Primary Executor**: Codex
**Task Type**: Bug Fix
**Priority**: P1 (HIGH)
**Stage**: 10166
**Goal**: Store cancel_reason in reject_reason field when keeper cancels an order
**Dependencies**: None
**Execution**: RUNPROMPT

---

## Context / 上下文

E2E 测试发现取消订单时取消原因未被存储：

测试场景：
- taidongxu (TEAM_LEADER) 创建并提交订单 TO-OUT-20260326-019
- hutingting (KEEPER) 取消订单并提供取消原因
- 检查数据库中 `reject_reason` 字段为 NULL

根本原因：`cancel_order()` 函数接收 `reason` 参数，但 UPDATE SQL 中没有将该值写入 `reject_reason` 字段。

```python
# order_repository.py 第 871-877 行
sql = f"""
UPDATE [{TABLE_NAMES['ORDER']}] SET
    [{ORDER_COLUMNS['order_status']}] = 'cancelled',
    [{ORDER_COLUMNS['updated_at']}] = GETDATE()
WHERE [{ORDER_COLUMNS['order_no']}] = ?
"""
# 注意：没有设置 reject_reason 字段！
```

---

## Required References / 必需参考

1. `backend/database/repositories/order_repository.py` - `cancel_order()` 方法
2. `backend/database/schema/column_names.py` - ORDER_COLUMNS 中 `reject_reason` 和 `cancel_reason` 定义
3. `backend/services/tool_io_service.py` - `cancel_order()` 函数调用
4. `docs/DB_SCHEMA.md` - 数据库 Schema 文档

---

## Core Task / 核心任务

修复 `cancel_order()` 函数，将 keeper 提供的取消原因存储到 `reject_reason` 字段。

---

## Required Work / 必需工作

1. **调查根本原因**
   - 检查 `cancel_order()` 方法的完整实现
   - 确认 `cancel_reason` 参数是否正确传递
   - 确认 `reject_reason` 和 `cancel_reason` 字段的区别和用途

2. **确认字段映射**
   - `ORDER_COLUMNS['reject_reason']` - 存储拒绝/取消原因
   - `ORDER_COLUMNS['cancel_reason']` - 可能用于其他场景
   - 检查 Schema 确定哪个字段用于存储取消原因

3. **实施修复**
   - 修改 `cancel_order()` UPDATE SQL，添加 `reject_reason` 字段的更新
   - 确保传递的 reason 参数被正确存储
   - 如果 `cancel_reason` 字段存在且应该存储cancel原因，也需要更新

4. **验证**
   - 调用 `cancel_order()` 时提供 reason
   - 确认数据库中 `reject_reason` 字段被正确更新
   - 确认 `tool_io_order` 表中可以看到取消原因
   - 确认审计日志记录了取消原因

---

## Constraints / 约束条件

- 不得修改数据库 Schema（字段已存在）
- 使用 `column_names.py` 中的常量引用中文字段名
- 所有 SQL 必须使用参数化查询
- 不得修改 API 接口契约
- 确保取消原因在 UI 上可以正确显示

---

## Completion Criteria / 完成标准

1. keeper 取消订单时提供的 cancel_reason 被存储到 `reject_reason` 字段
2. 调用 `GET /api/tool-io-orders/{order_no}` 可以看到 `reject_reason` 包含取消原因
3. 订单详情页可以正确显示取消原因
4. 审计日志记录了完整的取消信息
