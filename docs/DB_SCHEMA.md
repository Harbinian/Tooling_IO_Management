# 工装出入库管理系统 - 数据库架构文档

## 概述

本文档定义工装出入库管理系统的数据库表结构。基于项目实际存在的 SQL Server 数据库模式。

**注意：** 本文档中引用的 line numbers (如 `database.py:307-343`) 已过时，请参考实际的 `backend/database/schema/schema_manager.py` 中的 CREATE TABLE 语句获取最新位置。

---

## 1. 表清单

### 1.1 已实现的表

| 表名（中文） | 逻辑表名 | 说明 | 状态 |
|--------------|----------|------|------|
| 工装出入库单_主表 | ToolIOOrder | 出入库单主表 | ✅ 已实现 |
| 工装出入库单_明细 | ToolIOOrderItem | 出入库单明细 | ✅ 已实现 |
| 工装出入库单_操作日志 | ToolIOLog | 操作日志 | ✅ 已实现 |
| 工装出入库单_通知记录 | ToolIONotify | 通知记录 | ✅ 已实现 |
| 工装出入库单_位置 | ToolLocation | 工装位置 | ✅ 已实现 |
| 工装身份卡_主表 | ToolMaster | 工装主数据（外部系统表） | ✅ 已存在 |
| tool_io_feedback | ToolIOFeedback | 用户反馈表 | ✅ 已实现 |
| tool_io_feedback_reply | ToolIOFeedbackReply | 反馈回复记录 | ✅ 已实现 |
| tool_status_change_history | ToolStatusHistory | 工装状态变更记录 | ✅ 已实现 |
| tool_io_transport_issue | TransportIssue | 运输异常记录 | ✅ 已实现 |
| tool_io_mpl | ToolIOMpl | 工装可拆卸件清单 | ✅ 已实现 |
| sys_system_config | SysSystemConfig | 系统功能开关配置 | ✅ 已实现 |
| sys_org | SysOrg | 组织表 | ✅ 已实现 |
| sys_user | SysUser | 系统用户表 | ✅ 已实现 |
| sys_role | SysRole | 角色表 | ✅ 已实现 |
| sys_permission | SysPermission | 权限表 | ✅ 已实现 |
| sys_user_role_rel | SysUserRoleRel | 用户角色关系 | ✅ 已实现 |
| sys_role_permission_rel | SysRolePermissionRel | 角色权限关系 | ✅ 已实现 |
| sys_role_data_scope_rel | SysRoleDataScopeRel | 角色数据范围关系 | ✅ 已实现 |
| sys_user_password_change_log | SysUserPasswordChangeLog | 密码修改审计日志 | ✅ 已实现 |
| sys_user_org_rel | SysUserOrgRel | 用户组织关系 | ✅ 已实现 |

---

## 2. 表结构详细设计

### 2.1 工装出入库单_主表 (tool_io_order)

**中文表名：** 工装出入库单_主表

**逻辑表名：** tool_io_order

**创建脚本位置：** `backend/database/schema/schema_manager.py:239-276`

#### 已实现字段

