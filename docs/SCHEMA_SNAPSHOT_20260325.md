# Schema 快照 / Schema Snapshot

> **Date**: 2026-03-25
> **Purpose**: 记录 Schema 英语化重构后的实际数据库结构，作为后续开发的权威参考

---

## 1. 表名映射 (Table Name Mapping)

| 旧中文表名 | 新英文表名 | 状态 |
|-----------|-----------|------|
| 工装出入库单_主表 | `tool_io_order` | ✅ 已实现 |
| 工装出入库单_明细 | `tool_io_order_item` | ✅ 已实现 |
| 工装出入库单_操作日志 | `tool_io_operation_log` | ✅ 已实现 |
| 工装出入库单_通知记录 | `tool_io_notification` | ✅ 已实现 |
| 工装出入库单_位置 | `tool_io_location` | ✅ 已实现 |

---

## 2. 表结构 (Table Structures)

### 2.1 tool_io_order

**定义位置**: `backend/database/schema/schema_manager.py` lines 240-275

| 列名 (英文) | 类型 | Nullable | 说明 |
|------------|------|---------|------|
| `id` | BIGINT IDENTITY | NO | 主键，自增 |
| `order_no` | VARCHAR(64) | NO | 订单号，唯一 |
| `order_type` | VARCHAR(16) | NO | outbound/inbound |
| `order_status` | VARCHAR(32) | NO | 订单状态 |
| `initiator_id` | VARCHAR(64) | NO | 发起人ID |
| `initiator_name` | VARCHAR(64) | NO | 发起人姓名 |
| `initiator_role` | VARCHAR(32) | NO | 发起人角色 |
| `department` | VARCHAR(64) | YES | 部门 |
| `project_code` | VARCHAR(64) | YES | 项目代号 |
| `usage_purpose` | VARCHAR(255) | YES | 用途 |
| `planned_use_time` | DATETIME | YES | 计划使用时间 |
| `planned_return_time` | DATETIME | YES | 计划归还时间 |
| `target_location_id` | BIGINT | YES | 目标位置ID |
| `target_location_text` | VARCHAR(255) | YES | 目标位置文本 |
| `keeper_id` | VARCHAR(64) | YES | 保管员ID |
| `keeper_name` | VARCHAR(64) | YES | 保管员姓名 |
| `transport_type` | VARCHAR(32) | YES | 运输类型 |
| `transport_operator_id` | VARCHAR(64) | YES | 运输人ID |
| `transport_operator_name` | VARCHAR(64) | YES | 运输人姓名 |
| `keeper_confirm_time` | DATETIME | YES | 保管员确认时间 |
| `tool_quantity` | INT | NO | 工装数量 (**废弃** - 工装以序列号为主键，数量应由 items.length 计算) |
| `confirmed_count` | INT | NO | 已确认数量 |
| `final_confirm_by` | VARCHAR(64) | YES | 最终确认人 |
| `final_confirm_time` | DATETIME | YES | 最终确认时间 |
| `cancel_reason` | VARCHAR(500) | YES | 取消原因 |
| `reject_reason` | VARCHAR(500) | YES | 驳回原因 |
| `remark` | VARCHAR(500) | YES | 备注 |
| `org_id` | VARCHAR(64) | YES | 组织ID |
| `created_at` | DATETIME | NO | 创建时间 |
| `updated_at` | DATETIME | NO | 修改时间 |
| `created_by` | VARCHAR(64) | YES | 创建人 |
| `updated_by` | VARCHAR(64) | YES | 修改人 |
| `is_deleted` | TINYINT | NO | 软删除标记 |

**索引**:
- `IX_tool_io_order_order_no` on `(order_no)`
- `IX_tool_io_order_order_status` on `(order_status)`
- `IX_tool_io_order_created_at` on `(created_at)`

---

### 2.2 tool_io_order_item

**定义位置**: `backend/database/schema/schema_manager.py` lines 278-302

