# 飞书通知按钮防重复点击

---

## Header

```
Primary Executor: Claude Code
Task Type: Feature Development
Priority: P1
Stage: 00094
Goal: 飞书通知按钮点击后禁用并持久化状态，禁止重复点击刷屏
Dependencies: None
Execution: RUNPROMPT
```

---

## Context

### 业务背景

当前系统中的飞书通知按钮可以被用户多次点击，导致同一订单的通知被重复发送到飞书群，造成信息刷屏。

### 需求定义

所有发送飞书通知的按钮，应当仅可被点击一次，然后标记该步骤的通知已发送，持久化到数据库，禁止重复点击刷屏。

### 详细需求

1. **影响范围**：所有发送飞书通知的按钮
2. **持久性**：持久化到数据库，刷新页面后仍禁用
3. **异常处理**：显示错误状态和失败原因
4. **驳回机制**：后续步骤驳回时允许重新点击

---

## Phase 1: PRD - 业务需求分析

### 业务场景

用户（班组长/保管员/运输员）在订单工作流中点击"发送飞书"按钮后，系统需要防止该按钮被重复点击。

### 目标用户

- 班组长（出库最终确认）
- 保管员（确认/驳回）
- 运输员（运输通知）

### 核心痛点

当前按钮可被多次点击，导致飞书群收到重复通知。

### 业务目标

- 避免重复通知刷屏
- 通知发送状态可追溯
- 驳回后允许重新发送

---

## Phase 2: Data - 数据流转

### 数据来源

- 后端：`tool_io_notification` 表
- 前端：Vue 组件状态 + Pinia Store

### Schema 审视

需要检查 `tool_io_notification` 表结构，确认是否需要新增字段来记录每个步骤的发送状态。

### 字段设计

方案 A：在 `tool_io_notification` 表增加 `is_sent` 字段
方案 B：在 `tool_io_order` 表增加各步骤通知状态字段（如 `keeper_confirm_notified`, `final_confirm_notified`）

**选择方案 A**，因为：
- notification 表已有每条通知的记录
- 可以追溯每次通知的发送时间
- 符合现有架构

---

## Phase 3: Architecture - 架构设计

### 交互链路

```
用户点击按钮
  → 前端立即禁用按钮（防前端刷屏）
  → 调用后端 API
  → 后端记录 notification 状态
  → 返回结果
  → 前端根据结果更新 UI
    - 成功：显示"已发送✓"
    - 失败：恢复按钮 + 显示错误原因
```

### 驳回恢复机制

当订单状态被驳回时，后端需要在驳回接口中清除对应通知步骤的状态，或前端根据订单状态判断按钮是否可用。

### 风险识别

1. **并发风险**：用户快速连续点击 → 前端按钮立即禁用可解决
2. **数据一致性**：数据库状态与前端状态同步 → 后端返回最新状态
3. **错误处理**：飞书 API 超时 → 返回错误原因，前端显示

### 熔断策略

- 发送失败：Log & Skip + 返回错误原因
- 按钮禁用状态：以数据库状态为准

---

## Phase 4: Execution - 精确执行

### 步骤 1: 数据库变更

检查 `tool_io_notification` 表，确认是否需要新增字段。

### 步骤 2: 后端实现

1. 修改 `feishu_notification_adapter.py` 的发送逻辑
2. 在通知发送成功后更新数据库状态
3. 修改驳回接口，清除对应通知状态

### 步骤 3: 前端实现

1. 在所有飞书通知按钮上添加防重复点击逻辑
2. 按钮点击后立即禁用，显示 loading
3. 根据后端返回结果更新 UI
4. 页面加载时根据数据库状态设置按钮初始状态

### 步骤 4: 测试验证

1. 发送通知后刷新页面，确认按钮仍禁用
2. 模拟发送失败，确认错误原因显示
3. 模拟驳回操作，确认按钮恢复可点击

---

## Required References

- `backend/database/schema/column_names.py` - 字段名常量
- `backend/services/feishu_notification_adapter.py` - 通知适配器
- `backend/services/tool_io_service.py` - 核心服务
- `frontend/src/pages/tool-io/KeeperProcess.vue` - 保管员处理页面
- `frontend/src/pages/tool-io/OrderDetail.vue` - 订单详情页面
- `docs/DB_SCHEMA.md` - 数据库 Schema

---

## Constraints

1. 按钮状态必须持久化到数据库
2. 刷新页面后状态必须保持
3. 发送失败必须显示错误原因
4. 驳回后必须允许重新发送
5. 禁止修改 `Tooling_ID_Main` 表
6. 使用 `column_names.py` 中的常量访问中文字段

---

## Completion Criteria

- [ ] `tool_io_notification` 表或相关表有 `is_sent` 状态字段
- [ ] 所有飞书通知按钮点击后立即禁用
- [ ] 发送成功后按钮显示"已发送✓"并保持禁用
- [ ] 刷新页面后禁用状态保持
- [ ] 发送失败显示错误原因，按钮恢复可点击
- [ ] 订单驳回后对应按钮恢复可点击
- [ ] 数据库正确记录通知发送状态
- [ ] 无重复通知发送到飞书群
