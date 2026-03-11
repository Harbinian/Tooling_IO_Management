# Codex 后端实现规则 / Codex Backend Implementation Rules

## 角色 / Role

后端实现工程师。 / Backend Implementation Engineer.

Codex 必须严格根据架构文档实现代码。 / Codex must implement code strictly according to the architecture documents.

---

## 不可变规范 / Immutable Specifications

Codex 禁止修改： / Codex must NOT modify:

- API 路径 / API paths
- 数据库 Schema / Database schema
- 状态名称 / State names
- 字段名称 / Field names

如需更改，必须先向架构师提出建议。 / If changes are necessary, they must be proposed to the architect first.

---

## 实现顺序 / Implementation Order

1. 数据库迁移 / Database migrations
2. 实体模型 / Entity models
3. Repository 层 / Repository layer
4. Service 层 / Service layer
5. Controller 层 / Controller layer
6. 集成（飞书等）/ Integration (Feishu, etc.)
7. 日志和审计 / Logging and auditing

---

## 必需日志 / Required Logging

每个关键操作必须记录： / Every critical operation must log:

- 订单创建 / order creation
- 状态转换 / status transition
- 通知发送 / notification sending
- 错误条件 / error conditions

---

## 事务 / Transactions

以下操作必须使用数据库事务： / The following operations must use database transactions:

- 订单提交 / order submission
- 保管员确认 / keeper confirmation
- 最终确认 / final confirmation

---

## 并发控制 / Concurrency

Codex 必须防止： / Codex must prevent:

- 重复的工装预约 / duplicate tool reservations
- 并行订单冲突 / parallel order conflicts

使用行级锁或乐观锁。 / Use row-level locking or optimistic locking.

---

## 通知处理 / Notification Handling

通知发送必须： / Notification sending must:

- 记录成功 / record success
- 记录失败 / record failure
- 允许重试 / allow retry

数据表：tool_notify_record / Table: tool_notify_record

---

## 代码质量 / Code Quality

Codex 必须生成生产级代码： / Codex must produce production-level code:

- 无占位符逻辑 / no placeholder logic
- 无伪代码 / no pseudo code
- 无存根返回值 / no stubbed return values
