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
| items[].tool_code | string | 是 | 工装编码 |
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
| items[].tool_code | string | 是 | 工装编码 |
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

### 1.11 获取操作日志

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

---

### 2.2 批量查询工装

**POST** `/api/tools/batch-query`

**实现说明：** 需实现

**请求参数：**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tool_codes | array | 是 | 工装编码列表 |

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
