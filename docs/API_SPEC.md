# API 规格文档

## 概述

本文档定义工装出入库管理系统的 REST API 接口。API 服务层应复用现有数据库模块中的函数。

**实现约束：**
- API 服务层应复用现有的 database.py 中的 CRUD 函数
- 新的 API 应包装或扩展现有数据库模块，而非完全替换
- 保持 SQL Server 兼容性

---

## 0. 认证 API

### 0.1 登录

**POST** `/api/auth/login`

**安全约束：**
- 登录接口启用速率限制：每个客户端 IP 每分钟最多 5 次请求
- 全局 API 默认速率限制：每个客户端 IP 每分钟最多 100 次请求

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| login_name | string | 是 | 本地账号登录名 |
| password | string | 是 | 明文密码 |

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| token | string | Bearer token |
| user | object | 当前用户信息 |
| user.user_id | string | 用户ID |
| user.display_name | string | 显示名称 |
| user.roles | array | 角色列表 |
| user.permissions | array | 权限列表 |

### 0.2 当前用户

**GET** `/api/auth/me`

**请求头：**

`Authorization: Bearer <token>`

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| user | object | 当前用户身份 |

---

## 0.5 组织 API

### 0.5.1 查询组织列表

**GET** `/api/orgs`

**实现说明：** 复用 `backend/services/org_service.py`

### 0.5.2 查询组织树

**GET** `/api/orgs/tree`

**实现说明：** 基于 `sys_org.parent_org_id` 构建树

### 0.5.3 查询组织详情

**GET** `/api/orgs/{org_id}`

### 0.5.4 创建组织

**POST** `/api/orgs`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| org_id | string | 是 | 组织ID |
| org_name | string | 是 | 组织名称 |
| org_code | string | 否 | 组织编码 |
| org_type | string | 是 | `company/factory/workshop/team/warehouse/project_group` |
| parent_org_id | string | 否 | 父组织ID |
| sort_no | int | 否 | 排序值 |
| status | string | 否 | `active/disabled` |
| remark | string | 否 | 备注 |

### 0.5.5 更新组织

**PUT** `/api/orgs/{org_id}`

**实现说明：** 支持基础字段更新与层级校验

---

## 1. 订单 API

### 1.1 创建订单

**POST** `/api/tool-io-orders`

**实现说明：** 复用 `database.create_tool_io_order()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_type | string | 是 | `outbound` 或 `inbound` |
| initiator_id | string | 是 | 发起人ID |
| initiator_name | string | 是 | 发起人姓名 |
| initiator_role | string | 是 | 发起人角色 |
| department | string | 否 | 部门 |
| project_code | string | 否 | 项目代号 |
| usage_purpose | string | 否 | 用途 |
| planned_use_time | string | 否 | 计划使用时间 |
| planned_return_time | string | 否 | 计划归还时间 |
| target_location_id | int | 否 | 目标位置ID |
| target_location_text | string | 否 | 目标位置文本 |
| remark | string | 否 | 备注 |
| items | array | 是 | 工装明细列表 |
| items[].tool_id | int | 否 | 工装ID |
| items[].serial_no | string | 是 | 工装序列号 |
| items[].tool_name | string | 是 | 工装名称 |
| items[].drawing_no | string | 否 | 工装图号 |
| items[].spec_model | string | 否 | 规格型号 |

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| order_no | string | 出入库单号 |

**状态转换：** 无 → `draft`

---

### 1.2 查询订单列表

**GET** `/api/tool-io-orders`

**实现说明：** 复用 `database.get_tool_io_orders()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_type | string | 否 | `outbound` 或 `inbound` |
| order_status | string | 否 | 订单状态 |
| initiator_id | string | 否 | 发起人ID |
| keeper_id | string | 否 | 保管员ID |
| keyword | string | 否 | 关键字搜索 |
| date_from | string | 否 | 开始日期 |
| date_to | string | 否 | 结束日期 |
| page_no | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| data | array | 订单列表 |
| total | int | 总数 |
| page_no | int | 当前页码 |
| page_size | int | 每页数量 |

---

### 1.3 查询订单详情

**GET** `/api/tool-io-orders/{order_no}`

