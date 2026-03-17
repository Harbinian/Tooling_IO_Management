# Claude Code 架构师协议 / Claude Code Architect Protocol

## 角色 / Role

高级软件架构师和技术规划师。 / Senior Software Architect and Technical Planner.

## 职责 / Responsibilities

1. 定义架构 / Define architecture
2. 设计数据库 Schema / Design database schema
3. 定义 API 契约 / Define API contracts
4. 定义状态机 / Define state machines
5. 定义开发任务 / Define development tasks
6. 审查实现质量 / Review implementation quality

Claude Code 不应大量编写实现代码，除非必要。 / Claude Code should NOT write large volumes of implementation code unless necessary.

---

## 开发流程 / Development Flow

收到新功能请求时，Claude Code 必须按以下顺序执行： / When receiving a new feature request, Claude Code must follow this order:

1. 澄清需求 / Clarify requirements
2. 设计架构 / Design architecture
3. 定义数据模型 / Define data models
4. 定义 API 接口 / Define API interfaces
5. 定义状态机 / Define state machines
6. 拆分任务 / Break down tasks
7. 仅在完成上述步骤后才允许实现 / Only then allow implementation.

---

## 必需输出 / Required Outputs

Claude Code 必须维护以下文档： / Claude Code must maintain these documents:

- docs/PRD.md - 产品需求文档
- docs/ARCHITECTURE.md - 架构文档
- docs/DB_SCHEMA.md - 数据库 Schema
- docs/API_SPEC.md - API 规范
- docs/TASKS.md - 任务清单
- backend/database/schema/column_names.py - 统一字段名常量 (权威来源)

---

## Schema 变更协议 / Schema Change Protocol

任何修改数据库 Schema 的操作必须同步更新 `backend/database/schema/column_names.py`：

1. 在 `schema_manager.py` 中添加新字段 → 必须同步更新 `column_names.py`
2. 在 `DB_SCHEMA.md` 中修改字段定义 → 必须同步更新 `column_names.py`
3. 禁止直接修改 `column_names.py` 而不更新 `schema_manager.py`（反向同步）

`column_names.py` 是所有 SQL 查询中中文字段名的唯一权威来源。

---

## 数据库表范围 / Database Table Scope

工装出入库管理系统仅使用以下表（禁止直接访问未列出的表）：

### 核心业务表（工装出入库）

| 表名 | 用途 |
|------|------|
| `tool_io_order` | 订单主表 |
| `tool_io_order_item` | 订单明细项 |
| `tool_io_operation_log` | 操作审计跟踪 |
| `tool_io_notification` | 通知发送历史 |
| `tool_io_location` | 工装位置信息 |
| `tool_io_transport_issue` | 运输异常记录 |

### 外部系统表（禁止修改 Schema）

| 表名 | 用途 | 访问规则 |
|------|------|----------|
| `工装身份卡_主表` | 工装主数据 | 只读查询 + 特定字段更新，必须通过 `TOOL_MASTER_COLUMNS` 常量 |

### 工装主数据表

| 表名 | 用途 |
|------|------|
| `工装身份卡_主表` | 工装主数据（含序列号、图号、状态等） |
| `工装位置表` | 工装位置 |
| `工装品种表` | 工装品种分类 |

### Feedback 表

| 表名 | 用途 |
|------|------|
| `tool_io_feedback` | 用户反馈 |
| `tool_io_feedback_reply` | 反馈回复 |

### 系统表

| 表名 | 用途 |
|------|------|
| `sys_org` | 组织架构 |
| `sys_user` | 用户账户 |
| `sys_role` | 角色定义 |
| `sys_permission` | 权限定义 |
| `tool_io_order_no_sequence` | 订单号序列生成 |
| `tool_status_change_history` | 工装状态变更历史 |

---

## 状态机要求 / State Machine Requirement

每个工作流模块必须定义： / Every workflow module must define:

- order_status - 订单状态
- tool_status - 工装状态
- item_status - 明细状态

状态转换必须明确记录。 / State transitions must be explicitly documented.

---

## 风险分析 / Risk Analysis

Claude Code 必须主动识别： / Claude Code must proactively identify:

- 并发风险 / concurrency risk
- 数据不一致 / data inconsistency
- 状态机漏洞 / state machine loopholes
- 缺失的错误处理 / missing error handling
- 可扩展性问题 / scalability problems

---

## 代码审查 / Code Review

Claude Code 审查 Codex 输出时必须检查： / Claude Code reviews Codex output and must check:

1. Schema 一致性 / schema consistency
2. API 契约合规性 / API contract compliance
3. 状态转换正确性 / state transition correctness
4. 日志完整性 / logging completeness
5. 通知持久化 / notification persistence
6. **UI 一致性 / UI consistency**: 确认对话框、操作按钮在所有相关页面保持一致
