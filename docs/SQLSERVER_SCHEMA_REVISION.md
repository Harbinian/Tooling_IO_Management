# SQL Server Schema 修订文档

## 概述

本文档基于项目现有的 database.py 代码，分析并修订工装出入库管理系统的数据库 schema 设计。

### 设计原则

- 保持现有的中文表名和列名命名风格
- 保持 SQL Server + pyodbc 兼容性
- 不重新设计整个持久层
- 聚焦于修正和稳定当前实现

---

## 1. 现有 Schema 问题

### 1.1 主表缺失字段

| 缺失字段 | 类型 | 代码引用位置 | 影响 |
|----------|------|--------------|------|
| 工装数量 | INT | database.py:519 | 创建订单时更新工装数量会失败 |
| 已确认数量 | INT | database.py:785 | 保管员确认时无法记录确认数量 |
| 最终确认人 | VARCHAR(64) | database.py:842 | 最终确认时无法记录确认人 |

### 1.2 明细表缺失字段

| 缺失字段 | 类型 | 代码引用位置 | 影响 |
|----------|------|--------------|------|
| 确认时间 | DATETIME | database.py:755 | 确认时间无法记录 |
| 出入库完成时间 | DATETIME | database.py:853 | 完成时间无法记录 |

### 1.3 其他问题

- 缺少取消原因字段
- 审计字段不完整
- 缺少部分状态跟踪字段

---

## 2. 修订表设计：工装出入库单_主表

### 2.1 A. 现有字段（已实现）

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | BIGINT | 主键，自增 |
| 出入库单号 | VARCHAR(64) | 单号，唯一 |
| 单据类型 | VARCHAR(16) | outbound/inbound |
| 单据状态 | VARCHAR(32) | 订单状态 |
| 发起人ID | VARCHAR(64) | 申请人ID |
| 发起人姓名 | VARCHAR(64) | 申请人姓名 |
| 发起人角色 | VARCHAR(32) | 角色 |
| 部门 | VARCHAR(64) | 部门 |
| 项目代号 | VARCHAR(64) | 项目代号 |
| 用途 | VARCHAR(255) | 用途 |
| 计划使用时间 | DATETIME | 计划使用时间 |
| 计划归还时间 | DATETIME | 计划归还时间 |
| 目标位置ID | BIGINT | 目标位置ID |
| 目标位置文本 | VARCHAR(255) | 目标位置文本 |
| 保管员ID | VARCHAR(64) | 保管员ID |
| 保管员姓名 | VARCHAR(64) | 保管员姓名 |
| 运输类型 | VARCHAR(32) | 运输类型 |
| 运输人ID | VARCHAR(64) | 运输人ID |
| 运输人姓名 | VARCHAR(64) | 运输人姓名 |
| 保管员需求文本 | TEXT | 保管员需求文本 |
| 运输通知文本 | TEXT | 运输通知文本 |
| 微信复制文本 | TEXT | 微信复制文本 |
| 保管员确认时间 | DATETIME | 保管员确认时间 |
| 运输通知时间 | DATETIME | 运输通知时间 |
| 最终确认时间 | DATETIME | 最终确认时间 |
| 驳回原因 | VARCHAR(500) | 驳回原因 |
| 备注 | VARCHAR(500) | 备注 |
| 创建时间 | DATETIME | 创建时间 |
| 修改时间 | DATETIME | 修改时间 |
| 创建人 | VARCHAR(64) | 创建人 |
| 修改人 | VARCHAR(64) | 修改人 |
| IS_DELETED | TINYINT | 软删除标记 |

### 2.2 B. 缺失但必需的字段（代码引用）

| 字段名 | 数据类型 | 代码引用 | 建议 |
|--------|----------|----------|------|
| 工装数量 | INT | database.py:519 | 必须添加 |
| 已确认数量 | INT | database.py:785 | 必须添加 |
| 最终确认人 | VARCHAR(64) | database.py:842 | 必须添加 |
| 取消原因 | VARCHAR(500) | - | 建议添加 |

### 2.3 C. 推荐的生产字段

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| version | INT | 乐观锁版本号 |
| 来源单号 | VARCHAR(64) | 原始申请单号（退库时） |
| 紧急程度 | VARCHAR(16) | 普通/加急 |

### 2.4 D. 可选未来增强字段

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 附件数量 | INT | 附件数量 |
| 打印次数 | INT | 打印次数 |
| 关闭时间 | DATETIME | 订单关闭时间 |

### 2.5 索引设计

