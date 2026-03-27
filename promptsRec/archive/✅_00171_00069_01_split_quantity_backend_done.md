# 提示词 / Prompt

Primary Executor: Codex
Task Type: Feature Development
Priority: P1
Stage: 00069-01
Goal: Backend - JOIN Tooling_ID_Main to get split_quantity in get_order
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

工装主数据表 `Tooling_ID_Main`（工装身份卡_主表，外部系统表）中有一个"分体数量"字段（split_quantity），表示工装主体的拆分数量。

当前 `OrderRepository.get_order()` 方法只查询 `tool_io_order_item` 表获取 items，未联查工装主数据表。需要修改 SQL，LEFT JOIN `Tooling_ID_Main` 获取 `split_quantity` 字段。

---

## Required References / 必需参考

- `backend/database/schema/column_names.py`:
  - `TOOL_MASTER_COLUMNS['split_quantity']` = '分体数量'
  - `TOOL_MASTER_TABLE = "Tooling_ID_Main"`
  - `ITEM_COLUMNS['tool_code']` = 'tool_code'
- `backend/database/repositories/order_repository.py`:
  - `get_order()` 方法（第364-391行）
  - TABLE_NAMES['ORDER_ITEM'] 和 TABLE_NAMES 常量

---

## Core Task / 核心任务

修改 `OrderRepository.get_order()` 方法的 items SQL 查询，通过 LEFT JOIN `Tooling_ID_Main` 表获取每条明细的 `split_quantity`（分体数量）。

---

## Required Work / 必需工作

1. 在 `get_order()` 方法中，定位 items_sql 查询（约第383行）
2. 将 `SELECT * FROM [{TABLE_NAMES['ORDER_ITEM']}]` 改为带 LEFT JOIN 的查询：

```python
items_sql = f"""
    SELECT
        i.*,
        m.[{TOOL_MASTER_COLUMNS['split_quantity']}] AS split_quantity
    FROM [{TABLE_NAMES['ORDER_ITEM']}] i
    LEFT JOIN [{TOOL_MASTER_TABLE}] m
        ON i.[{ITEM_COLUMNS['tool_code']}] = m.[{TOOL_MASTER_COLUMNS['tool_code']}]
    WHERE i.[{ITEM_COLUMNS['order_no']}] = ?
    ORDER BY i.[{ITEM_COLUMNS['sort_order']}]
"""
```

3. 确保 `TOOL_MASTER_TABLE` 已导入（检查文件头部 import 语句）
4. 运行语法检查：`python -m py_compile backend/database/repositories/order_repository.py`

---

## Constraints / 约束条件

1. **字段名常量**：必须使用 `TOOL_MASTER_COLUMNS['split_quantity']` 引用字段，禁止硬编码中文
2. **外部表只读**：Tooling_ID_Main 是外部系统表，只做 SELECT LEFT JOIN，不修改
3. **保持兼容**：现有返回字段必须保留，split_quantity 作为额外字段追加

---

## Completion Criteria / 完成标准

1. items_sql 包含 LEFT JOIN Tooling_ID_Main 获取 split_quantity
2. `python -m py_compile` 语法检查通过
3. 后续前端任务可从 order.items[].split_quantity 读取到数据
