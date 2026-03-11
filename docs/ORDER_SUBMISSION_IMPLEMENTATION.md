# 订单提交实现 / Order Submission Implementation

---

## Schema 检查摘要 / Schema Inspection Summary

此工作流使用以下现有 SQL Server 表: / The workflow uses these existing SQL Server tables:

- `工装出入库单_主表` / Tool IO Order Main Table
- `工装出入库单_明细` / Tool IO Order Detail Table
- `工装出入库单_操作日志` / Tool IO Order Operation Log Table
- `tool_io_order_no_sequence` / 工装出入库单号序列

`工装出入库单_主表` 中已审计的相关主表字段: / Relevant audited header fields in `工装出入库单_主表`:

- `出入库单号` / Order Number
- `单据类型` / Order Type
- `单据状态` / Order Status
- `发起人ID` / Initiator ID
- `发起人姓名` / Initiator Name
- `发起人角色` / Initiator Role
- `部门` / Department
- `项目代号` / Project Code
- `用途` / Usage Purpose
- `计划使用时间` / Planned Use Time
- `计划归还时间` / Planned Return Time
- `目标位置ID` / Target Location ID
- `目标位置文本` / Target Location Text
- `工装数量` / Tool Quantity
- `已确认数量` / Confirmed Quantity
- `备注` / Remark
- `创建时间` / Create Time
- `修改时间` / Modify Time
- `创建人` / Creator
- `修改人` / Modifier
- `IS_DELETED` / 是否删除

`工装出入库单_明细` 中已审计的相关明细字段: / Relevant audited item fields in `工装出入库单_明细`:

- `出入库单号` / Order Number
- `工装ID` / Tool ID
- `工装编码` / Tool Code
- `工装名称` / Tool Name
- `工装图号` / Tool Drawing Number
- `规格型号` / Specification Model
- `申请数量` / Apply Quantity
- `确认数量` / Confirm Quantity
- `明细状态` / Item Status
- `工装快照状态` / Tool Snapshot Status
- `工装快照位置文本` / Tool Snapshot Location Text
- `排序号` / Sort Number

`工装出入库单_操作日志` 中已审计的相关日志字段: / Relevant audited log fields in `工装出入库单_操作日志`:

- `出入库单号` / Order Number
- `操作类型` / Operation Type
- `操作人ID` / Operator ID
- `操作人姓名` / Operator Name
- `操作人角色` / Operator Role
- `变更前状态` / Previous Status
- `变更后状态` / Changed Status
- `操作内容` / Operation Content
- `操作时间` / Operation Time

---

## 逻辑实体映射 / Logical Entity Mapping

### 订单主表 / Order Header

存储在 `工装出入库单_主表`。 / Stored in `工装出入库单_主表`.

逻辑映射: / Logical mapping:

- `order_no` -> `出入库单号`
- `order_type` -> `单据类型`
- 初始状态 -> `单据状态 = 'draft'` / initial status -> `单据状态 = 'draft'`
- 提交状态 -> `单据状态 = 'submitted'` / submit status -> `单据状态 = 'submitted'`
- 发起人字段 -> `发起人ID` / `发起人姓名` / `发起人角色` / initiator fields -> `发起人ID` / `发起人姓名` / `发起人角色`
- 业务表单字段 -> `项目代号` / `用途` / `目标位置文本` / `备注` / business form fields -> `项目代号` / `用途` / `目标位置文本` / `备注`

### 订单明细 / Order Item

存储在 `工装出入库单_明细`。 / Stored in `工装出入库单_明细`.

逻辑映射: / Logical mapping:

- `tool_code` -> `工装编码`
- `tool_name` -> `工装名称`
- `drawing_no` -> `工装图号`
- `spec_model` -> `规格型号`
- `apply_qty` -> `申请数量`
- 初始明细状态 -> `明细状态 = 'pending_check'` / initial item status -> `明细状态 = 'pending_check'`

`工装ID` 物理上存在为 `BIGINT`，但实际工装业务键是 `序列号`。 / `工装ID` exists physically as `BIGINT`, but the actual tool business key is `序列号`.

因此，实现将 `工装编码=序列号` 作为主要引用，/ The implementation therefore writes `工装编码=序列号` as the primary reference,

仅在传入值可以安全转换为 `BIGINT` 时才写入 `工装ID`。 / and only writes `工装ID` when the incoming value can safely convert to `BIGINT`.

### 审计日志 / Audit Log

存储在 `工装出入库单_操作日志`。 / Stored in `工装出入库单_操作日志`.

用于: / Used for:

- 创建操作 / create action
- 提交操作 / submit action

---

## 使用的 API 端点 / API Endpoints Used

### 创建订单 / Create Order

- `POST /api/tool-io-orders`

响应: / Response:

```json
{
  "success": true,
  "order_no": "TO-OUT-20260311-002"
}
```

### 提交订单 / Submit Order

- `POST /api/tool-io-orders/{order_no}/submit`

响应: / Response:

```json
{
  "success": true,
  "order_no": "TO-OUT-20260311-002",
  "status": "submitted"
}
```

---

## 请求 Payload 结构 / Request Payload Structure

```json
{
  "order_type": "outbound",
  "initiator_id": "u_test",
  "initiator_name": "Test User",
  "initiator_role": "team_leader",
  "department": "TEST",
  "project_code": "P-001",
  "usage_purpose": "workflow test",
  "planned_use_time": "2026-03-11 10:00:00",
  "planned_return_time": "2026-03-12 10:00:00",
  "target_location_text": "A06",
  "remark": "prompt 013 test",
  "items": [
    {
      "tool_id": "04M02777",
      "tool_code": "04M02777",
      "tool_name": "MA700登机梯试验件手工铣切工装",
      "drawing_no": "Y21-RDFY21-5211-3010-001-S9400",
      "spec_model": "MA700",
      "apply_qty": 1
    }
  ]
}
```

---

## 后端行为 / Backend Behavior

- 验证 `order_type` / validates `order_type`
- 验证至少选择一个工装 / validates at least one selected tool
- 验证所有 `tool_code` 值存在于 `工装身份卡_主表` 中 / validates all `tool_code` values exist in `工装身份卡_主表`
- 防止一个订单内重复的 `tool_code` 值 / prevents duplicate `tool_code` values inside one order
- 插入主表行 / inserts header row
- 插入明细表行 / inserts item rows
- 初始化主表状态为 `draft` / initializes header status to `draft`
- 初始化明细表状态为 `pending_check` / initializes item status to `pending_check`
- 提交时更新主表状态为 `submitted` / updates header status to `submitted` on submit
- 写入创建和提交审计日志 / writes create and submit audit logs

---

## 前端集成 / Frontend Integration

`frontend/src/pages/tool-io/OrderCreate.vue` 现在: / `frontend/src/pages/tool-io/OrderCreate.vue` now:

- 在 payload 中包含已选工具 / includes selected tools in the payload
- 提交前验证已选工具和目标位置 / validates selected tools and target location before submit
- 支持保存草稿和提交操作 / supports save-draft and submit actions
- 成功后显示返回的订单号 / shows the returned order number on success
- 使用 `ElMessage` 处理 API 错误 / handles API errors with `ElMessage`

---

## 验证 / Verification

使用实时后端测试调用验证: / Verified with live backend test calls:

- 创建订单成功 / create order succeeded
- 提交订单成功 / submit order succeeded
- 返回订单号: `TO-OUT-20260311-002` / returned order number: `TO-OUT-20260311-002`
- 持久化的主表行状态: `submitted` / persisted header row status: `submitted`
- 持久化的明细表行状态: `pending_check` / persisted item row status: `pending_check`