| 列名 (英文) | 类型 | Nullable | 说明 |
|------------|------|---------|------|
| `id` | BIGINT IDENTITY | NO | 主键，自增 |
| `order_no` | VARCHAR(64) | NO | 订单号（外键） |
| `tool_id` | BIGINT | YES | 工装ID |
| `tool_code` | VARCHAR(64) | NO | 工装编码 |
| `tool_name` | VARCHAR(255) | YES | 工装名称 |
| `drawing_no` | VARCHAR(255) | YES | 工装图号 |
| `spec_model` | VARCHAR(255) | YES | 规格型号 |
| `apply_qty` | DECIMAL(18,2) | NO | 申请数量 |
| `confirmed_qty` | DECIMAL(18,2) | NO | 确认数量 |
| `item_status` | VARCHAR(32) | NO | 明细状态 |
| `tool_snapshot_status` | VARCHAR(255) | YES | 工装快照状态 |
| `tool_snapshot_location_text` | VARCHAR(255) | YES | 工装快照位置文本 |
| `tool_snapshot_location_id` | BIGINT | YES | 工装快照位置ID |
| `confirm_by` | VARCHAR(255) | YES | 确认人 |
| `confirm_by_id` | BIGINT | YES | 确认人ID |
| `confirm_by_name` | VARCHAR(64) | YES | 确认人姓名 |
| `confirm_time` | VARCHAR(500) | YES | 确认时间 ⚠️ 警告：类型是 VARCHAR 而非 DATETIME |
| `reject_reason` | VARCHAR(500) | YES | 驳回原因 |
| `io_complete_time` | DATETIME | YES | 出入库完成时间 |
| `sort_order` | INT | NO | 排序号 |
| `created_at` | DATETIME | NO | 创建时间 |
| `updated_at` | DATETIME | NO | 修改时间 |

---

### 2.3 tool_io_operation_log

**定义位置**: `backend/database/schema/schema_manager.py` lines 305-318

| 列名 (英文) | 类型 | Nullable | 说明 |
|------------|------|---------|------|
| `id` | BIGINT IDENTITY | NO | 主键，自增 |
| `order_no` | VARCHAR(64) | NO | 订单号 |
| `item_id` | BIGINT | YES | 明细ID |
| `operation_type` | VARCHAR(64) | NO | 操作类型 |
| `operator_id` | VARCHAR(64) | YES | 操作人ID |
| `operator_name` | VARCHAR(64) | YES | 操作人姓名 |
| `operator_role` | VARCHAR(64) | YES | 操作人角色 |
| `from_status` | VARCHAR(64) | YES | 变更前状态 |
| `to_status` | VARCHAR(64) | YES | 变更后状态 |
| `operation_content` | TEXT | YES | 操作内容 |
| `operation_time` | DATETIME | NO | 操作时间 |

---

### 2.4 tool_io_notification

**定义位置**: `backend/database/schema/schema_manager.py` lines 321-336

| 列名 (英文) | 类型 | Nullable | 说明 |
|------------|------|---------|------|
| `id` | BIGINT IDENTITY | NO | 主键，自增 |
| `order_no` | VARCHAR(64) | NO | 订单号 |
| `notify_type` | VARCHAR(64) | NO | 通知类型 |
| `notify_channel` | VARCHAR(64) | YES | 通知渠道 |
| `receiver` | VARCHAR(255) | YES | 接收人 |
| `notify_title` | VARCHAR(255) | YES | 通知标题 |
| `notify_content` | TEXT | YES | 通知内容 |
| `copy_text` | TEXT | YES | 复制文本 |
| `send_status` | VARCHAR(32) | NO | 发送状态 |
| `send_time` | DATETIME | YES | 发送时间 |
| `send_result` | TEXT | YES | 发送结果 |
| `retry_count` | INT | NO | 重试次数 |
| `created_at` | DATETIME | NO | 创建时间 |