| 字段名（中文） | 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 单号，唯一 |
| 单据类型 | order_type | VARCHAR(16) | 是 | outbound/inbound |
| 单据状态 | order_status | VARCHAR(32) | 是 | 状态 |
| 发起人ID | initiator_id | VARCHAR(64) | 是 | 申请人ID |
| 发起人姓名 | initiator_name | VARCHAR(64) | 是 | 申请人姓名 |
| 发起人角色 | initiator_role | VARCHAR(32) | 是 | 角色 |
| 部门 | department | VARCHAR(64) | 否 | 部门 |
| 项目代号 | project_code | VARCHAR(64) | 否 | 项目代号 |
| 用途 | usage_purpose | VARCHAR(255) | 否 | 用途 |
| 计划使用时间 | planned_use_time | DATETIME | 否 | 计划使用时间 |
| 计划归还时间 | planned_return_time | DATETIME | 否 | 计划归还时间 |
| 目标位置ID | target_location_id | BIGINT | 否 | 目标位置ID |
| 目标位置文本 | target_location_text | VARCHAR(255) | 否 | 目标位置文本 |
| 保管员ID | keeper_id | VARCHAR(64) | 否 | 保管员ID |
| 保管员姓名 | keeper_name | VARCHAR(64) | 否 | 保管员姓名 |
| 运输类型 | transport_type | VARCHAR(32) | 否 | 运输类型 |
| 运输人ID | transport_operator_id | VARCHAR(64) | 否 | 运输人ID |
| 运输人姓名 | transport_operator_name | VARCHAR(64) | 否 | 运输人姓名 |
| 保管员确认时间 | keeper_confirm_time | DATETIME | 否 | 保管员确认时间 |
| 运输通知时间 | transport_notify_time | DATETIME | 否 | 运输通知时间 |
| 最终确认时间 | final_confirm_time | DATETIME | 否 | 最终确认时间 |
| 工装数量 | tool_quantity | INT | 否 | 工装数量 |
| 已确认数量 | confirmed_count | INT | 否 | 已确认数量 |
| 最终确认人 | final_confirm_by | VARCHAR(64) | 否 | 最终确认人 |
| 拒绝原因 | reject_reason | VARCHAR(500) | 否 | 拒绝原因 |
| 取消原因 | cancel_reason | VARCHAR(500) | 否 | 取消原因 |
| 备注 | remark | VARCHAR(500) | 否 | 备注 |
| 组织ID | org_id | VARCHAR(64) | 否 | 所属组织 |
| 创建时间 | created_at | DATETIME | 是 | 创建时间 |
| 修改时间 | updated_at | DATETIME | 是 | 修改时间 |
| 创建人 | created_by | VARCHAR(64) | 否 | 创建人 |
| 修改人 | updated_by | VARCHAR(64) | 否 | 修改人 |
| IS_DELETED | is_deleted | TINYINT | 是 | 逻辑删除标记 |

#### 已补充的缺失字段（通过 schema alignment）

| 字段 | 类型 | 状态 |
|------|------|------|
| org_id | VARCHAR(64) | ✅ 已补充 |
| tool_quantity | INT | ✅ 已补充 |
| confirmed_count | INT | ✅ 已补充 |
| final_confirm_by | VARCHAR(64) | ✅ 已补充 |

---

### 2.2 工装出入库单_明细 (tool_io_order_item)

**中文表名：** 工装出入库单_明细

**逻辑表名：** tool_io_order_item

**创建脚本位置：** `backend/database/schema/schema_manager.py:277-303`

#### 已实现字段

| 字段名（中文） | 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 外键 |
| 工装ID | tool_id | BIGINT | 否 | 工装ID |
| 工装序列号 | serial_no | VARCHAR(64) | 是 | 工装序列号 |
| 工装名称 | tool_name | VARCHAR(255) | 否 | 工装名称 |
| 工装图号 | drawing_no | VARCHAR(255) | 否 | 工装图号 |
| 规格型号 | spec_model | VARCHAR(255) | 否 | 规格型号 |
| 申请数量 | apply_qty | DECIMAL(18,2) | 否 | 默认1 |
| 确认数量 | confirmed_qty | DECIMAL(18,2) | 否 | 确认数量 |
| 明细状态 | item_status | VARCHAR(32) | 是 | pending_check/approved/rejected/completed |
| 工装快照状态 | tool_snapshot_status | VARCHAR(255) | 否 | 工装快照状态 |
| 工装快照位置ID | tool_snapshot_location_id | BIGINT | 否 | 快照位置ID |
| 工装快照位置文本 | tool_snapshot_location_text | VARCHAR(255) | 否 | 快照位置文本 |
| 确认人 | confirm_by | VARCHAR(255) | 否 | 确认人 |
| 确认人ID | confirm_by_id | BIGINT | 否 | 确认人ID |
| 确认人姓名 | confirm_by_name | VARCHAR(64) | 否 | 确认人姓名 |
| 确认时间 | confirm_time | DATETIME | 否 | 确认时间 |
| 拒绝原因 | reject_reason | VARCHAR(500) | 否 | 拒绝原因 |
| 出入库完成时间 | io_complete_time | DATETIME | 否 | 出入库完成时间 |
| 排序号 | sort_order | INT | 否 | 排序号，默认1 |
| 创建时间 | created_at | DATETIME | 是 | 创建时间 |
| 修改时间 | updated_at | DATETIME | 是 | 修改时间 |

#### 已补充的缺失字段（通过 schema alignment）

