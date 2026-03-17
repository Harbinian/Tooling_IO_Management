Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 130
Goal: Fix order API to return tool_count and approved_count fields
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述

用户要求在订单列表和详情页显示工装数量，便于班组长、保管员通过数量建立直观认识。

前端已有显示逻辑：
- `OrderList.vue` 第210行显示 `工装 {{ order.toolCount || 0 }}`
- `OrderDetail.vue` 第368行显示 `toolCount` (工装数量)
- `OrderDetail.vue` 第369行显示 `approvedCount` (已确认数量)

前端 API 规范化函数 `toolIO.js` 第53-54行期望字段：
```javascript
toolCount: Number(pickValue(record, ['tool_count', '工装数量'], 0)) || 0,
approvedCount: Number(pickValue(record, ['approved_count', '已确认数量'], 0)) || 0,
```

但后端 `order_repository.py` 的 `get_orders()` 方法使用的显式 SELECT 列列表中**不包含** `工装数量` 和 `已确认数量`。

### 问题根因

1. `order_repository.py:get_orders()` (line 351-384) 的显式列列表缺少：
   - `[工装数量] AS [tool_count]`
   - `[已确认数量] AS [approved_count]`

2. `tool_io_service.py:_normalize_runtime_order()` (line 686-706) 没有将原始记录的 `tool_count` 映射到输出

---

## Required References / 必需参考

### 数据库 Schema
- `backend/database/schema/schema_manager.py`:
  - Line 177: `[已确认数量] INT NOT NULL DEFAULT 0` (CREATE TABLE 中已定义)
  - Line 178: `[最终确认人] VARCHAR(64) NULL` (CREATE TABLE 中已定义)
  - Line 183: `[org_id] VARCHAR(64) NULL` (CREATE TABLE 中已定义)
  - **注意**: `工装数量` 在 CREATE TABLE 中缺失，但 `_build_schema_alignment_sql()` (line 63) 会通过 ALTER TABLE 补齐

### 关键代码文件
- `backend/database/repositories/order_repository.py`:
  - Line 98, 119: INSERT 语句包含 `[工装数量]` 和 `[org_id]` 列
  - Line 120: INSERT 语句包含 `[org_id]`
  - Line 351-384: `get_orders()` 方法的显式列列表
  - Line 484-485: `keeper_confirm()` 更新 `[已确认数量]`
  - Line 552: `final_confirm()` 更新 `[最终确认人]`
  - Line 775: `delete_order()` 重置 `[已确认数量]` 为 0

- `backend/services/tool_io_service.py`:
  - Line 686-706: `_normalize_runtime_order()` 方法

### 前端期望字段
- `frontend/src/api/tools.js`: `normalizeOrder` 函数期望 `toolCount` 和 `approvedCount`

---

## Core Task / 核心任务

修复订单 API，使其返回 `tool_count` 和 `approved_count` 字段，让前端能够正确显示工装数量。

---

## Required Work / 必需工作

### 1. 修改 `order_repository.py` 的 `get_orders()` 方法

在 `backend/database/repositories/order_repository.py` 的 `get_orders()` 方法中，找到显式列列表 (line 351-384)，添加以下两列：

```python
"[工装数量] AS [tool_count]",
"[已确认数量] AS [approved_count]",
```

**注意**: 列必须添加到 WHERE 子句之前的位置，与其他列保持一致格式。

### 2. 修改 `tool_io_service.py` 的 `_normalize_runtime_order()` 方法

在 `backend/services/tool_io_service.py` 的 `_normalize_runtime_order()` 方法中，确保 `tool_count` 被正确映射到输出。

检查当前实现，如果缺少则添加：
```python
"tool_count": _pick_value(order, ["tool_count", "工装数量"], 0),
```

### 3. 验证修改

修改完成后，运行以下验证：
1. 后端语法检查：`python -m py_compile backend/database/repositories/order_repository.py backend/services/tool_io_service.py`
2. 检查 API 响应是否包含 `tool_count` 和 `approved_count` 字段

---

## Constraints / 约束条件

1. **不要修改** `database.py` 中的 `__all__` 导出列表
2. **不要修改** 数据库 schema（字段已存在或通过 schema alignment 自动补齐）
3. **不要修改** 前端代码（前端已正确期望这些字段）
4. **保持** `get_orders()` 的分页逻辑不变
5. **保持** `get_order()` 使用 `SELECT *` 的现有行为
6. **使用** 英文变量名和注释

---

## Completion Criteria / 完成标准

1. ✅ `GET /api/tool-io-orders` 返回的数据包含 `tool_count` 和 `approved_count` 字段
2. ✅ `GET /api/tool-io-orders/<order_no>` 返回的数据包含 `tool_count` 和 `approved_count` 字段
3. ✅ 后端语法检查通过：`python -m py_compile backend/database/repositories/order_repository.py backend/services/tool_io_service.py`
4. ✅ 前端订单列表页面能正确显示工装数量（不显示为0或undefined）
5. ✅ 前端订单详情页面能正确显示工装数量和已确认数量
