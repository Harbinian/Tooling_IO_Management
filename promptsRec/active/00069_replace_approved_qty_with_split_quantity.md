# 提示词 / Prompt

Primary Executor: Codex
Task Type: Feature Development
Priority: P2
Stage: 00069
Goal: Replace "approved quantity" field with "split quantity" in keeper workflow
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

在保管员工作台（KeeperProcess.vue）中，仍显示"批准数量"（approvedQty）字段供保管员手动输入。但该字段已被取消，需要改为显示工装主数据表（Tooling_ID_Main）中的"分体数量"（split_quantity）字段。

分体数量代表工装主体的拆分数量——某一套工装可能由多个主体构成，使用时装配好，使用后需拆开存放。此字段由数据库提供，保管员无需手动填写。

业务要求：
1. 保管员工作台的工装明细确认页面显示分体数量（只读）
2. 订单详情页面（生产准备工页面）也需显示分体数量
3. API payload 中的 approved_qty 改用 split_quantity 的值

---

## Required References / 必需参考

- `backend/database/schema/column_names.py` - TOOL_MASTER_COLUMNS 中定义 `split_quantity` = '分体数量'
- `backend/database/repositories/order_repository.py` - get_order() 方法，当前只查询 tool_io_order_item 表
- `frontend/src/pages/tool-io/KeeperProcess.vue` - 保管员工作台，第181行表头"批准数量"，第202-212行输入框
- `frontend/src/pages/tool-io/OrderDetail.vue` - 订单详情，第193-194行显示"确认数量"
- `TOOL_MASTER_TABLE = "Tooling_ID_Main"`（工装身份卡_主表，外部系统表）

---

## Core Task / 核心任务

### 1. 后端修改 - order_repository.py

修改 `OrderRepository.get_order()` 方法（第364-391行），在查询 items 时**联查** `Tooling_ID_Main` 表获取 `split_quantity` 字段。

### 2. 前端修改 - KeeperProcess.vue

- 第181行表头：`批准数量` → `分体数量`
- 第202-212行：将输入框改为只读显示 `item.split_quantity`
- buildEditableItems 函数：移除 approvedQty 相关逻辑
- approveOrder payload：approved_qty 改用 `item.split_quantity`

### 3. 前端修改 - OrderDetail.vue

- 第193-194行：将"确认数量"字段的显示从 `item.approvedQty` 改为 `item.split_quantity`

---

## Required Work / 必需工作

### 后端 (Codex)

1. 修改 `backend/database/repositories/order_repository.py` 的 `get_order()` 方法
2. 将 items_sql 从直接查询 `tool_io_order_item` 改为 LEFT JOIN `Tooling_ID_Main` 获取分体数量
3. 使用 `TOOL_MASTER_COLUMNS['split_quantity']` 引用字段（值为 '分体数量'）
4. 验证语法：`python -m py_compile backend/database/repositories/order_repository.py`

### 前端 (Gemini)

1. **KeeperProcess.vue**:
   - 第181行表头：`<th>批准数量</th>` → `<th>分体数量</th>`
   - 第202-212行单元格：移除 Input 输入框，改为只读文本显示 `{{ item.split_quantity || '-' }}`
   - buildEditableItems 函数：移除 `approvedQty: defaultApprovedQty` 行
   - approveOrder payload：第718行 `approved_qty: item.status === 'approved' ? item.approvedQty || item.applyQty || 1 : 0` 改为 `approved_qty: item.status === 'approved' ? item.split_quantity || item.applyQty || 1 : 0`

2. **OrderDetail.vue**:
   - 第193-194行：`确认数量` 显示从 `{{ item.approvedQty ?? '-' }}` 改为 `{{ item.split_quantity ?? '-' }}`

3. 验证前端构建：`cd frontend && npm run build`

---

## Constraints / 约束条件

1. **字段名常量**：所有 SQL 中的中文字段名必须使用 `column_names.py` 中定义的常量，禁止直接使用中文字面量
2. **外部表只读**：Tooling_ID_Main 是外部系统表，只做 SELECT 联查，不修改
3. **零退化**：不得破坏现有 UI 样式和工作流逻辑
4. **只读字段**：分体数量由数据库提供，保管员不能修改
5. **API 兼容**：approved_qty 字段保留但使用 split_quantity 的值，确保后端兼容

---

## Completion Criteria / 完成标准

1. 后端 `get_order()` 方法成功联查 Tooling_ID_Main 表返回 `split_quantity` 字段
2. KeeperProcess.vue 页面表头显示"分体数量"，单元格显示只读值
3. OrderDetail.vue 页面"确认数量"改为显示分体数量
4. approveOrder API payload 中的 approved_qty 使用 split_quantity 值
5. 前端构建成功，无语法错误
6. 保管员工作台功能正常工作，分体数量正确显示