| 字段 | 类型 | 状态 |
|------|------|------|
| confirm_time | DATETIME | ✅ 已补充 |
| io_complete_time | DATETIME | ✅ 已补充 |

---

### 2.3 工装出入库单_操作日志 (tool_io_operation_log)

**中文表名：** 工装出入库单_操作日志

**逻辑表名：** tool_io_operation_log

**创建脚本位置：** `backend/database/schema/schema_manager.py:304-318`

#### 已实现字段

| 字段名（中文） | 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 外键 |
| 明细ID | item_id | BIGINT | 否 | 明细ID |
| 操作类型 | operation_type | VARCHAR(64) | 是 | 操作类型 |
| 操作人ID | operator_id | VARCHAR(64) | 是 | 操作人ID |
| 操作人姓名 | operator_name | VARCHAR(64) | 是 | 操作人姓名 |
| 操作人角色 | operator_role | VARCHAR(64) | 否 | 操作人角色 |
| 变更前状态 | from_status | VARCHAR(64) | 否 | 变更前状态 |
| 变更后状态 | to_status | VARCHAR(64) | 否 | 变更后状态 |
| 操作内容 | operation_content | TEXT | 否 | 操作内容 |
| 操作时间 | operation_time | DATETIME | 是 | 操作时间 |

---

### 2.4 工装出入库单_通知记录 (tool_io_notification)

**中文表名：** 工装出入库单_通知记录

**逻辑表名：** tool_io_notification

**创建脚本位置：** `backend/database/schema/schema_manager.py:320-337`

#### 已实现字段

| 字段名（中文） | 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 外键 |
| 通知类型 | notify_type | VARCHAR(64) | 是 | 通知类型 |
| 通知渠道 | notify_channel | VARCHAR(64) | 否 | feishu/wechat/email |
| 接收人 | receiver | VARCHAR(255) | 否 | 接收人 |
| 通知标题 | notify_title | VARCHAR(255) | 否 | 通知标题 |
| 通知内容 | notify_content | TEXT | 否 | 通知内容 |
| 复制文本 | copy_text | TEXT | 否 | 复制文本 |
| 发送状态 | send_status | VARCHAR(32) | 是 | pending/success/failed |
| 发送时间 | send_time | DATETIME | 否 | 发送时间 |
| 发送结果 | send_result | TEXT | 否 | 发送结果 |
| 重试次数 | retry_count | INT | 否 | 重试次数，默认0 |
| 创建时间 | created_at | DATETIME | 是 | 创建时间 |

---

### 2.5 工装出入库单_位置 (tool_io_location)

**中文表名：** 工装出入库单_位置

**逻辑表名：** tool_io_location

**创建脚本位置：** `backend/database/schema/schema_manager.py:338-350`

**注意：** 此表原用名`工装位置表`，现统一使用 `工装出入库单_位置`。

#### 已实现字段

| 字段名（中文） | 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 位置编码 | location_code | VARCHAR(64) | 是 | 位置编码 |
| 位置名称 | location_name | VARCHAR(255) | 是 | 位置名称 |
| 位置描述 | location_desc | VARCHAR(255) | 否 | 位置描述 |
| 库区 | warehouse_area | VARCHAR(64) | 否 | 库区 |
| 货架位 | storage_slot | VARCHAR(64) | 否 | 货架位 |
| 货架 | shelf | VARCHAR(255) | 否 | 货架 |
| 备注 | remark | VARCHAR(500) | 否 | 备注 |

---

### 2.6 工装身份卡_主表 (Tooling_ID_Main)

**中文表名：** 工装身份卡_主表

**逻辑表名：** Tooling_ID_Main

**说明：** 这是已有的业务源表，用于工装搜索。表结构由外部系统管理，本系统只读。

#### 主要字段（用于搜索）

| 字段名（中文） | 字段名（英文） | 说明 |
|----------------|----------------|------|
| 序列号 | tool_code | 外部系统表中的工装序列号 |
| 工装图号 | drawing_no | 工装图号 |
| 工装名称 | tool_name | 工装名称 |
| 规格型号 | spec_model | 规格型号 |
| 当前版次 | current_version | 当前版次 |
| 定检属性 | inspection_category | 定检属性 |
| 定检周期 | inspection_cycle | 定检周期 |
| 定检有效截止 | inspection_expiry_date | 定检有效截止 |
| 库位 | storage_location | 库位信息 |
| 出入库状态 | io_status | 出入库状态 |

