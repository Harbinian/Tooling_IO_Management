# 订单详情 UI 迁移 / Order Detail UI Migration

## 布局重新设计摘要 / Layout redesign summary

订单详情页面被重建为更新的基于卡片的 Mist 风格布局。页面现在使用更平静的层次结构，包括：

The order detail page was rebuilt into the newer card-based Mist-style layout. The page now uses a calmer hierarchy with:

- 详情头部和操作区域 / a detail header and action area
- 两列概览和工作流部分 / a two-column overview and workflow section
- 专门的明细详情部分 / a dedicated item detail section
- 单独的审计和通知部分 / separate audit and notification sections
- 用于下游消息文本的预览卡片 / preview cards for downstream messaging text

## 订单信息部分设计 / Order info section design

页面头部和概览卡片以定义式块呈现订单标识符、状态和关键元数据。概览保持当前 API 字段可见，而不更改数据契约：

The page header and overview card present the order identifier, status, and key metadata in definition-style blocks. The overview keeps the current API fields visible without changing the data contract:

- 订单类型 / order type
- 发起人 / initiator
- 保管员 / keeper
- 项目代号 / project code
- 用途 / usage purpose
- 目标位置 / target location
- 创建时间 / created time
- 运输类型 / transport type
- 工装数量 / tool count
- 已确认数量 / approved count
- 部门 / department
- 备注 / remark

## 工作流追踪器设计 / Workflow tracker design

工作流区域现在使用轻量级进度卡片，而不是简单的详情表格。它使用当前仅支持的状态反映现有工作流语义：

The workflow area now uses a lightweight progress card instead of a plain detail table. It reflects the existing workflow semantics using currently supported statuses only:

- `draft` / 草稿
- `submitted` / 已提交
- `keeper_confirmed` / 保管员已确认
- `partially_confirmed` / 部分已确认
- `transport_notified` / 运输已通知
- `final_confirmation_pending` / 待最终确认
- `completed` / 已完成
- `rejected` / 已拒绝
- `cancelled` / 已取消

追踪器用平静的颜色处理表达完成、当前、即将到来和阻止的状态。

The tracker expresses complete, current, upcoming, and blocked states with calm color treatment.

## 工装明细部分设计 / Tool item section design

工装项目呈现为结构化操作行，而不是密集的 Element Plus 表格。每行保持当前 API 驱动的字段可读：

Tool items are rendered as structured operational rows instead of a dense Element Plus table. Each row keeps the current API-driven fields readable:

- 工装标识符或编码 / tool identifier or code
- 工装名称 / tool name
- 工装图号 / drawing number
- 规格或型号 / spec or model
- 申请数量 / requested quantity
- 已确认数量 / approved quantity
- 当前位置 / current location
- 保管员确认位置 / keeper-confirmed location
- 检查结果 / check result
- 明细状态徽章 / item status badge

## 审计日志呈现策略 / Audit log presentation strategy

操作日志区域现在使用垂直审计列表，包含时间戳、操作人、角色、操作和备注。这保持了工作流可追溯性可见，同时避免使用旧的 Element Plus 时间线外壳。

The operation log area now uses a vertical audit list with timestamp, operator, role, action, and remarks. This keeps workflow traceability visible while avoiding the older Element Plus timeline shell.

## 通知占位符策略 / Notification placeholder strategy

通知记录现在存在于专门部分，具有以下任一情况：

Notification records now live in a dedicated section with either:

- 当 API 返回记录时的结构化通知卡片 / structured notification cards when the API returns records
- 当尚无通知历史时的虚线空占位符 / a dashed empty placeholder when no notification history exists yet

页面还保留三个预览卡片，分别用于保管员文本、运输文本和微信复制文本。

The page also preserves three preview cards for keeper text, transport text, and WeChat copy text.

## 操作区域设计 / Action area design

操作区域保持与工作流兼容，仅显示后端支持的操作：

The action area remains workflow-compatible and only shows backend-supported actions:

- 提交 / submit
- 取消 / cancel
- 最终确认 / final confirm

这些操作仍然使用现有业务逻辑中的当前角色和状态守卫。

These actions still use the current role and status guards from the existing business logic.

## 与当前 API 的兼容性说明 / Compatibility notes with current API

未更改后端 API 或路由契约。迁移后的页面仍然使用：

No backend API or route contract was changed. The migrated page still uses:

- `getOrderDetail` / 获取订单详情
- `getOrderLogs` / 获取订单日志
- `generateKeeperText` / 生成保管员文本
- `generateTransportText` / 生成运输文本
- `submitOrder` / 提交订单
- `cancelOrder` / 取消订单
- `finalConfirmOrder` / 最终确认订单

路由保持为 `/inventory/:orderNo`，迁移保留了现有的工作流语义和响应结构。

The route remains `/inventory/:orderNo`, and the migration preserves the existing workflow semantics and response structure.
