# 数据库架构文档

## 概述

本文档定义工装出入库管理系统的数据库表结构。基于项目实际存在的 SQL Server 数据库模块。

---

## 1. 表清单

### 1.1 已实现的表

| 表名（中文） | 逻辑别名 | 说明 | 状态 |
|--------------|----------|------|------|
| 工装出入库单_主表 | ToolIOOrder | 出入库单主表 | ✅ 已实现 |
| 工装出入库单_明细 | ToolIOOrderItem | 出入库单明细 | ✅ 已实现 |
| 工装出入库单_操作日志 | ToolIOLog | 操作日志 | ✅ 已实现 |
| 工装出入库单_通知记录 | ToolIONotify | 通知记录 | ✅ 已实现 |
| 工装位置表 | ToolLocation | 工装位置 | ✅ 已实现 |
| 工装身份卡_主表 | ToolMaster | 工装主数据（业务源表） | ✅ 已存在 |

---

## 2. 表结构详细设计

### 2.1 工装出入库单_主表 (ToolIOOrder)

**中文表名：** 工装出入库单_主表

**逻辑别名：** tool_io_order

**创建脚本位置：** database.py:307-343

#### 已实现字段

| 字段名（中文） | 字段名（英文别名） | 数据类型 | 必填 | 说明 |
|----------------|-------------------|----------|------|------|
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
| 保管员需求文本 | keeper_demand_text | TEXT | 否 | 保管员需求文本 |
| 运输通知文本 | transport_notify_text | TEXT | 否 | 运输通知文本 |
| 微信复制文本 | wechat_copy_text | TEXT | 否 | 微信复制文本 |
| 保管员确认时间 | keeper_confirm_time | DATETIME | 否 | 保管员确认时间 |
| 运输通知时间 | transport_notify_time | DATETIME | 否 | 运输通知时间 |
| 最终确认时间 | final_confirm_time | DATETIME | 否 | 最终确认时间 |
| 驳回原因 | reject_reason | VARCHAR(500) | 否 | 驳回原因 |
| 备注 | remark | VARCHAR(500) | 否 | 备注 |
| 创建时间 | created_at | DATETIME | 是 | 创建时间 |
| 修改时间 | updated_at | DATETIME | 是 | 修改时间 |
| 创建人 | created_by | VARCHAR(64) | 否 | 创建人 |
| 修改人 | updated_by | VARCHAR(64) | 否 | 修改人 |
| IS_DELETED | is_deleted | TINYINT | 是 | 软删除标记 |

#### ⚠️ 缺失字段（代码中引用但未在CREATE TABLE中定义）

| 字段名 | 数据类型 | 引用位置 | 建议 |
|--------|----------|----------|------|
| 工装数量 | INT | database.py:519 | 需要添加 |
| 已确认数量 | confirmed_count | INT | database.py:785 | 需要添加 |
| 最终确认人 | final_confirm_by | VARCHAR(64) | database.py:842 | 需要添加 |

---

### 2.2 工装出入库单_明细 (ToolIOOrderItem)

**中文表名：** 工装出入库单_明细

**逻辑别名：** tool_io_order_item

**创建脚本位置：** database.py:346-374

#### 已实现字段