| 索引类型 | 字段 | 说明 |
|----------|------|------|
| PK | id | 聚集索引主键 |
| UK | 出入库单号 | 唯一索引 |
| IDX | 单据类型 | 查询过滤 |
| IDX | 单据状态 | 状态查询 |
| IDX | 发起人ID | 用户查询 |
| IDX | 保管员ID | 保管员查询 |
| IDX | 创建时间 | 时间排序 |

---

## 3. 修订表设计：工装出入库单_明细

### 3.1 A. 现有字段（已实现）

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | BIGINT | 主键，自增 |
| 出入库单号 | VARCHAR(64) | 外键 |
| 工装ID | BIGINT | 工装ID |
| 工装编码 | VARCHAR(64) | 工装编码 |
| 工装名称 | VARCHAR(128) | 工装名称 |
| 工装图号 | VARCHAR(64) | 工装图号 |
| 规格型号 | VARCHAR(128) | 规格型号 |
| 申请数量 | DECIMAL(10,2) | 申请数量 |
| 确认数量 | DECIMAL(10,2) | 确认数量 |
| 明细状态 | VARCHAR(32) | 明细状态 |
| 工装快照状态 | VARCHAR(32) | 工装快照状态 |
| 工装快照位置ID | BIGINT | 快照位置ID |
| 工装快照位置文本 | VARCHAR(255) | 快照位置文本 |
| 保管员确认位置ID | BIGINT | 确认位置ID |
| 保管员确认位置文本 | VARCHAR(255) | 确认位置文本 |
| 保管员检查结果 | VARCHAR(32) | 检查结果 |
| 保管员检查备注 | VARCHAR(500) | 检查备注 |
| 归还检查结果 | VARCHAR(32) | 归还检查结果 |
| 归还检查备注 | VARCHAR(500) | 归还检查备注 |
| 排序号 | INT | 排序号 |
| 创建时间 | DATETIME | 创建时间 |
| 修改时间 | DATETIME | 修改时间 |

### 3.2 B. 缺失但必需的字段（代码引用）

| 字段名 | 数据类型 | 代码引用 | 建议 |
|--------|----------|----------|------|
| 确认时间 | DATETIME | database.py:755 | 必须添加 |
| 出入库完成时间 | DATETIME | database.py:853 | 必须添加 |

### 3.3 C. 推荐的生产字段

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 批号 | VARCHAR(32) | 批次号 |
| 出库库位 | VARCHAR(64) | 出库库位 |
| 入库库位 | VARCHAR(64) | 入库库位 |

### 3.4 D. 可选未来增强字段

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 图片URL | VARCHAR(500) | 工装图片 |
| 质量状态 | VARCHAR(32) | 质量状态 |

### 3.5 索引设计

| 索引类型 | 字段 | 说明 |
|----------|------|------|
| PK | id | 聚集索引主键 |
| IDX | 出入库单号 | 订单关联 |
| IDX | 工装编码 | 工装查询 |
| IDX | 明细状态 | 状态查询 |

---

## 4. 修订表设计：工装出入库单_操作日志

### 4.1 A. 现有字段（已实现）

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | BIGINT | 主键，自增 |
| 出入库单号 | VARCHAR(64) | 外键 |
| 明细ID | BIGINT | 明细ID（可选） |
| 操作类型 | VARCHAR(64) | 操作类型 |
| 操作人ID | VARCHAR(64) | 操作人ID |
| 操作人姓名 | VARCHAR(64) | 操作人姓名 |
| 操作人角色 | VARCHAR(32) | 操作人角色 |
| 变更前状态 | VARCHAR(32) | 变更前状态 |
| 变更后状态 | VARCHAR(32) | 变更后状态 |
| 操作内容 | TEXT | 操作内容 |
| 操作时间 | DATETIME | 操作时间 |

### 4.2 B. 缺失但必需的字段

无（现有字段已满足审计需求）

### 4.3 C. 推荐的生产字段

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 来源IP | VARCHAR(32) | 操作来源IP |
| 设备信息 | VARCHAR(128) | 操作设备信息 |

### 4.4 索引设计

| 索引类型 | 字段 | 说明 |
|----------|------|------|
| PK | id | 聚集索引主键 |
| IDX | 出入库单号 | 订单关联 |
| IDX | 操作时间 | 时间排序 |
| IDX | 操作人ID | 用户查询 |

---

## 5. 修订表设计：工装出入库单_通知记录

