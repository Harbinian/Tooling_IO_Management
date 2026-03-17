# 前端设计文档 (FRONTEND_DESIGN.md)

## 1. 页面概览

本系统包含四个核心页面，主要面向班组长（Team Leader）和保管员（Keeper）两个角色。系统采用 Vue3 + Element Plus 构建，确保在 PC 端和移动端均有良好的操作体验。

| 页面名称 | 访问路径 | 主要用户 | 核心功能 |
|----------|----------|----------|----------|
| 单据列表页 | `/inventory` | 全部 | 订单搜索、筛选、状态查看、快捷操作 |
| 新建单据页 | `/inventory/create` | 班组长 | 搜索工装、批量选择、填写申请信息、生成预览文本 |
| 保管员工作台 | `/inventory/keeper` | 保管员 | 待处理单据汇总、逐项确认、发送通知 |
| 单据详情页 | `/inventory/:order_no` | 全部 | 完整单据信息、操作日志、通知记录、最终确认动作 |

---

## 2. 页面详细设计

### 2.1 新建单据页 (Order Creation Page)

**设计目标**：提供高效的工装搜索与批量选择体验。

- **工装搜索区域**：
  - 支持关键字搜索（编码、名称、图号、规格、位置）。
  - 结果以表格形式展示，支持分页或无限滚动。
  - **批量选择 UX**：点击行即可选中，支持全选/反选。
- **已选工装列表**：
  - 悬浮或侧边栏显示已选数量。
  - 支持从已选列表中移除。
- **基本信息表单**：
  - 单据类型切换（出库/入库），根据类型动态显示/隐藏字段（如：入库时“目标位置”变为“回库位置”）。
  - 日期时间选择器（计划使用/归还时间）。
- **结构化文本预览**：
  - 提交前可点击“预览申请文本”，在弹窗中显示。
- **动作按钮**：
  - `保存草稿`：保存为 `draft` 状态。
  - `提交申请`：保存并流转至 `submitted` 状态。

### 2.2 保管员工作台 (Keeper Processing Page)

**设计目标**：快速处理待办任务，简化确认与通知流程。

- **待办汇总**：
  - 顶部显示待处理订单总数。
  - 订单卡片展示：单号、类型、发起人、工装数量、提交时间。
- **确认弹窗/抽屉**：
  - 点击订单进入确认界面。
  - **逐项确认表格**：
    - 展示快照位置，提供输入框修改“确认位置”。
    - 状态选择：通过（Approved）/ 拒绝（Rejected）。
  - **运输配置**：
    - 选择运输类型（叉车/吊车/人工）。
    - 填写运输人姓名。
- **通知与发送**：
  - 实时生成“运输通知文本”和“微信复制文本”。
  - 提供 `发送飞书通知` 和 `一键复制微信文本` 按钮。
- **动作按钮**：
  - `确认通过`：单据转为 `keeper_confirmed` 或 `partially_confirmed`。
  - `驳回单据`：填写理由，单据转为 `rejected`。

### 2.3 单据列表页 (Order List Page)

**设计目标**：清晰展示业务状态，支持快速检索。

- **筛选器**：
  - 类型筛选（出库/入库）。
  - 状态筛选（多选）。
  - 发起人/保管员搜索。
  - 日期范围选择。
- **数据表格**：
  - 状态标签（Tag）：不同状态对应不同颜色（见 4. 状态显示规则）。
  - 快速预览：点击单号跳转详情。
- **动作列**：
  - 根据当前状态显示 `查看`、`撤回`（草稿态）等。

### 2.4 单据详情页 (Order Detail Page)

**设计目标**：提供完整的审计踪迹和闭环操作。

- **核心信息区**：
  - 显著的状态徽章。
  - 关键时间节点（创建时间、确认时间、通知时间、完成时间）。
- **工装明细表**：
  - 展示申请信息与保管员确认信息的对比。
- **审计与日志**：
  - 时间轴形式展示 `操作日志`。
  - 展示 `通知记录`（发送时间、接收人、状态）。
- **文本展示区**：
  - 折叠面板显示各类结构化文本，支持一键复制。
- **动作区域**：
  - **最终确认按钮**：
    - 出库单：发起人可见。
    - 入库单：保管员可见。

---

## 3. 组件结构建议