---

## 3. 状态定义

### 3.1 订单状态 (order_status)

定义位置：`backend/services/tool_io_service.py`

| 状态值 | 中文 | 说明 |
|--------|------|------|
| draft | 草稿 | 订单刚创建 |
| submitted | 已提交 | 已提交给保管员 |
| partially_confirmed | 部分确认 | 部分明细已确认 |
| keeper_confirmed | 保管员已确认 | 保管员已确认 |
| transport_notified | 已通知运输 | 已发送运输通知 |
| transporting | 运输中 | 运输进行中 |
| final_confirmation_pending | 待最终确认 | 等待最终确认 |
| completed | 已完成 | 订单已完成 |
| rejected | 已拒绝 | 订单被拒绝 |
| cancelled | 已取消 | 订单已取消 |

### 3.2 明细状态 (item_status)

| 状态值 | 中文 | 说明 |
|--------|------|------|
| pending_check | 待确认 | 等待确认 |
| approved | 已确认 | 已确认通过 |
| rejected | 已拒绝 | 已拒绝 |
| completed | 已完成 | 已完成 |

### 3.3 工装状态 (tool_status)

| 状态值 | 中文 | 说明 |
|--------|------|------|
| in_storage | 在库 | 工装在仓库中 |
| outbounded | 已出库 | 工装已被借出 |
| maintain | 维修中 | 工装需要维修 |
| scrapped | 已报废 | 工装已报废 |

---

## 4. Schema 一致性报告

### 4.1 已修复的主表缺失字段 (2026-03-19)

以下字段已在 `backend/database/schema/schema_manager.py` 的 CREATE TABLE 中补充：

| 字段 | 类型 | 状态 |
|------|------|------|
| org_id | VARCHAR(64) | ✅ 已补充 |
| tool_quantity | INT | ✅ 已补充 |
| confirmed_count | INT | ✅ 已补充 |
| final_confirm_by | VARCHAR(64) | ✅ 已补充 |

### 4.2 已修复的明细表缺失字段 (2026-03-19)

| 字段 | 类型 | 状态 |
|------|------|------|
| confirm_time | DATETIME | ✅ 已补充 |
| io_complete_time | DATETIME | ✅ 已补充 |

---

## 5. 运输异常记录表 (tool_io_transport_issue)

**中文表名：** 工装运输异常记录

**逻辑表名：** tool_io_transport_issue

**创建脚本位置：** `backend/database/schema/schema_manager.py:187-228`

#### 字段定义

| 字段名（中文） | 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 外键 |
| 异常类型 | issue_type | VARCHAR(50) | 是 | tool_damaged/quantity_mismatch/location_error/other |
| 描述 | description | NVARCHAR(500) | 否 | 异常描述，最大500字符 |
| 图片URLs | image_urls | NVARCHAR(2000) | 否 | 异常图片URL列表 |
| 上报人ID | reporter_id | VARCHAR(64) | 否 | 上报人ID |
| 上报人姓名 | reporter_name | NVARCHAR(50) | 否 | 上报人姓名 |
| 上报时间 | report_time | DATETIME | 是 | 上报时间 |
| 状态 | status | VARCHAR(20) | 是 | pending/resolved |
| 处理人ID | handler_id | VARCHAR(64) | 否 | 处理人ID |
| 处理人姓名 | handler_name | NVARCHAR(50) | 否 | 处理人姓名 |
| 处理时间 | handle_time | DATETIME | 否 | 处理时间 |
| 处理回复 | handle_reply | NVARCHAR(500) | 否 | 处理回复，最大500字符 |
| 创建时间 | created_at | DATETIME | 是 | 创建时间 |

#### 索引

- `IX_tool_io_transport_issue_order_no` on `(order_no)`
- `IX_tool_io_transport_issue_status` on `(status)`
- `IX_tool_io_transport_issue_report_time` on `(report_time)`

---

## 6. 工装状态变更历史表 (tool_status_change_history)

**中文表名：** 工装状态变更记录

**逻辑表名：** tool_status_change_history

