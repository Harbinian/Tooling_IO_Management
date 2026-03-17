# 00059 准备工预知运输任务功能 - 前端实现

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 00059
Goal: 实现准备工预知列表页面（查看已提交但未审批的订单）
Dependencies: 00059_pre_transport_visibility_backend (后端必须先完成)
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
班组长可以看到订单执行进度。生产准备工（Production Prep）也希望能提前看到已提交但保管员未审批的申请，这样准备工们能有心理准备，知道有哪些运输任务即将到来。

### 目标用户
- 生产准备工：查看即将到来的运输任务

### 核心痛点
当前 Production Prep 无法提前获知即将到来的运输任务，只有在 Keeper 确认并指派后才能看到。

### 业务目标
1. Production Prep 可查看"预知列表"页面
2. 列表包含已提交但 Keeper 还没确认的订单
3. 列表包含 Keeper 已确认、等待运输的订单
4. 界面符合深色主题 Element Plus 规范

---

## Required References / 必需参考

- frontend/src/pages/OrderList.vue - 订单列表页参考
- frontend/src/api/orderApi.js - 订单API调用
- .claude/rules/30_gemini_frontend.md - 前端设计协议

---

## Core Task / 核心任务

### 1. 新建预知列表页面

**路由**: `/pre-transport` 或在现有页面中添加 Tab
**组件**: PreTransportList.vue 或 PreTransportTab.vue

### 2. 页面布局

```
+------------------------------------------+
| 预知运输任务                    [刷新]   |
+------------------------------------------+
| 状态标签筛选:                           |
| [全部] [已提交] [已确认待运输]           |
+------------------------------------------+
| 订单号    | 类型 | 目的地 | 状态  | 预计时间 |
|----------|------|--------|------|---------|
| IO2026... | 出库 | 车间A3 | 已提交| --      |
| IO2026... | 出库 | 车间B2 | 已确认| 14:00   |
+------------------------------------------+
|                                     分页 |
+------------------------------------------+
```

### 3. 列表项显示

| 字段 | 组件 | 说明 |
|------|------|------|
| order_no | 链接 | 点击跳转订单详情 |
| order_type | Tag | 出库=primary, 入库=success |
| destination | 文本 | 目的地 |
| status | Tag | 已提交=warning, 已确认=info, 已通知=primary |
| submit_time | 文本 | 格式: MM-DD HH:mm |
| keeper_confirmed_time | 文本 | 如有 |
| estimated_transport_time | 文本 | 如有 |

### 4. 状态筛选

- 全部: 显示所有状态
- 已提交: `status = 'submitted'`
- 已确认待运输: `status IN ('keeper_confirmed', 'transport_notified')`

---

## Required Work / 必需工作

1. **API层**
   - 在 `frontend/src/api/orderApi.js` 添加:
     - `getPreTransportOrders(params)`

2. **页面组件**
   - 创建 `frontend/src/pages/PreTransportList.vue`
   - 或在 OrderList.vue 中添加 Tab

3. **路由配置**
   - 在 `frontend/src/router/index.js` 添加路由

4. **权限控制**
   - Production Prep 角色: 显示预知列表菜单/Tab
   - 其他角色: 不显示相关入口

5. **状态管理**
   - 使用 Pinia store 管理预知列表状态

6. **UI一致性**
   - 使用 CSS 变量，禁止硬编码颜色
   - 符合深色主题 Element Plus 规范

---

## Constraints / 约束条件

1. **权限控制**: 基于当前用户角色动态显示功能
2. **CSS规范**: 禁止 `bg-white`, `text-white` 等硬编码，必须使用 CSS 变量
3. **主题兼容**: 支持明暗主题切换
4. **无占位符**: 所有代码必须完整可执行

---

## Completion Criteria / 完成标准

1. ✅ 创建预知列表页面组件
2. ✅ 正确调用 `getPreTransportOrders` API
3. ✅ 实现状态筛选功能
4. ✅ 显示所有必需字段
5. ✅ Production Prep 角色可访问
6. ✅ 前端构建通过: `cd frontend && npm run build`
7. ✅ UI 符合深色主题规范