---

### 2.5 tool_io_location

**定义位置**: `backend/database/schema/schema_manager.py` lines 339-349

| 列名 (英文) | 类型 | Nullable | 说明 |
|------------|------|---------|------|
| `id` | BIGINT IDENTITY | NO | 主键，自增 |
| `location_code` | VARCHAR(64) | NO | 位置编码 |
| `location_name` | VARCHAR(255) | NO | 位置名称 |
| `location_desc` | VARCHAR(255) | YES | 位置描述 |
| `warehouse_area` | VARCHAR(64) | YES | 仓库区 |
| `storage_slot` | VARCHAR(64) | YES | 存储槽 |
| `shelf` | VARCHAR(255) | YES | 货架 |
| `remark` | VARCHAR(500) | YES | 备注 |

---

## 3. 不存在的列 (Non-Existent Columns)

以下列曾被 repository 代码引用，但**实际不存在于数据库中**：

| 列名 | 曾用于 | 说明 |
|------|--------|------|
| `keeper_demand_text` | ORDER 查询 | ❌ 不存在 |
| `transport_notify_text` | ORDER 查询 | ❌ 不存在 |
| `wechat_copy_text` | ORDER 查询 | ❌ 不存在 |
| `transport_notify_time` | ORDER 查询 | ❌ 不存在 (用 `notify_record.send_time`) |
| `位置ID` | 工装搜索 | ❌ 不存在于 `工装身份卡_主表` |

---

## 4. 已知问题 (Known Issues)

### 4.1 item.confirm_time 类型错误

**问题**: `tool_io_order_item.confirm_time` 定义为 `VARCHAR(500)` 而非 `DATETIME`

**影响**: 时间比较操作可能失败

**建议**: 后续修复为 `DATETIME` 类型

---

## 5. 权威常量来源 (Authoritative Constants)

所有列名常量定义在: `backend/database/schema/column_names.py`

```python
TABLE_NAMES = {
    'ORDER': 'tool_io_order',
    'ORDER_ITEM': 'tool_io_order_item',
    'ORDER_LOG': 'tool_io_operation_log',
    'ORDER_NOTIFICATION': 'tool_io_notification',
    'ORDER_LOCATION': 'tool_io_location',
}

ORDER_COLUMNS = {
    'order_no': 'order_no',
    'order_status': 'order_status',
    'keeper_id': 'keeper_id',
    'transport_operator_id': 'transport_operator_id',
    # ... 共 34 个字段
}

ITEM_COLUMNS = {
    'tool_code': 'tool_code',
    'item_status': 'item_status',
    'confirm_time': 'confirm_time',  # 注意：实际是 VARCHAR(500)
    # ...
}
```

---

## 6. 重构变更日志 (Refactoring Changelog)

| 日期 | 变更 | 文件 |
|------|------|------|
| 2026-03-25 | Repository 层 SQL 查询全面使用英文列名 | order_repository.py, tool_repository.py |
| 2026-03-25 | 移除不存在的列引用 (keeper_demand_text, transport_notify_text, wechat_copy_text) | order_repository.py |
| 2026-03-25 | 移除重复的 `[位置ID]` 条件 | tool_repository.py |
| 2026-03-25 | 所有表名使用 `TABLE_NAMES` 常量 | order_repository.py |

---

## 7. 下游消费者 (Downstream Consumers)

| 模块 | 使用方式 |
|------|---------|
| `order_repository.py` | 使用 `ORDER_COLUMNS`, `ITEM_COLUMNS`, `LOG_COLUMNS`, `NOTIFY_COLUMNS`, `TABLE_NAMES` |
| `tool_repository.py` | 使用 `TOOL_MASTER_COLUMNS` (外部表), `ORDER_COLUMNS`, `ITEM_COLUMNS`, `TABLE_NAMES` |
| 前端 `toolIO.js` | 使用 `pickValue()` 兼容中英文字段名 |