| 字段名（中文） | 字段名（英文别名） | 数据类型 | 必填 | 说明 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 外键 |
| 工装ID | tool_id | BIGINT | 否 | 工装ID |
| 工装编码 | tool_code | VARCHAR(64) | 是 | 工装编码 |
| 工装名称 | tool_name | VARCHAR(128) | 是 | 工装名称 |
| 工装图号 | drawing_no | VARCHAR(64) | 否 | 工装图号 |
| 规格型号 | spec_model | VARCHAR(128) | 否 | 规格型号 |
| 申请数量 | apply_qty | DECIMAL(10,2) | 否 | 默认1 |
| 确认数量 | confirmed_qty | DECIMAL(10,2) | 否 | 确认数量 |
| 明细状态 | item_status | VARCHAR(32) | 是 | pending_check/approved/rejected/completed |
| 工装快照状态 | tool_snapshot_status | VARCHAR(32) | 否 | 工装快照状态 |
| 工装快照位置ID | tool_snapshot_location_id | BIGINT | 否 | 快照位置ID |
| 工装快照位置文本 | tool_snapshot_location_text | VARCHAR(255) | 否 | 快照位置文本 |
| 保管员确认位置ID | keeper_confirm_location_id | BIGINT | 否 | 确认位置ID |
| 保管员确认位置文本 | keeper_confirm_location_text | VARCHAR(255) | 否 | 确认位置文本 |
| 保管员检查结果 | keeper_check_result | VARCHAR(32) | 否 | 检查结果 |
| 保管员检查备注 | keeper_check_remark | VARCHAR(500) | 否 | 检查备注 |
| 归还检查结果 | return_check_result | VARCHAR(32) | 否 | 归还检查结果 |
| 归还检查备注 | return_check_remark | VARCHAR(500) | 否 | 归还检查备注 |
| 排序号 | sort_order | INT | 否 | 排序号 |
| 创建时间 | created_at | DATETIME | 是 | 创建时间 |
| 修改时间 | updated_at | DATETIME | 是 | 修改时间 |

#### ⚠️ 缺失字段（代码中引用但未在CREATE TABLE中定义）

| 字段名 | 数据类型 | 引用位置 | 建议 |
|--------|----------|----------|------|
| 确认时间 | confirm_time | DATETIME | database.py:755 | 需要添加 |
| 出入库完成时间 | complete_time | DATETIME | database.py:853 | 需要添加 |

---

### 2.3 工装出入库单_操作日志 (ToolIOLog)

**中文表名：** 工装出入库单_操作日志

**逻辑别名：** tool_io_log

**创建脚本位置：** database.py:377-394

#### 已实现字段

| 字段名（中文） | 字段名（英文别名） | 数据类型 | 必填 | 说明 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 外键 |
| 明细ID | item_id | BIGINT | 否 | 明细ID |
| 操作类型 | operation_type | VARCHAR(64) | 是 | 操作类型 |
| 操作人ID | operator_id | VARCHAR(64) | 是 | 操作人ID |
| 操作人姓名 | operator_name | VARCHAR(64) | 是 | 操作人姓名 |
| 操作人角色 | operator_role | VARCHAR(32) | 否 | 操作人角色 |
| 变更前状态 | from_status | VARCHAR(32) | 否 | 变更前状态 |
| 变更后状态 | to_status | VARCHAR(32) | 否 | 变更后状态 |
| 操作内容 | operation_content | TEXT | 否 | 操作内容 |
| 操作时间 | operation_time | DATETIME | 是 | 操作时间 |

---

### 2.4 工装出入库单_通知记录 (ToolIONotify)

**中文表名：** 工装出入库单_通知记录

**逻辑别名：** tool_io_notification

**创建脚本位置：** database.py:397-416

#### 已实现字段

| 字段名（中文） | 字段名（英文别名） | 数据类型 | 必填 | 说明 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 出入库单号 | order_no | VARCHAR(64) | 是 | 外键 |
| 通知类型 | notify_type | VARCHAR(32) | 是 | 通知类型 |
| 通知渠道 | notify_channel | VARCHAR(32) | 是 | feishu/wechat/email |
| 接收人 | receiver | VARCHAR(255) | 否 | 接收人 |
| 通知标题 | notify_title | VARCHAR(100) | 否 | 通知标题 |
| 通知内容 | notify_content | TEXT | 是 | 通知内容 |
| 复制文本 | copy_text | TEXT | 否 | 复制文本 |
| 发送状态 | send_status | VARCHAR(32) | 是 | pending/success/failed |
| 发送时间 | send_time | DATETIME | 否 | 发送时间 |
| 发送结果 | send_result | TEXT | 否 | 发送结果 |
| 重试次数 | retry_count | INT | 否 | 重试次数，默认0 |
| 创建时间 | created_at | DATETIME | 是 | 创建时间 |

---

### 2.5 工装位置表 (ToolLocation)

**中文表名：** 工装位置表

