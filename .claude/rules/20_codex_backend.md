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

## 字段名常量使用 / Field Name Constant Usage

**所有 SQL 查询中的中文字段名必须使用 `backend/database/schema/column_names.py` 中定义的常量。**

Codex 实现时必须：

1. 导入所需的列名常量：`from backend.database.schema.column_names import ORDER_COLUMNS, ITEM_COLUMNS, ...`
2. 在 SQL 字符串中使用常量引用中文字段名
3. 禁止在 SQL 字符串中直接使用中文字段名字面量

### 正确示例:

```python
from backend.database.schema.column_names import ORDER_COLUMNS, ITEM_COLUMNS

# Correct: use constants with English table name
sql = f"SELECT {ORDER_COLUMNS['order_no']}, {ORDER_COLUMNS['order_status']} FROM tool_io_order"

# Correct: parameterize column names in dynamic queries
column_name = ORDER_COLUMNS['order_no']
sql = f"SELECT {column_name} FROM tool_io_order WHERE {ORDER_COLUMNS['order_status']} = ?"
```

### 禁止示例:

```python
# Forbidden: direct Chinese characters in SQL
sql = "SELECT order_no FROM tool_io_order"

# Forbidden: using Chinese table names directly
sql = "SELECT order_no FROM 工装出入库单_主表"
```

### 已知字段名映射参考:

| 逻辑名 | 英文字段名 |
|--------|-----------|
| order_no | order_no |
| order_status | order_status |
| transport_operator_id | transport_operator_id |
| transport_operator_name | transport_operator_name |

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

---

## 前端 UI 一致性配合 / Frontend UI Consistency Coordination

Codex 实现后端 API 时，必须确保：

1. **API 响应一致性**: 确保相同操作的 API 在不同端点返回一致的数据结构
2. **错误消息一致性**: 错误消息应使用中文，与前端显示一致
3. **状态码一致性**: 使用 `docs/API_SPEC.md` 中定义的标准状态码

如果后端修改可能影响前端 UI 行为，必须通知 Claude Code 进行审查。
