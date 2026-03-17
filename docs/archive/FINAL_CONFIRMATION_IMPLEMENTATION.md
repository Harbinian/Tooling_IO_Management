# 最终确认实现 / Final Confirmation Implementation

## Schema 检查摘要 / Schema inspection summary

最终确认工作流继续使用当前工装出入库工作流已使用的现有 SQL Server 表：

The final confirmation workflow continues to use the existing SQL Server tables already used by the current Tool IO workflow:

- `工装出入库单_主表` 用于订单头状态 / for order header state
- `工装出入库单_明细` 用于明细级状态 / for item-level state
- `工装出入库单_操作日志` 用于操作日志 / for operation logs

运行时详情路径已公开最终确认决策所需的字段：

The runtime detail path already exposes the fields needed for final confirmation decisions:

- 订单号 / order number
- 订单类型 / order type
- 订单状态 / order status
- 发起人ID / initiator id
- 保管员ID / keeper id
- 已确认数量 / approved count

现有数据库写入路径已更新：

The existing database write path already updates:

- 订单状态 / order status
- 最终确认人字段 / final confirmer field
- 最终确认时间 / final confirmation time
- 已确认明细行为 `completed` / approved item rows to `completed`
- 操作日志记录 / operation log records

## 资格规则 / Eligibility rules

服务层现在在调用现有数据库写入函数之前评估最终确认资格。

The service layer now evaluates final confirmation eligibility before calling the existing database write function.

当前服务级允许的状态：

Current service-level allowed statuses:

- `transport_notified` / 运输已通知
- `final_confirmation_pending` / 待最终确认

服务层拒绝：

The service rejects:

- 缺失订单 / missing orders
- 已完成订单 / completed orders
- 不支持的订单类型 / unsupported order types
- 错误角色 / wrong roles
- 当订单已分配发起人或保管员时，操作人身份不匹配 / mismatched operator identity when the order already has an assigned initiator or keeper

## 出库确认规则 / Outbound confirmation rule

出库订单只能由发起人角色最终确认。

Outbound orders can be finally confirmed only by the initiator role.

验证行为：

Validation behavior:

- `operator_role` 必须是 `initiator` / must be `initiator`
- 如果订单有 `initiator_id`，`operator_id` 必须匹配 / if the order has `initiator_id`, `operator_id` must match it
- 当前状态必须是 `transport_notified` 或 `final_confirmation_pending` / current status must be `transport_notified` or `final_confirmation_pending`

## 入库确认规则 / Inbound confirmation rule

入库订单只能由保管员角色最终确认。

Inbound orders can be finally confirmed only by the keeper role.

验证行为：

Validation behavior:

- `operator_role` 必须是 `keeper` / must be `keeper`
- 如果订单有 `keeper_id`，`operator_id` 必须匹配 / if the order has `keeper_id`, `operator_id` must match it
- 当前状态必须是 `transport_notified` 或 `final_confirmation_pending` / current status must be `transport_notified` or `final_confirmation_pending`

## 已实现或更新的 API / APIs implemented or updated

更新的后端端点：

Updated backend endpoints:

- `POST /api/tool-io-orders/<order_no>/final-confirm`
  - 现在在调用现有数据库写入器之前执行服务层资格验证 / now performs service-layer eligibility validation before calling the existing database writer
  - 确认后返回更新的订单详情 / returns updated order detail after confirmation

- `GET /api/tool-io-orders/<order_no>/final-confirm-availability`
  - 返回当前请求角色和操作人是否可进行最终确认 / returns whether final confirmation is currently available for the requesting role and operator
  - 响应包含当前状态、订单类型、预期角色和不可用时的拒绝原因 / response includes current status, order type, expected role, and rejection reason when unavailable

## 前端页面集成 / Frontend page integration

更新的前端集成点：

Updated frontend integration points:

- `frontend/src/pages/tool-io/OrderDetail.vue`
  - 现在调用 `getFinalConfirmAvailability` / now calls `getFinalConfirmAvailability`
  - 仅在后端确认可用时显示最终确认操作 / only shows the final confirmation action when the backend confirms availability
  - 最终确认后刷新详情页 / refreshes the detail page after final confirmation

- `frontend/src/api/toolIO.js`
  - 现在暴露 `getFinalConfirmAvailability` / now exposes `getFinalConfirmAvailability`

保管员工作台脚本路径也已准备好读取可用性并与共享 API 包装器一致地提交最终确认。

The keeper workbench script path was also prepared to read availability and submit final confirmation consistently with the shared API wrapper.

## 状态转换行为 / State transition behavior

工作流保持现有终态：

The workflow preserves the existing terminal state:

- `transport_notified` -> `completed`
- `final_confirmation_pending` -> `completed`

现有数据库写入路径继续：

The existing database write path continues to:

- 设置订单头状态为 `completed` / set the order header status to `completed`
- 记录最终确认元数据 / record final confirmation metadata
- 将已确认的明细行标记为 `completed` / mark approved item rows as `completed`

## 操作日志行为 / Operation logging behavior

操作日志继续由现有的最终确认数据库函数处理。

Operation logging remains handled by the existing final confirmation database function.

它记录：

It records:

- 订单号 / order number
- 操作人ID / operator id
- 操作人姓名 / operator name
- 操作人角色 / operator role
- 操作类型 / action type
- 前一状态 / previous status
- 下一状态 / next status
- 操作时间戳 / operation timestamp

## Schema 限制和假设 / Schema limitations and assumptions

- 运行时安全读取路径和遗留数据库写入路径被有意混合，以在保持与现有 SQL Server 工作流实现兼容性的同时最小化风险。/ The runtime-safe read path and the legacy database write path are mixed intentionally to minimize risk while preserving compatibility with the existing SQL Server workflow implementation.
- 当前工作流已包含更广泛的遗留最终确认写入器，但服务层现在将 UI/API 资格缩小到当前前端工作流期望的运输完成阶段。/ The current workflow already contains a broader legacy final-confirm writer, but the service layer now narrows UI/API eligibility to the transport-complete stages that the current frontend workflow expects.
- 本任务未添加新的 schema 字段。/ No new schema fields were added in this task.