**实现说明：** 复用 `database.get_tool_io_order()`

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| order_no | string | 出入库单号 |
| order_type | string | 单据类型 |
| order_status | string | 单据状态 |
| initiator_id | string | 发起人ID |
| initiator_name | string | 发起人姓名 |
| keeper_id | string | 保管员ID |
| keeper_name | string | 保管员姓名 |
| transport_type | string | 运输类型 |
| items | array | 工装明细 |
| ... | | 其他主表字段 |

---

### 1.4 提交订单

**POST** `/api/tool-io-orders/{order_no}/submit`

**实现说明：** 复用 `database.submit_tool_io_order()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| operator_id | string | 是 | 操作人ID |
| operator_name | string | 是 | 操作人姓名 |
| operator_role | string | 是 | 操作人角色 |

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| order_no | string | 出入库单号 |

**状态转换：** `draft` → `submitted`

---

### 1.5 保管员确认

**POST** `/api/tool-io-orders/{order_no}/keeper-confirm`

**实现说明：** 复用 `database.keeper_confirm_order()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keeper_id | string | 是 | 保管员ID |
| keeper_name | string | 是 | 保管员姓名 |
| transport_type | string | 否 | 运输类型 |
| transport_assignee_id | string | 否 | 运输人ID |
| transport_assignee_name | string | 否 | 运输人姓名 |
| items | array | 是 | 明细确认列表 |
| items[].serial_no | string | 是 | 工装序列号 |
| items[].location_id | int | 否 | 确认位置ID |
| items[].location_text | string | 否 | 确认位置文本 |
| items[].check_result | string | 是 | 检查结果 |
| items[].check_remark | string | 否 | 检查备注 |
| items[].approved_qty | float | 否 | 确认数量 |
| items[].status | string | 是 | approved/rejected |
| operator_id | string | 是 | 操作人ID |
| operator_name | string | 是 | 操作人姓名 |
| operator_role | string | 是 | 操作人角色 |

**状态转换：** `submitted` → `keeper_confirmed` 或 `partially_confirmed`

---

### 1.6 发送运输通知

**POST** `/api/tool-io-orders/{order_no}/notify-transport`

**实现说明：** 需实现，调用 `database.add_tool_io_notification()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| notify_type | string | 是 | 通知类型 |
| notify_channel | string | 是 | 通知渠道 |
| receiver | string | 是 | 接收人 |
| title | string | 否 | 通知标题 |
| content | string | 是 | 通知内容 |
| copy_text | string | 否 | 复制文本 |

**状态转换：** successful delivery: `keeper_confirmed`/`partially_confirmed` → `transport_notified`

---

### 1.7 最终确认

**POST** `/api/tool-io-orders/{order_no}/final-confirm`

**实现说明：** 复用 `database.final_confirm_order()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| operator_id | string | 是 | 操作人ID |
| operator_name | string | 是 | 操作人姓名 |
| operator_role | string | 是 | 操作人角色 |

**状态转换：** `keeper_confirmed`/`partially_confirmed`/`transport_notified`/`final_confirmation_pending` → `completed`

**业务规则：**
- 出库单：由班组长（发起人）确认
- 入库单：由保管员确认

---

### 1.8 拒绝订单

**POST** `/api/tool-io-orders/{order_no}/reject`

**实现说明：** 复用 `database.reject_tool_io_order()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| reject_reason | string | 是 | 拒绝原因 |
| operator_id | string | 是 | 操作人ID |
| operator_name | string | 是 | 操作人姓名 |
| operator_role | string | 是 | 操作人角色 |

**状态转换：** `submitted`/`keeper_confirmed`/`partially_confirmed` → `rejected`

---

### 1.9 取消订单

**POST** `/api/tool-io-orders/{order_no}/cancel`

**实现说明：** 复用 `database.cancel_tool_io_order()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| operator_id | string | 是 | 操作人ID |
| operator_name | string | 是 | 操作人姓名 |
| operator_role | string | 是 | 操作人角色 |

**状态转换：** 非终态 → `cancelled`

---

### 1.10 获取待保管员确认订单

**GET** `/api/tool-io-orders/pending-keeper`

