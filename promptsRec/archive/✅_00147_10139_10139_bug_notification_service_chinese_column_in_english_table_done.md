# Bug Fix: notification_service.py 使用中文列名查询英文字段表

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10139
Goal: 修复 notification_service.py 中使用中文列名查询内部英文表的一致性问题
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

Codex Review 报告 (Codex_Review20260326_SQL_Chinese_Identifiers.md) 发现了一个高优先级问题：

- **位置**: `backend/services/notification_service.py:327`
- **问题**: SQL 查询使用 `FROM tool_io_notification`（内部英文字段表），但 WHERE 条件使用 `WHERE 出入库单号 = ?`（中文列名）
- **影响**: `tool_io_notification` 是本系统的内部表，其字段已统一使用英文字段名。此处使用中文列名会导致查询失败或数据不一致

内部表 `tool_io_notification` 的正确列名应为 `order_no`（参见 `NOTIFY_COLUMNS` 常量）。

---

## Required References / 必需参考

1. `backend/database/schema/column_names.py` - 查看 `NOTIFY_COLUMNS` 常量定义
2. `backend/services/notification_service.py` - 检查问题代码位置

---

## Core Task / 核心任务

修复 `notification_service.py` 中第 327 行的 SQL 查询，将 WHERE 子句中的中文列名 `出入库单号` 替换为英文字段名 `order_no`。

---

## Required Work / 必需工作

1. **检查 `NOTIFY_COLUMNS` 常量**：
   - 确认 `tool_io_notification` 表的英文字段名
   - 确认 `order_no` 字段的正确引用方式

2. **修复 SQL 查询**：
   - 将 `WHERE 出入库单号 = ?` 修改为使用英文字段名
   - 可选：使用 `NOTIFY_COLUMNS['order_no']` 常量以保持一致性

3. **验证修改**：
   - 执行 `python -m py_compile backend/services/notification_service.py` 确认语法正确

---

## Constraints / 约束条件

- 只修改 `notification_service.py` 中涉及 `tool_io_notification` 表的中文列名
- 外部系统表（如 `工装验收管理_主表`）的中文列名保持不变
- 使用 `NOTIFY_COLUMNS` 常量或直接使用英文字段名 `order_no`
- 不要修改其他文件的代码

---

## Completion Criteria / 完成标准

1. `backend/services/notification_service.py` 第 327 行的 WHERE 子句使用英文字段名 `order_no`
2. `python -m py_compile backend/services/notification_service.py` 语法检查通过
3. 如果同一文件其他位置存在类似问题（使用中文列名查询英文字段内部表），一并修复