### 5.1 A. 现有字段（已实现）

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | BIGINT | 主键，自增 |
| 出入库单号 | VARCHAR(64) | 外键 |
| 通知类型 | VARCHAR(32) | 通知类型 |
| 通知渠道 | VARCHAR(32) | feishu/wechat/email |
| 接收人 | VARCHAR(255) | 接收人 |
| 通知标题 | VARCHAR(100) | 通知标题 |
| 通知内容 | TEXT | 通知内容 |
| 复制文本 | TEXT | 复制文本 |
| 发送状态 | VARCHAR(32) | pending/success/failed |
| 发送时间 | DATETIME | 发送时间 |
| 发送结果 | TEXT | 发送结果 |
| 重试次数 | INT | 重试次数 |
| 创建时间 | DATETIME | 创建时间 |

### 5.2 B. 缺失但必需的字段

| 字段名 | 数据类型 | 说明 | 建议 |
|--------|----------|------|------|
| 错误信息 | VARCHAR(500) | 错误详情 | 建议添加 |

### 5.3 C. 推荐的生产字段

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| 消息ID | VARCHAR(64) | 第三方消息ID |
| 计划发送时间 | DATETIME | 定时发送时间 |

### 5.4 索引设计

| 索引类型 | 字段 | 说明 |
|----------|------|------|
| PK | id | 聚集索引主键 |
| IDX | 出入库单号 | 订单关联 |
| IDX | 发送状态 | 状态查询 |
| IDX | 通知渠道 | 渠道查询 |

---

## 6. 修订表设计：工装位置表

### 6.1 A. 现有字段（已实现）

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | BIGINT | 主键，自增 |
| 位置编码 | VARCHAR(64) | 位置编码，唯一 |
| 位置名称 | VARCHAR(128) | 位置名称 |
| 仓库区域 | VARCHAR(64) | 仓库区域 |
| 货架号 | VARCHAR(64) | 货架号 |
| 槽位号 | VARCHAR(64) | 槽位号 |
| 完整路径 | VARCHAR(255) | 完整路径 |
| 备注 | VARCHAR(500) | 备注 |

### 6.2 B. 缺失字段

无

### 6.3 索引设计

| 索引类型 | 字段 | 说明 |
|----------|------|------|
| PK | id | 聚集索引主键 |
| UK | 位置编码 | 唯一索引 |

---

## 7. 英文逻辑别名映射

### 7.1 表级别别名

| 中文表名 | 英文别名 |
|----------|----------|
| 工装出入库单_主表 | tool_io_order |
| 工装出入库单_明细 | tool_io_order_item |
| 工装出入库单_操作日志 | tool_io_order_log |
| 工装出入库单_通知记录 | tool_io_notification |
| 工装位置表 | tool_location |
| 工装身份卡_主表 | tool_master (外部依赖) |

### 7.2 主表字段别名

| 中文列名 | 英文别名 |
|----------|----------|
| 出入库单号 | order_no |
| 单据类型 | order_type |
| 单据状态 | order_status |
| 发起人ID | initiator_id |
| 发起人姓名 | initiator_name |
| 发起人角色 | initiator_role |
| 部门 | department |
| 项目代号 | project_code |
| 用途 | usage_purpose |
| 计划使用时间 | planned_use_time |
| 计划归还时间 | planned_return_time |
| 目标位置ID | target_location_id |
| 目标位置文本 | target_location_text |
| 保管员ID | keeper_id |
| 保管员姓名 | keeper_name |
| 运输类型 | transport_type |
| 运输人ID | transport_operator_id |
| 运输人姓名 | transport_operator_name |
| 保管员需求文本 | keeper_demand_text |
| 运输通知文本 | transport_notify_text |
| 微信复制文本 | wechat_copy_text |
| 保管员确认时间 | keeper_confirm_time |
| 运输通知时间 | transport_notify_time |
| 最终确认时间 | final_confirm_time |
| 工装数量 | tool_count |
| 已确认数量 | confirmed_count |
| 最终确认人 | final_confirm_by |
| 驳回原因 | reject_reason |
| 取消原因 | cancel_reason |
| 创建时间 | created_at |
| 修改时间 | updated_at |
| 创建人 | created_by |
| 修改人 | updated_by |

### 7.3 明细表字段别名

| 中文列名 | 英文别名 |
|----------|----------|
| 出入库单号 | order_no |
| 工装ID | tool_id |
| 工装编码 | tool_code |
| 工装名称 | tool_name |
| 工装图号 | drawing_no |
| 规格型号 | spec_model |
| 申请数量 | apply_qty |
| 确认数量 | confirmed_qty |
| 明细状态 | item_status |
| 工装快照状态 | tool_snapshot_status |
| 工装快照位置ID | tool_snapshot_location_id |
| 工装快照位置文本 | tool_snapshot_location_text |
| 确认时间 | confirm_time |
| 出入库完成时间 | complete_time |