**实现说明：** 复用 `database.get_pending_keeper_orders()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keeper_id | string | 否 | 保管员ID |

---

### 1.10.1 获取准备工预知运输列表

**GET** `/api/tool-io-orders/pre-transport`

**权限**: `order:transport_execute`

**实现说明：**
- 查询状态为 `submitted` / `keeper_confirmed` / `transport_notified` 的订单
- 按 RBAC 组织范围进行数据隔离（Production Prep 默认仅本组织）

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| orders | array | 预知运输订单列表 |
| orders[].order_no | string | 出入库单号 |
| orders[].order_type | string | 单据类型 |
| orders[].destination | string | 目标位置文本 |
| orders[].status | string | 状态值 |
| orders[].status_text | string | 状态显示文本 |
| orders[].expected_tools | int | 预计工装数量 |
| orders[].submit_time | string/null | 提交时间（ISO8601） |
| orders[].submitter_name | string | 提交人姓名 |
| orders[].estimated_transport_time | string/null | 预计运输时间（ISO8601） |
| orders[].keeper_confirmed_time | string/null | 保管员确认时间（ISO8601） |

---

### 1.11 运输异常上报与处理

#### 1.11.1 上报运输异常

**POST** `/api/tool-io-orders/{order_no}/report-transport-issue`

**权限**: `order:transport_execute`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| issue_type | string | 是 | `tool_damaged` / `quantity_mismatch` / `location_error` / `other` |
| description | string | 否 | 异常描述，最大 500 字符 |
| image_urls | array | 否 | 异常图片 URL 列表 |

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| issue_id | int | 异常记录 ID |
| message | string | 固定为 `异常已上报` |

#### 1.11.2 查询运输异常列表

**GET** `/api/tool-io-orders/{order_no}/transport-issues`

**权限**: `order:keeper_confirm`

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| issues | array | 异常记录列表 |
| issues[].id | int | 异常 ID |
| issues[].issue_type | string | 异常类型 |
| issues[].description | string | 异常描述 |
| issues[].image_urls | array | 图片 URL 列表 |
| issues[].reporter_name | string | 上报人姓名 |
| issues[].report_time | string/null | 上报时间（ISO8601） |
| issues[].status | string | `pending` / `resolved` |
| issues[].handler_name | string/null | 处理人姓名 |
| issues[].handle_time | string/null | 处理时间（ISO8601） |
| issues[].handle_reply | string/null | 处理回复 |

#### 1.11.3 处理运输异常

**POST** `/api/tool-io-orders/{order_no}/resolve-transport-issue`

**权限**: `order:keeper_confirm`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| issue_id | int | 是 | 异常记录 ID |
| handle_reply | string | 是 | 处理回复，最大 500 字符 |

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| message | string | 固定为 `异常已处理` |

---

### 1.12 批量更新工装状态

**PATCH** `/api/tools/batch-status`

**实现说明：** 调用 `tool_io_service.batch_update_tool_status()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tool_codes | array | 是 | 工装序列号列表 |
| new_status | string | 是 | 新状态 |
| remark | string | 否 | 备注 |
| operator | object | 是 | 操作人信息 {user_id, display_name} |

---

### 1.13 获取工装状态变更历史

**GET** `/api/tools/status-history/{serial_no}`

**实现说明：** 调用 `tool_io_service.get_tool_status_history()`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page_no | integer | 否 | 页码 (默认1) |
| page_size | integer | 否 | 每页条数 (默认20) |

---

### 1.14 获取操作日志

**GET** `/api/tool-io-orders/{order_no}/logs`

**实现说明：** 复用 `database.get_tool_io_logs()`

---

## 2. 工装 API

### 2.1 搜索工装

**GET** `/api/tools/search`

**实现说明：** 复用 `database.search_tools()`，基于工装身份卡_主表

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | string | 否 | 关键字 |
| status | string | 否 | 状态 |
| location_id | int | 否 | 位置ID |
| page_no | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应参数：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 是否成功 |
| data | array | 工装列表 |
| data[].serial_no | string/null | 工装序列号 |
| data[].tool_name | string | 工装名称 |
| data[].spec_model | string | 机型 |
| data[].current_location_text | string | 当前库位 |
| data[].status_text | string | 状态显示文本（正常/返修中/封存中/定检超期/定检中/无合格证） |
| data[].disabled | boolean | 是否禁用（异常工装为 `true`） |
| data[].disabled_reason | string/null | 禁用原因（可用工装为 `null`） |
| total | int | 总数 |
| page_no | int | 当前页 |
| page_size | int | 每页数量 |