**创建脚本位置：** `backend/database/schema/schema_manager.py:151-184`

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| id | BIGINT | 是 | 主键，自增 |
| serial_no | NVARCHAR(100) | 是 | 工装序列号 |
| old_status | NVARCHAR(50) | 是 | 之前状态 |
| new_status | NVARCHAR(50) | 是 | 更新后状态 |
| remark | NVARCHAR(500) | 否 | 操作备注 |
| operator_id | NVARCHAR(64) | 是 | 操作人ID |
| operator_name | NVARCHAR(100) | 是 | 操作人显示名 |
| change_time | DATETIME2 | 是 | 变更时间戳 |
| client_ip | NVARCHAR(64) | 否 | 来源IP |

#### 索引

- `IX_tool_status_change_history_serial_no_time` on `(serial_no, change_time)`

---

## 7. 反馈表 (tool_io_feedback)

**中文表名：** 工装反馈表

**逻辑表名：** tool_io_feedback

**说明：** 存储用户从设置页面提交的反馈，持久化到 SQL Server 而非浏览器本地存储。

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| id | BIGINT | 是 | 主键，自增 |
| category | VARCHAR(32) | 是 | bug/feature/ux/other |
| subject | NVARCHAR(200) | 是 | 反馈标题 |
| content | NVARCHAR(2000) | 是 | 反馈内容 |
| login_name | VARCHAR(100) | 是 | 提交人登录名 |
| user_name | NVARCHAR(100) | 是 | 提交人显示名 |
| status | VARCHAR(32) | 是 | pending/reviewed/resolved |
| created_at | DATETIME2 | 是 | 创建时间戳 |
| updated_at | DATETIME2 | 是 | 最后更新时间戳 |

#### 索引

- `IX_tool_io_feedback_login_name` on `(login_name)`
- `IX_tool_io_feedback_created_at` on `(created_at)`

---

## 8. 反馈回复表 (tool_io_feedback_reply)

**中文表名：** 工装反馈回复表

**逻辑表名：** tool_io_feedback_reply

**说明：** 存储管理员对反馈的处理回复记录。

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| id | BIGINT | 是 | 主键，自增 |
| feedback_id | BIGINT | 是 | 关联反馈ID |
| reply_content | NVARCHAR(1000) | 是 | 回复内容 |
| replier_login_name | VARCHAR(100) | 是 | 回复人登录名 |
| replier_user_name | NVARCHAR(100) | 是 | 回复人显示名 |
| created_at | DATETIME2 | 是 | 回复时间戳 |

#### 外键

- `FK_feedback_reply` on `feedback_id` -> `tool_io_feedback(id)` with `ON DELETE CASCADE`

#### 索引

- `IX_tool_io_feedback_reply_feedback_id` on `(feedback_id)`

---

## 9. 密码修改审计表 (sys_user_password_change_log)

**中文表名：** 密码修改审计表

**逻辑表名：** sys_user_password_change_log

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| id | BIGINT | 是 | 主键，自增 |
| user_id | NVARCHAR(64) | 是 | 修改密码的用户ID |
| changed_by | NVARCHAR(64) | 是 | 操作人ID（当前实现中为本人） |
| change_result | NVARCHAR(20) | 是 | success 或 failed |
| remark | NVARCHAR(500) | 否 | 失败或操作备注 |
| client_ip | NVARCHAR(64) | 否 | 客户端IP |
| changed_at | DATETIME2 | 是 | 操作时间戳 |

#### 索引

- `IX_sys_user_password_change_user_time` on `(user_id, changed_at DESC)`

---

## 10. MPL 清单表 (tool_io_mpl)

**中文表名：** 工装可拆卸件清单

**逻辑表名：** tool_io_mpl

**说明：** 每个 `mpl_no` 表示一个工装图号 + 版次的清单分组；表内一行对应一个可拆卸组件。

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| id | BIGINT | 是 | 主键，自增 |
| mpl_no | VARCHAR(128) | 是 | 分组编号，格式 `MPL-{tool_drawing_no}-{tool_revision}` |
| tool_drawing_no | VARCHAR(64) | 是 | 工装图号 |
| tool_revision | VARCHAR(32) | 是 | 工装版次 |
| component_no | VARCHAR(64) | 是 | 组件号 |
| component_name | NVARCHAR(256) | 是 | 组件名称 |
| quantity | INT | 是 | 数量，默认 1 |
| photo_data | NVARCHAR(MAX) | 否 | Base64 图片 |
| created_by | VARCHAR(64) | 否 | 维护人 |
| created_at | DATETIME2 | 是 | 创建时间 |
| updated_at | DATETIME2 | 是 | 更新时间 |

