Primary Executor: Gemini
Task Type: Bug Fix
Priority: P1
Stage: 10141
Goal: Fix order list click navigates to dashboard instead of order detail
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

**问题描述**：
- 胡婷婷在订单列表页面能看到出库订单 TO-OUT-20260324-005
- 点击该订单后，前端跳转到仪表盘（dashboard）而不是订单详情页（order detail）

**期望行为**：
- 点击订单应该导航到 `/tool-io-orders/{order_no}` 或 `/inventory/{order_no}`

---

## Required References / 必需参考

1. `frontend/src/pages/tool-io/OrderList.vue` - 订单列表页面
2. `frontend/src/router/index.js` - 路由配置
3. `frontend/src/api/orders.js` - 订单 API 调用
4. `docs/ARCHITECTURE.md` - 前端架构文档

---

## Core Task / 核心任务

调查并修复订单列表点击事件跳转到错误页面的问题。

---

## Required Work / 必需工作

### 1. 调查阶段

1.1 检查 OrderList.vue 中的订单点击处理逻辑：
- 查找 `@click`、`:href`、`<router-link>` 或 `navigateTo` 相关代码
- 确认点击事件的处理函数

1.2 检查路由配置：
- 确认订单详情页的路由路径
- 确认路由参数名称（是 `order_no` 还是 `id` 或其他）

1.3 检查是否有权限检查导致的重定向：
- 查看 `Permission.js` 或权限指令
- 检查是否有未授权时重定向到仪表盘的逻辑

### 2. 修复阶段

根据调查结果修复：
- 如果是路由路径错误，修正路由
- 如果是权限检查问题，修正权限逻辑
- 如果是参数传递错误，修正点击事件处理

### 3. 验证

- 确认点击订单可以正确导航到订单详情页
- 确认导航后页面显示正确的订单信息

---

## Constraints / 约束条件

1. 不破坏现有的 UI 样式和组件结构
2. 遵循项目 CSS 变量使用规范
3. 不引入新的安全问题

---

## Completion Criteria / 完成标准

1. 点击订单列表中的订单，导航到订单详情页
2. 订单详情页显示正确的订单信息
3. 不出现 403/401 等权限错误（除非用户确实无权限）