**disabled_reason 枚举值：**

- `null`
- `工装处于返修状态，不可使用`
- `工装处于封存状态，不可使用`
- `定检超期，工装不具备使用条件`
- `工装正在定检中，不可使用`
- `工装无合格证，不具备验收条件`

**响应示例：**

```json
{
  "success": true,
  "data": [
    {
      "serial_no": "T001",
      "tool_name": "扳手",
      "spec_model": "规格A",
      "current_location_text": "仓库A-1",
      "status_text": "在库",
      "disabled": false,
      "disabled_reason": null
    },
    {
      "serial_no": "T003",
      "tool_name": "钻头",
      "spec_model": "规格C",
      "current_location_text": "仓库B-2",
      "status_text": "定检超期",
      "disabled": true,
      "disabled_reason": "定检超期，工装不具备使用条件"
    }
  ],
  "total": 2,
  "page_no": 1,
  "page_size": 20
}
```

---

### 2.2 批量查询工装

**POST** `/api/tools/batch-query`

**实现说明：** 需实现

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tool_codes | array | 是 | 工装序列号列表 |

---

## 2.3 MPL API (2026-04-01)

### 2.3.1 查询 MPL 分组列表

**GET** `/api/mpl`

**权限**: `tool:view`

**查询参数**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page_no | int | 否 | 页码，默认 `1` |
| page_size | int | 否 | 每页数量，默认 `20` |
| drawing_no | string | 否 | 工装图号模糊筛选 |
| keyword | string | 否 | 图号 / 版次 / 组件号 / 组件名 模糊筛选 |

### 2.3.2 创建 MPL 分组

**POST** `/api/mpl`

**权限**: `tool:view`

**请求体**

```json
{
  "tool_drawing_no": "DJ-1001",
  "tool_revision": "A",
  "items": [
    {
      "component_no": "CB-01",
      "component_name": "卡板",
      "quantity": 2,
      "photo_data": "data:image/png;base64,..."
    }
  ]
}
```

**说明**

- 一个 MPL 分组对应一套 `tool_drawing_no + tool_revision`
- `photo_data` 使用 Base64 Data URL，前端限制 2MB

### 2.3.3 获取 MPL 详情

**GET** `/api/mpl/{mpl_no}`

**权限**: `tool:view`

### 2.3.4 更新 MPL 分组

**PUT** `/api/mpl/{mpl_no}`

**权限**: `tool:view`

**说明**: 使用请求体中的 `items` 全量替换该分组组件列表

### 2.3.5 删除 MPL 分组

**DELETE** `/api/mpl/{mpl_no}`

**权限**: `tool:view`

### 2.3.6 按工装图号和版次查询 MPL

**GET** `/api/mpl/by-tool?drawing_no=xxx&revision=xxx`

**权限**: `tool:view`

---

## 3.4 系统配置 API (2026-04-01)

### 3.4.1 查询系统配置

**GET** `/api/admin/system-config`

**权限**: `admin:user_manage`

### 3.4.2 查询单个配置

**GET** `/api/admin/system-config/{config_key}`

**权限**: `admin:user_manage`

### 3.4.3 更新系统配置

**PUT** `/api/admin/system-config/{config_key}`

**权限**: `admin:user_manage`

**初始配置项**

- `mpl_enabled`: 是否启用保管员确认前的 MPL 检查
- `mpl_strict_mode`: 缺少 MPL 时是否阻止确认

---

## 3. 文本生成 API

### 3.1 生成保管员需求文本

**GET** `/api/tool-io-orders/{order_no}/generate-keeper-text`

**实现说明：** 需实现

---

### 3.2 生成运输通知文本

**GET** `/api/tool-io-orders/{order_no}/generate-transport-text`

**实现说明：** 需实现

---

### 3.3 扩展 API（已实现）

以下 API 端点在实现过程中新增，非原始需求文档定义：

#### 3.3.1 分配运输人

**POST** `/api/tool-io-orders/{order_no}/assign-transport`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| transport_type | string | 否 | 运输类型 |
| transport_assignee_id | string | 否 | 运输人ID |
| transport_assignee_name | string | 否 | 运输人姓名 |
| operator_id | string | 是 | 操作人ID |
| operator_name | string | 是 | 操作人姓名 |
| operator_role | string | 是 | 操作人角色 |

