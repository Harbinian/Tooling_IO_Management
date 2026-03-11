# 保管员确认实现 / Keeper Confirmation Implementation

## 使用的表 / Tables Used

此工作流使用运行时架构中已定义的现有 SQL Server 表。

This workflow uses the existing SQL Server tables already defined in the runtime schema.

- `工装出入库单_主表`：订单头表 / order header table
- `工装出入库单_明细`：订单明细表 / order item table
- `工装出入库单_操作日志`：操作日志表 / operation log table
- `工装出入库单_通知记录`：通知记录表 / notification record table

## Schema 检查摘要 / Schema Inspection Summary

实现遵循 `docs/DB_SCHEMA.md` 和 `docs/SQLSERVER_SCHEMA_REVISION.md` 中记录的现有运行时架构。

The implementation follows the existing runtime schema documented in `docs/DB_SCHEMA.md` and `docs/SQLSERVER_SCHEMA_REVISION.md`.

保管员处理使用的头字段：

Header fields used by keeper processing:

- 订单号 / order number
- 订单类型 / order type
- 订单状态 / order status
- 保管员ID/姓名 / keeper id/name
- 运输类型 / transport type
- 运输操作人ID/姓名 / transport operator id/name
- 保管员确认时间 / keeper confirm time
- 已确认数量 / confirmed count
- 备注 / remark
- 创建/更新时间 / created/updated time

保管员处理使用的明细字段：

Item fields used by keeper processing:

- 工装编码 / tool code
- 工装名称 / tool name
- 申请数量 / apply quantity
- 已确认数量 / confirmed quantity
- 明细状态 / item status
- 位置快照文本 / snapshot location text
- 保管员确认位置文本 / keeper confirm location text
- 保管员检查结果 / keeper check result
- 保管员检查备注 / keeper check remark
- 确认时间 / confirm time

使用的日志字段：

Log fields used:

- 订单号 / order number
- 明细ID / item id
- 操作类型 / action type
- 操作人ID/姓名/角色 / operator id/name/role
- 前状态 / before status
- 后状态 / after status
- 操作内容 / operation content
- 操作时间 / operation time

## 保管员待处理订单规则 / Keeper Pending Order Rule

保管员待处理订单从 `工装出入库单_主表` 查询，使用：

Keeper pending orders are queried from `工装出入库单_主表` with:

- `单据状态 IN ('submitted', 'partially_confirmed')`
- `IS_DELETED = 0`
- 可选的保管员过滤：分配的保管员匹配当前保管员或订单仍未分配 / optional keeper filter: assigned keeper matches current keeper or the order is still unassigned

这使工作台与项目已使用的实际运行时状态保持一致。

This keeps the workbench aligned with the actual runtime statuses already used by the project.

## 已实现或更新的 API / APIs Implemented or Updated

保留现有路由。服务层现在通过 `backend/services/tool_io_runtime.py` 路由保管员特定的读取和确认写入。

Existing routes are preserved. The service layer now routes keeper-specific reads and confirmation writes through `backend/services/tool_io_runtime.py`.

更新的运行时行为：

Updated runtime behavior:

- `GET /api/tool-io-orders/pending-keeper`
  - 返回保管员待处理订单 / returns keeper-pending orders
- `GET /api/tool-io-orders/<order_no>`
  - 返回头、明细行和通知记录 / returns header, item rows, and notification records
- `GET /api/tool-io-orders/<order_no>/logs`
  - 返回按最新排序的操作日志 / returns operation logs ordered by latest first
- `POST /api/tool-io-orders/<order_no>/keeper-confirm`
  - 验证提交的明细载荷并持久化保管员确认 / validates submitted item payload and persists keeper confirmation

## 请求和响应结构 / Request and Response Structure

### 保管员确认请求 / Keeper Confirm Request

```json
{
  "keeper_id": "U1001",
  "keeper_name": "Keeper User",
  "transport_type": "manual",
  "transport_assignee_id": "U2001",
  "transport_assignee_name": "Transport User",
  "keeper_remark": "checked on site",
  "items": [
    {
      "tool_code": "T-01",
      "location_id": null,
      "location_text": "A-01",
      "check_result": "approved",
      "check_remark": "ready",
      "approved_qty": 1,
      "status": "approved"
    }
  ],
  "operator_id": "U1001",
  "operator_name": "Keeper User",
  "operator_role": "keeper"
}
```