---

## 8. SQL Server 索引建议

### 8.1 工装出入库单_主表

```sql
-- 必须索引
CREATE INDEX IX_工装出入库单_主表_单据类型 ON 工装出入库单_主表(单据类型);
CREATE INDEX IX_工装出入库单_主表_单据状态 ON 工装出入库单_主表(单据状态);
CREATE INDEX IX_工装出入库单_主表_发起人ID ON 工装出入库单_主表(发起人ID);
CREATE INDEX IX_工装出入库单_主表_保管员ID ON 工装出入库单_主表(保管员ID);
CREATE INDEX IX_工装出入库单_主表_创建时间 ON 工装出入库单_主表(创建时间);
```

### 8.2 工装出入库单_明细

```sql
-- 必须索引
CREATE INDEX IX_工装出入库单_明细_出入库单号 ON 工装出入库单_明细(出入库单号);
CREATE INDEX IX_工装出入库单_明细_工装编码 ON 工装出入库单_明细(工装编码);
CREATE INDEX IX_工装出入库单_明细_明细状态 ON 工装出入库单_明细(明细状态);
```

### 8.3 工装出入库单_操作日志

```sql
-- 必须索引
CREATE INDEX IX_工装出入库单_操作日志_出入库单号 ON 工装出入库单_操作日志(出入库单号);
CREATE INDEX IX_工装出入库单_操作日志_操作时间 ON 工装出入库单_操作日志(操作时间);
```

---

## 9. 状态机支持

### 9.1 订单状态

| 状态值 | 权威存储字段 | 说明 |
|--------|--------------|------|
| draft | 单据状态 | 草稿 |
| submitted | 单据状态 | 已提交 |
| keeper_confirmed | 单据状态 | 保管员已确认 |
| partially_confirmed | 单据状态 | 部分确认 |
| transport_notified | 单据状态 | 已通知运输 |
| final_confirmation_pending | 单据状态 | 待最终确认 |
| completed | 单据状态 | 已完成 |
| rejected | 单据状态 | 已拒绝 |
| cancelled | 单据状态 | 已取消 |

### 9.2 明细状态

| 状态值 | 权威存储字段 | 说明 |
|--------|--------------|------|
| pending_check | 明细状态 | 待确认 |
| approved | 明细状态 | 已确认 |
| rejected | 明细状态 | 已拒绝 |
| completed | 明细状态 | 已完成 |

### 9.3 工装状态

工装状态存储在外部表 `工装身份卡_主表`，不在本系统管理范围内。

---

## 10. 必须修复的 Schema 清单

### 10.1 工装出入库单_主表

```sql
-- 添加缺失字段
ALTER TABLE 工装出入库单_主表 ADD 工装数量 INT NULL;
ALTER TABLE 工装出入库单_主表 ADD 已确认数量 INT NULL;
ALTER TABLE 工装出入库单_主表 ADD 最终确认人 VARCHAR(64) NULL;
ALTER TABLE 工装出入库单_主表 ADD 取消原因 VARCHAR(500) NULL;
```

### 10.2 工装出入库单_明细

```sql
-- 添加缺失字段
ALTER TABLE 工装出入库单_明细 ADD 确认时间 DATETIME NULL;
ALTER TABLE 工装出入库单_明细 ADD 出入库完成时间 DATETIME NULL;
```

### 10.3 工装出入库单_通知记录

```sql
-- 添加可选字段
ALTER TABLE 工装出入库单_通知记录 ADD 错误信息 VARCHAR(500) NULL;
```

---

## 11. 可选未来增强

| 增强项 | 表 | 说明 | 优先级 |
|--------|-----|------|--------|
| 乐观锁版本号 | 主表 | 并发控制 | 中 |
| 附件管理 | 主表 | 附件上传 | 低 |
| 批号管理 | 明细表 | 批次管理 | 低 |
| 消息ID追踪 | 通知记录 | 第三方消息追踪 | 低 |
| 定时发送 | 通知记录 | 定时通知 | 低 |

---

## 相关文档

- [数据库架构文档](./DB_SCHEMA.md)
- [继承数据库访问审查](./INHERITED_DB_ACCESS_REVIEW.md)
- [API规格文档](./API_SPEC.md)