---

#### 3.3.2 开始运输

**POST** `/api/tool-io-orders/{order_no}/transport-start`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| operator_id | string | 否 | 操作人ID |
| operator_name | string | 否 | 操作人姓名 |
| operator_role | string | 否 | 操作人角色 |

**状态转换：** `transport_notified` → `transporting`

---

#### 3.3.3 完成运输

**POST** `/api/tool-io-orders/{order_no}/transport-complete`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| operator_id | string | 否 | 操作人ID |
| operator_name | string | 否 | 操作人姓名 |
| operator_role | string | 否 | 操作人角色 |

**状态转换：** `transporting` → `final_confirmation_pending`

---

#### 3.3.4 删除订单

**DELETE** `/api/tool-io-orders/{order_no}`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| operator_id | string | 是 | 操作人ID |
| operator_name | string | 是 | 操作人姓名 |
| operator_role | string | 是 | 操作人角色 |

**说明：** 仅允许删除草稿状态的订单

---

#### 3.3.5 获取通知记录

**GET** `/api/tool-io-orders/{order_no}/notification-records`

**说明：** 获取订单的所有通知发送记录

---

#### 3.3.6 发送保管员通知

**POST** `/api/tool-io-orders/{order_no}/notify-keeper`

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| notify_type | string | 否 | 通知类型 |
| notify_channel | string | 否 | 通知渠道 |
| receiver | string | 否 | 接收人 |
| title | string | 否 | 通知标题 |
| content | string | 否 | 通知内容 |
| operator_id | string | 否 | 操作人ID |
| operator_name | string | 否 | 操作人姓名 |

---

#### 3.3.7 获取最终确认可用性

**GET** `/api/tool-io-orders/{order_no}/final-confirm-availability`

**说明：** 检查当前用户是否有权限进行最终确认，返回订单类型和角色信息

---