### 保管员确认响应 / Keeper Confirm Response

```json
{
  "success": true,
  "status": "keeper_confirmed",
  "approved_count": 1
}
```

验证规则：

Validation rules:

- 订单必须存在且未删除 / the order must exist and not be deleted
- 订单状态必须是 `submitted` 或 `partially_confirmed` / the order status must be `submitted` or `partially_confirmed`
- `items` 必须是非空数组 / `items` must be a non-empty array
- 每个明细必须有唯一的 `tool_code` / each item must have a unique `tool_code`
- 每个 `tool_code` 必须已属于目标订单 / each `tool_code` must already belong to the target order
- 明细状态必须是 `approved` 或 `rejected` / item status must be `approved` or `rejected`
- 已确认数量必须是数值且非负 / approved quantity must be numeric and non-negative

## 前端页面更改 / Frontend Page Changes

`frontend/src/pages/tool-io/KeeperProcess.vue` 现在支持：

`frontend/src/pages/tool-io/KeeperProcess.vue` now supports:

- 加载保管员待处理订单 / loading pending keeper orders
- 选择一个订单并显示基本订单信息 / selecting one order and showing basic order information
- 编辑明细级确认位置、状态、数量和备注 / editing item-level confirm location, status, quantity, and remark
- 输入运输类型、运输指派人 / entering transport type, transport assignee
- 保管员备注 / and keeper remark
- 为 `submitted` 和 `partially_confirmed` 订单提交保管员确认 / submitting keeper confirmation for both `submitted` and `partially_confirmed` orders
- 预览运输通知文本 / previewing transport notification text
- 在同一工作台拒绝订单或发送运输通知 / rejecting an order or sending the transport notification from the same workbench

`frontend/src/utils/toolIO.js` 已更新以一致地规范化保管员特定的明细字段和通知记录。

`frontend/src/utils/toolIO.js` was updated to normalize keeper-specific item fields and notification records consistently.

## 使用的状态转换 / Status Transition Used

实现保持现有工作流状态。

The implementation keeps the existing workflow states.

- 保管员工作台范围：`submitted`、`partially_confirmed` / pending keeper workbench scope: `submitted`, `partially_confirmed`
- 保管员确认结果：/ keeper confirm result:
  - 全部明细批准 -> `keeper_confirmed` / all items approved -> `keeper_confirmed`
  - 混合批准/拒绝 -> `partially_confirmed` / mixed approved/rejected items -> `partially_confirmed`
- 完全拒绝仍由现有拒绝 API 处理 -> `rejected` / full rejection remains handled by the existing reject API -> `rejected`

## 日志行为 / Logging Behavior

保管员确认写入一条操作日志记录到 `工装出入库单_操作日志`，包含：

Keeper confirmation writes one operation log record into `工装出入库单_操作日志` with:

- 订单号 / order number
- 操作类型 `ToolIOAction.KEEPER_CONFIRM` / action type `ToolIOAction.KEEPER_CONFIRM`
- 操作人ID/姓名/角色 / operator id/name/role
- 前一订单状态 / previous order status
- 下一订单状态 / next order status
- 包含已确认明细数量的摘要内容 / summary content including approved item count
- 存在时的保管员备注 / keeper remark when present

详情页通过 `GET /api/tool-io-orders/<order_no>/logs` 读取这些日志。

The detail page reads those logs back through `GET /api/tool-io-orders/<order_no>/logs`.

## Schema 限制和假设 / Schema Limitations and Assumptions

- 当前架构公开明细级保管员备注和检查结果，但只有一个通用订单级 `remark` 字段。新运行时路径将顶级保管员备注记录在操作日志中，而不是创建新的头列。/ The current schema exposes item-level keeper remarks and check results, but only a generic order-level `remark` field. The new runtime path records top-level keeper remarks in the operation log instead of inventing a new header column.
- 保管员页面使用订单头部的现有运输指派字段，而不是创建单独的运输表。/ The keeper page uses existing transport assignment fields on the order header instead of creating a separate transport table.
- 通知记录从现有通知表读取并作为 `notification_records` 返回，以实现稳定的前端规范化。/ Notification records are read from the existing notification table and returned as `notification_records` for stable frontend normalization.