#### 索引

- `IX_tool_io_mpl_tool` on `(tool_drawing_no, tool_revision)`
- `IX_tool_io_mpl_mpl_no` on `(mpl_no)`
- `UX_tool_io_mpl_tool_component` UNIQUE on `(tool_drawing_no, tool_revision, component_no)`

---

## 11. 系统配置表 (sys_system_config)

**中文表名：** 系统配置表

**逻辑表名：** sys_system_config

**说明：** 保存管理员可在线修改的系统功能开关。

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| config_key | VARCHAR(128) | 是 | 配置键，主键 |
| config_value | NVARCHAR(256) | 否 | 配置值 |
| description | NVARCHAR(512) | 否 | 描述 |
| updated_by | VARCHAR(64) | 否 | 更新人 |
| updated_at | DATETIME2 | 是 | 更新时间 |

#### 初始数据

- `mpl_enabled = false`
- `mpl_strict_mode = false`

---

## 12. 组织架构表 (sys_org)

**中文表名：** 组织表

**逻辑表名：** sys_org

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| id | BIGINT | 是 | 主键，自增 |
| org_id | NVARCHAR(64) | 是 | 组织标识符，唯一 |
| org_name | NVARCHAR(100) | 是 | 组织显示名称 |
| org_code | NVARCHAR(100) | 否 | 组织编码 |
| org_type | NVARCHAR(50) | 是 | 类型: company/factory/workshop/team/warehouse/project_group |
| parent_org_id | NVARCHAR(64) | 否 | 父组织ID |
| sort_no | INT | 否 | 排序值 |
| status | NVARCHAR(20) | 是 | active 或 disabled |
| remark | NVARCHAR(500) | 否 | 备注 |
| created_at | DATETIME2 | 是 | 创建时间戳 |
| created_by | NVARCHAR(64) | 否 | 创建人 |
| updated_at | DATETIME2 | 否 | 最后更新时间戳 |
| updated_by | NVARCHAR(64) | 否 | 最后更新人 |

#### 索引

- `UX_sys_org_org_id` UNIQUE on `(org_id)`
- `IX_sys_org_parent_org_id` on `(parent_org_id)`

---

## 13. 用户组织关系表 (sys_user_org_rel)

**中文表名：** 用户组织关系表

**逻辑表名：** sys_user_org_rel

#### 字段定义

| 字段名（英文） | 数据类型 | 必填 | 说明 |
|----------------|----------|------|------|
| id | BIGINT | 是 | 主键，自增 |
| user_id | NVARCHAR(64) | 是 | 用户标识符 |
| org_id | NVARCHAR(64) | 是 | 组织标识符 |
| is_primary | BIT | 是 | 是否为主组织 (1=yes) |
| status | NVARCHAR(20) | 是 | active 或 disabled |
| created_at | DATETIME2 | 是 | 创建时间戳 |
| created_by | NVARCHAR(64) | 否 | 创建人 |
| updated_at | DATETIME2 | 否 | 最后更新时间戳 |
| updated_by | NVARCHAR(64) | 否 | 最后更新人 |

---

## 14. 未来可选扩展

| 改进项 | 说明 | 优先级 |
|--------|------|--------|
| 工装图片字段 | 增加工装图片存储 | 低 |
| 附件支持 | 支持上传附件 | 低 |
| 多级审批流程 | 多级审批支持 | 低 |
| 打印模板 | 打印单据模板 | 低 |

---

## 15. 相关文档

- [API规格文档](./API_SPEC.md)
- [继承数据库访问审查](./INHERITED_DB_ACCESS_REVIEW.md)
- [产品需求文档](./PRD.md)
- [架构文档](./ARCHITECTURE.md)

---

## 16. 附录：新增组织归属字段

新增组织归属字段:

- `org_id`: 订单所属组织，用于 RBAC `ORG` / `ORG_AND_CHILDREN` 数据范围过滤

历史数据迁移规则:

- 当历史订单缺少 `org_id` 时，优先填入发起人的主组织 `org_id`
- 如果发起人主组织为空，则回退到发起人的 `default_org_id`