## 4. 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {}
}
```

### 失败响应

```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATUS",
    "message": "当前订单状态不允许此操作"
  }
}
```

---

## 5. 错误码定义

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| INVALID_PARAMS | 400 | 参数错误 |
| NOT_FOUND | 404 | 资源不存在 |
| FORBIDDEN | 403 | 无权限操作 |
| INVALID_STATUS | 400 | 状态转换非法 |
| SYSTEM_ERROR | 500 | 系统错误 |

---

## 6. 相关文档

- [数据库架构文档](./DB_SCHEMA.md)
- [继承数据库访问审查](./INHERITED_DB_ACCESS_REVIEW.md)
- [产品需求文档](./PRD.md)
- [架构文档](./ARCHITECTURE.md)

---

## 7. Password Change API (2026-03-19)

### 7.1 Change Current User Password

**POST** `/api/user/change-password`

**Auth:** `Authorization: Bearer <token>`

**Request Body**

```json
{
  "old_password": "current_password",
  "new_password": "NewPassword123"
}
```

**Validation Rules**

- `old_password` is required
- `new_password` is required
- `new_password` must be at least 8 characters
- `new_password` must include uppercase, lowercase, and numeric characters
- `new_password` must be different from `old_password`

**Responses**

- `200`:

```json
{
  "success": true
}
```

- `400` (example, old password mismatch):

```json
{
  "success": false,
  "error": "old_password is incorrect"
}
```

---

## 8. Feedback API (2026-03-19)

All feedback endpoints require authentication (`Authorization: Bearer <token>`).

### 8.1 List Feedback

**GET** `/api/feedback`

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| login_name | string | No | Optional login name filter; normal users are restricted to their own feedback |
| status | string | No | `pending` / `reviewed` / `resolved` |
| limit | integer | No | Max rows to return, default `200`, max `500` |

**Response (`200`)**

```json
{
  "success": true,
  "data": [
    {
      "id": 12,
      "category": "bug",
      "subject": "无法提交工装单",
      "content": "点击提交后按钮一直 loading",
      "login_name": "zhangsan",
      "user_name": "张三",
      "status": "pending",
      "created_at": "2026-03-19T10:15:00",
      "updated_at": "2026-03-19T10:15:00"
    }
  ]
}
```

### 8.2 Create Feedback

**POST** `/api/feedback`

**Request Body**

```json
{
  "category": "feature",
  "subject": "增加筛选条件",
  "content": "建议在订单列表增加部门维度筛选",
  "status": "pending"
}
```

**Validation**

- `category` must be one of `bug/feature/ux/other`
- `subject` length: `2..100`
- `content` length: `10..2000`

**Response (`201`)**

```json
{
  "success": true,
  "data": {
    "id": 13,
    "category": "feature",
    "subject": "增加筛选条件",
    "content": "建议在订单列表增加部门维度筛选",
    "login_name": "zhangsan",
    "user_name": "张三",
    "status": "pending",
    "created_at": "2026-03-19T10:20:00",
    "updated_at": "2026-03-19T10:20:00"
  }
}
```

### 8.3 Delete Feedback

**DELETE** `/api/feedback/{id}`

Normal users can only delete their own feedback. Users with `admin:user_manage` can delete any feedback.

**Response (`200`)**

```json
{
  "success": true
}
```

### 8.4 Admin List All Feedback

**GET** `/api/feedback/all`

**Permission:** `admin:user_manage`

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| status | string | No | `pending` / `reviewed` / `resolved` |
| category | string | No | `bug` / `feature` / `ux` / `other` |
| keyword | string | No | Fuzzy match on subject/content/login_name/user_name |
| limit | integer | No | Default `50`, max `500` |
| offset | integer | No | Default `0` |

**Response (`200`)**

```json
{
  "success": true,
  "data": [],
  "total": 100
}
```

### 8.5 Admin Update Feedback Status

**PUT** `/api/feedback/{id}/status`

**Permission:** `admin:user_manage`

**Request Body**

```json
{
  "new_status": "reviewed"
}
```

**Allowed transitions**

- `pending` -> `reviewed`
- `pending` -> `resolved`
- `reviewed` -> `resolved`
- `resolved` -> `reviewed` (reopen)

### 8.6 Admin Add Feedback Reply

**POST** `/api/feedback/{id}/reply`

**Permission:** `admin:user_manage`

**Request Body**

```json
{
  "content": "已定位问题，计划在下个版本修复。"
}
```

**Validation**

- `content` length: `1..1000`

When the current feedback status is `pending`, adding a reply auto-updates it to `reviewed`.

### 8.7 Admin Get Feedback Replies

**GET** `/api/feedback/{id}/replies`

**Permission:** `admin:user_manage`

**Response (`200`)**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "feedback_id": 13,
      "reply_content": "已收到，处理中",
      "replier_login_name": "admin",
      "replier_user_name": "系统管理员",
      "created_at": "2026-03-23T12:00:00"
    }
  ]
}
```

---

## 9. Tool Batch Status API (2026-03-19)

### 9.1 Batch Update Tool Status

**PATCH** `/api/tools/batch-status`

**Permission:** `tool:status_update`

**Request Body**

```json
{
  "tool_codes": ["T001", "T002"],
  "new_status": "maintain",
  "remark": "scheduled maintenance"
}
```

**Validation**

- `tool_codes` must be a non-empty array
- `new_status` must be one of `in_storage` / `outbounded` / `maintain` / `scrapped`

**Response (`200`)**

```json
{
  "success": true,
  "updated_count": 2,
  "records": [
    {
      "tool_code": "T001",
      "old_status": "in_storage",
      "new_status": "maintain"
    },
    {
      "tool_code": "T002",
      "old_status": "outbounded",
      "new_status": "maintain"
    }
  ],
  "missing_tool_codes": []
}
```

### 9.2 Query Tool Status Change History

**GET** `/api/tools/status-history/{serial_no}`

**Permission:** `tool:view`

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| page_no | integer | No | Page number, default `1` |
| page_size | integer | No | Page size, default `20` |

**Response (`200`)**

```json
{
  "success": true,
  "data": [
    {
      "old_status": "in_storage",
      "new_status": "maintain",
      "remark": "scheduled maintenance",
      "operator_id": "U10001",
      "operator_name": "keeper_a",
      "change_time": "2026-03-19T13:20:00",
      "client_ip": "10.10.1.8"
    }
  ],
  "total": 1,
  "page_no": 1,
  "page_size": 20
}
```
