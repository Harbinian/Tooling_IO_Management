# 订单列表 UI 迁移 / Order List UI Migration

## 页面结构更改 / Page structure changes

订单列表页面现在使用更新的基于卡片的操作布局，而不是旧的密集 Element Plus 表格外壳。页面分为三个清晰的层：

The order list page now uses the newer card-based operational layout instead of the older dense Element Plus table shell. The page is split into three clear layers:

- 带摘要指标的轻量级页面头部 / a lightweight page header with summary metrics
- 专门的过滤器卡片 / a dedicated filter card
- 带列表行和分页控件的结果卡片 / a results card with list rows and paging controls

## 过滤器区域重新设计 / Filter area redesign

过滤器区域重建为结构化顶部面板，使用与 Mist 视觉系统匹配的原生输入。保留现有过滤器功能：

The filter area was rebuilt as a structured top panel with native inputs styled to match the Mist-inspired visual system. Existing filter capabilities were preserved:

- 关键字 / keyword
- 订单类型 / order type
- 订单状态 / order status
- 发起人ID / initiator ID
- 保管员ID / keeper ID
- 创建日期从 / created date from
- 创建日期至 / created date to

页面仍然将这些值作为查询参数发送到当前的 `/api/tool-io-orders` 请求。

The page still sends these values to the current `/api/tool-io-orders` request as query parameters.

## 列表呈现策略 / List presentation strategy

页面不再使用之前的密集管理表格，而是将每个订单呈现为结构化操作行。每行保持核心字段可见：

Instead of the previous grid-heavy admin table, the page now renders each order as a structured operational row. Each row keeps the core fields visible:

- 订单号 / order number
- 项目代号 / project code
- 工装数量 / tool count
- 目标位置 / target location
- 订单类型 / order type
- 发起人 / initiator
- 保管员 / keeper
- 订单状态 / order status
- 创建时间 / created time
- 操作 / actions

这提高了桌面端可扫描性，同时在较窄布局上保持可读性。

This improves scanability on desktop while remaining readable on narrower layouts.

## 状态显示策略 / Status display strategy

订单状态徽章现在通过共享的 `OrderStatusTag` 组件呈现，该组件包装了新的 UI `Badge` 组件。状态色调保持平静和操作导向：

Order status badges are now rendered through the `OrderStatusTag` component, which wraps the new UI `Badge` component. Status tones remain calm and operational:

- 板岩色用于中性或信息状态 / slate for neutral or informational states
- 琥珀色用于进行中或等待状态 / amber for in-progress or waiting states
- 翡翠绿用于成功状态 / emerald for successful states
- 天蓝色用于运输相关进度 / sky for transport-related progress
- 玫瑰红用于拒绝或风险状态 / rose for rejected or risky states

## 空、错误和加载状态 / Empty, error, and loading states

迁移后的页面现在提供明确的操作状态：

The migrated page now provides explicit operational states:

- 加载：骨架行而不是空白表格 / loading: skeleton rows instead of a blank table
- 错误：简洁的失败消息，带有单一重试操作 / error: concise failure message with a single retry action
- 无过滤器时为空：提示重新加载订单 / empty without filters: prompt to reload orders
- 有过滤器时为空：提示清除过滤器 / empty with filters: prompt to clear filters

## 重用的 UI 组件 / Reused UI components

页面重用先前迁移任务引入的共享前端 UI 基础：

The page reuses the shared frontend UI foundation introduced by the earlier migration tasks:

- `Button` / 按钮
- `Card` / 卡片
- `CardHeader` / 卡片头部
- `CardContent` / 卡片内容
- `CardTitle` / 卡片标题
- `Badge` / 徽章
- `OrderStatusTag` / 订单状态标签

## 与当前 API 的兼容性说明 / Compatibility notes with current API

未更改后端 API 契约。页面仍然使用：

No backend API contract was changed. The page still uses:

- `getOrderList` / 获取订单列表
- `submitOrder` / 提交订单
- `cancelOrder` / 取消订单
- `finalConfirmOrder` / 最终确认订单

路由导航现在指向活动库存路由：

Route navigation now points at the active inventory routes:

- `/inventory`
- `/inventory/:orderNo`

迁移还保留了提交、取消和最终确认的现有基于角色的操作守卫。

The migration also preserved the existing role-based action guards for submit, cancel, and final confirm.