| 组件名 | 路径 | 说明 |
|----------|------|------|
| `ToolSearchDialog` | `components/tool-io/ToolSearchDialog.vue` | 工装搜索与多选弹窗 |
| `SelectedToolList` | `components/tool-io/SelectedToolList.vue` | 已选工装预览与编辑 |
| `OrderStatusTag` | `components/tool-io/OrderStatusTag.vue` | 统一的状态标签组件 |
| `LogTimeline` | `components/tool-io/LogTimeline.vue` | 操作日志时间轴组件 |
| `TextPreviewCard` | `components/tool-io/TextPreviewCard.vue` | 带复制功能的文本预览卡片 |

---

## 4. 状态显示规则 (Order Status)

| 状态值 | UI 标签文本 | Element Plus 类型 | 说明 |
|----------|------------|-------------------|------|
| `draft` | 草稿 | info | 初始状态，仅发起人可见 |
| `submitted` | 待确认 | warning | 已提交，等待保管员处理 |
| `keeper_confirmed` | 已确认 | success | 保管员已全部确认通过 |
| `partially_confirmed` | 部分通过 | warning | 保管员拒绝了部分明细 |
| `transport_notified` | 已通知运输 | primary | 已发送通知，等待线下搬运 |
| `final_confirmation_pending` | 待收货/入库 | warning | 搬运完成，等待最终确认 |
| `completed` | 已完成 | success | 流程结束，终态 |
| `rejected` | 已驳回 | danger | 保管员拒绝申请 |
| `cancelled` | 已取消 | info | 发起人取消订单 |

---

## 5. 按钮显示规则 (Button Visibility)

| 页面 | 按钮 | 可见条件 (Role + Status) |
|----------|------|-------------------------|
| 新建/编辑页 | `提交申请` | Role=TL && Status=draft |
| 新建/编辑页 | `保存草稿` | Role=TL && Status=draft |
| 工作台 | `开始确认` | Role=Keeper && Status=submitted |
| 工作台 | `发送通知` | Role=Keeper && Status in [keeper_confirmed, partially_confirmed] |
| 详情页 | `确认收货` | Role=TL && OrderType=outbound && Status in [transport_notified, final_confirmation_pending] |
| 详情页 | `确认入库` | Role=Keeper && OrderType=inbound && Status in [transport_notified, final_confirmation_pending] |
| 详情页 | `驳回` | Role=Keeper && Status=submitted |
| 详情页 | `取消订单` | Role=TL && Status in [draft, rejected] |

---

## 6. 字段映射表 (Field Mapping)

### 6.1 订单主表

| UI 字段名 | API 字段名 | 类型 | 说明 |
|-----------|------------|------|------|
| 出入库单号 | `order_no` | string | 唯一标识 |
| 单据类型 | `order_type` | string | outbound/inbound |
| 单据状态 | `order_status` | string | 见状态枚举 |
| 发起人 | `initiator_name` | string | |
| 项目代号 | `project_code` | string | |
| 计划使用时间 | `planned_use_time`| datetime | |
| 目标位置 | `target_location_text`| string | |
| 运输人 | `transport_operator_name`| string | |

### 6.2 订单明细

| UI 字段名 | API 字段名 | 类型 | 说明 |
|-----------|------------|------|------|
| 工装编码 | `tool_code` | string | |
| 工装名称 | `tool_name` | string | |
| 申请数量 | `apply_qty` | number | |
| 确认位置 | `keeper_confirm_location_text`| string | 保管员填写的实际位置 |
| 明细状态 | `item_status` | string | |

---

## 7. 结构化文本 UX 处理

- **预览弹窗**：使用 `ElDialog` 配合 `pre` 标签保持格式。
- **一键复制**：使用 `navigator.clipboard` API，并配合 `ElMessage` 提示成功。
- **区分样式**：保管员需求文本、运输通知文本、微信复制文本应使用不同的卡片背景色或图标区分，避免用户混淆。

---

## 8. 前端实现注意事项

- **移动端适配**：
  - 列表页在手机端自动转为卡片流展示。
  - 搜索对话框应占据 100% 宽度。
- **异常处理**：
  - 所有 API 调用需有 `try-cache` 捕获，并通过 `ElNotification` 报错。
  - 表单提交前必须进行前端校验（必填项检查）。
- **性能优化**：
  - 工装选择列表使用虚拟列表（Virtual List）处理大量数据。
  - 搜索框添加 `debounce`（防抖）减少 API 请求频率。
