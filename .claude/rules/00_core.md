# 核心开发规则 / Core Development Rules

---

## 编码 / Encoding

所有生成的文件必须使用 UTF-8 (无 BOM) 编码。

```python
open(path, encoding="utf-8")
```

---

## 字段名常量使用规范 / Field Name Constant Usage

**所有 SQL 查询中的中文字段名必须使用 `backend/database/schema/column_names.py` 中定义的常量。**

### 正确用法:

```python
from backend.database.schema.column_names import ORDER_COLUMNS

sql = f"SELECT {ORDER_COLUMNS['order_no']} FROM tool_io_order"
```

### 禁止用法:

```python
# 禁止直接使用中文字段名字面量
sql = "SELECT 出入库单号 FROM tool_io_order"

# 禁止使用 Unicode 转义
sql = "SELECT \u51fa\u5165\u5e93\u5355\u53f7 FROM tool_io_order"
```

---

## 外部系统表访问规范 / External System Table Access Rules

**严禁直接修改外部系统表结构。**

| 表名 | 用途 | 访问方式 |
|------|------|----------|
| `Tooling_ID_Main` | 工装主数据 | 只读查询 + 特定字段更新，必须通过常量引用 |

### 访问规则:

1. **禁止 DDL 操作**: 严禁对外部系统表执行 `CREATE TABLE`、`ALTER TABLE`、`DROP TABLE`
2. **字段更新需通过常量**: 对外部系统表的字段更新必须通过 `column_names.py` 中的常量引用

---

## 语言标准 / Language Standard

- 代码、注释、变量名、提交信息必须使用英文
- 文档可以使用中文或中英双语
- AI CLI 交互界面使用中文输出

---

## 代码完整性 / Code Integrity

AI 严禁生成占位符代码。所有代码必须完整且可执行。

---

## 命名规则 / Naming Rules

变量和函数禁止使用拼音。使用清晰的英文名称。

```python
toolInventory
toolLocation
```

---

## 错误处理 / Error Handling

关键 I/O 或网络操作必须使用 try-except 块保护。

---

## Git 规范 / Git Discipline

每个重大功能必须对应一个 Git 提交。

```
feat: add tool_io_order schema
fix: correct tool reservation logic
```

---

## 文档权威性 / Documentation Source of Truth

| 文档 | 用途 | 更新时机 |
|------|------|----------|
| docs/PRD.md | 产品需求定义 | 功能变更前必须同步 |
| docs/ARCHITECTURE.md | 系统架构和技术选型 | 架构变更前必须同步 |
| docs/API_SPEC.md | API 接口规范 | API 变更前必须同步 |
| docs/DB_SCHEMA.md | 数据库表结构 | Schema 变更前必须同步 |
| docs/RBAC_PERMISSION_MATRIX.md | 权限矩阵 | 权限变更前必须同步 |
| backend/database/schema/column_names.py | 中文字段名常量 | 字段变更必须同步 |

### 禁止行为:

- 严禁在文档更新前进行代码实现
- 严禁跳过文档更新直接提交代码

---

## 业务规则 / Business Rule

所有仓库操作必须可追溯。每个操作必须记录：

- 操作人 (operator)
- 时间戳 (timestamp)
- 订单ID (order_id)
- 之前状态 (previous_state)
- 下一状态 (next_state)

---

## UI 一致性规则 / UI Consistency Rules

所有关键操作（提交、取消、确认、删除）必须在涉及该操作的每个页面保持一致的确认行为。

| 操作 | 必需页面 | 确认消息格式 |
|------|---------|------------|
| 提交 / Submit | OrderList.vue, OrderDetail.vue | `确认提交单据 ${orderNo} 吗？提交后将进入保管员审核流程。` |
| 取消 / Cancel | OrderDetail.vue | `确认取消单据 ${orderNo} 吗？` |
| 最终确认 / Final Confirm | OrderDetail.vue | `确认最终完成单据 ${orderNo} 吗？` |
| 删除 / Delete | OrderDetail.vue | `确认删除单据 ${orderNo} 吗？删除后不可恢复。` |

**严禁使用硬编码颜色值，必须使用 CSS 变量。**

---

## 数据库表范围 / Database Table Scope

工装出入库管理系统仅使用以下表：

### 核心业务表

| 表名 | 用途 |
|------|------|
| `tool_io_order` | 订单主表 |
| `tool_io_order_item` | 订单明细项 |
| `tool_io_operation_log` | 操作审计跟踪 |
| `tool_io_notification` | 通知发送历史 |
| `tool_io_location` | 工装位置信息 |
| `tool_io_transport_issue` | 运输异常记录 |

### 系统表

| 表名 | 用途 |
|------|------|
| `sys_org` | 组织架构 |
| `sys_user` | 用户账户 |
| `sys_role` | 角色定义 |
| `sys_permission` | 权限定义 |
| `tool_io_order_no_sequence` | 订单号序列生成 |

---

## 实现规范 / Implementation Standards

### 事务要求 / Transaction Requirements

以下操作必须使用数据库事务：

- 订单提交 / order submission
- 保管员确认 / keeper confirmation
- 最终确认 / final confirmation

### 并发控制 / Concurrency Control

- 防止重复的工装预约
- 防止并行订单冲突
- 使用行级锁或乐观锁

### 通知处理 / Notification Handling

通知发送必须：
- 记录成功
- 记录失败
- 允许重试

数据表：`tool_io_notification`