**逻辑别名：** tool_location

**创建脚本位置：** database.py:419-431

#### 已实现字段

| 字段名（中文） | 字段名（英文别名） | 数据类型 | 必填 | 说明 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 是 | 主键，自增 |
| 位置编码 | location_code | VARCHAR(64) | 是 | 位置编码，唯一 |
| 位置名称 | location_name | VARCHAR(128) | 是 | 位置名称 |
| 仓库区域 | warehouse_area | VARCHAR(64) | 否 | 仓库区域 |
| 货架号 | rack_no | VARCHAR(64) | 否 | 货架号 |
| 槽位号 | slot_no | VARCHAR(64) | 否 | 槽位号 |
| 完整路径 | full_path | VARCHAR(255) | 否 | 完整路径 |
| 备注 | remark | VARCHAR(500) | 否 | 备注 |

---

### 2.6 工装身份卡_主表 (ToolMaster)

**中文表名：** 工装身份卡_主表

**逻辑别名：** tool_master

**说明：** 这是已有的业务源表，用于工装搜索。

#### 主要字段（用于搜索）

| 字段名（中文） | 字段名（英文别名） | 说明 |
|----------------|-------------------|------|
| 序列号 | tool_code | 工装编码 |
| 工装图号 | drawing_no | 工装图号 |
| 工装名称 | tool_name | 工装名称 |
| 规格型号 | spec_model | 规格型号 |
| 当前版次 | version | 当前版次 |
| 定检属性 | category | 定检属性 |
| 定检有效截止 | expiry_date | 定检有效截止 |
| 应用历史 | location_info | 位置信息 |

---

## 3. 状态枚举

### 3.1 订单状态 (order_status)

定义位置：database.py:266-277

| 状态值 | 中文 | 说明 |
|--------|------|------|
| draft | 草稿 | 订单刚创建 |
| submitted | 已提交 | 已提交给保管员 |
| keeper_confirmed | 保管员已确认 | 保管员已确认 |
| partially_confirmed | 部分确认 | 部分明细已确认 |
| transport_notified | 已通知运输 | 已发送运输通知 |
| final_confirmation_pending | 待最终确认 | 等待最终确认 |
| completed | 已完成 | 订单完成 |
| rejected | 已拒绝 | 订单被拒绝 |
| cancelled | 已取消 | 订单已取消 |

### 3.2 明细状态 (item_status)

定义位置：database.py:280-283

| 状态值 | 中文 | 说明 |
|--------|------|------|
| pending_check | 待确认 | 等待确认 |
| approved | 已确认 | 已确认通过 |
| rejected | 已拒绝 | 已拒绝 |
| completed | 已完成 | 已完成 |

---

## 4. Schema 不一致报告

### 4.1 主表缺失字段

| 缺失字段 | 类型 | 引用代码 | 影响 |
|----------|------|----------|------|
| 工装数量 | INT | database.py:519 | 创建订单时更新工装数量会失败 |
| 已确认数量 | INT | database.py:785 | 保管员确认时无法记录确认数量 |
| 最终确认人 | VARCHAR(64) | database.py:842 | 最终确认时无法记录确认人 |

### 4.2 明细表缺失字段

| 缺失字段 | 类型 | 引用代码 | 影响 |
|----------|------|----------|------|
| 确认时间 | DATETIME | database.py:755 | 确认时间无法记录 |
| 出入库完成时间 | DATETIME | database.py:853 | 完成时间无法记录 |

---

## 5. 未来可选增强

| 增强项 | 说明 | 优先级 |
|--------|------|--------|
| 工装图片字段 | 增加工装图片存储 | 低 |
| 附件支持 | 支持上传附件 | 低 |
| 审批流程 | 多级审批支持 | 低 |
| 打印模板 | 打印单据模板 | 低 |

---

## 6. 相关文档

- [API规格文档](./API_SPEC.md)
- [继承数据库访问审查](./INHERITED_DB_ACCESS_REVIEW.md)
- [产品需求文档](./PRD.md)
- [架构文档](./ARCHITECTURE.md)
