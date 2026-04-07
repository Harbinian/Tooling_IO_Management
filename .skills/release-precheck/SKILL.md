---
name: release-precheck
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/07_ci_gates.md
version: 1.0.0
---

# 发布预检技能 / RELEASE PRECHECK

---

## 目的 / Purpose

在发布项目之前执行最终的系统一致性审查。/ Perform a final system consistency review before releasing the project.

此技能验证文档、后端实现、数据库 Schema 和前端集成的内部一致性。/ This skill verifies that documentation, backend implementation, database schema, and frontend integration are internally consistent.

此技能不修改项目文件，仅生成最终报告。/ This skill does NOT modify project files except for generating the final report.

---

## 必需的项目文档 / Required Project Documents

检查以下文件（如果存在）: / Check the following files if they exist:

```
docs/PRD.md
docs/ARCHITECTURE.md
docs/DB_SCHEMA.md
docs/API_SPEC.md
docs/SQLSERVER_SCHEMA_REVISION.md
docs/FRONTEND_DESIGN.md
```

---

## 检查项 / Checks

### 1 API 一致性 / API Consistency

验证后端 API 与规范匹配: / Verify backend APIs match the specification:

`docs/API_SPEC.md`

检查: / Check:

- 端点路径 / endpoint paths
- HTTP 方法 / HTTP methods
- 请求参数 / request parameters
- 响应字段 / response fields

报告不匹配项。 / Report mismatches.

---

### 2 数据库一致性 / Database Consistency

验证数据库 Schema 使用与以下文档匹配: / Verify database schema usage matches:

```
docs/DB_SCHEMA.md
docs/SQLSERVER_SCHEMA_REVISION.md
```

检查: / Check:

- 后端代码中引用的表是否存在 / tables referenced in backend code exist
- 代码中引用的字段是否存在 / fields referenced in code exist
- 无效的 INSERT 或 UPDATE 语句 / no invalid INSERT or UPDATE statements

---

### 3 状态机验证 / State Machine Validation

验证订单工作流状态。 / Verify order workflow states.

预期状态可能包括: / Expected states may include:

```
draft - 草稿
submitted - 已提交
keeper_confirmed - 保管员已确认
transport_notified - 运输已通知
completed - 已完成
rejected - 已拒绝
cancelled - 已取消
```

检查: / Check for:

- 无效转换 / invalid transitions
- 缺失状态 / missing states
- 不可达状态 / unreachable states

---

### 4 审计日志 / Audit Logging

验证关键操作存在日志: / Verify logging exists for critical actions:

- 创建 / create
- 提交 / submit
- 保管员确认 / keeper confirm
- 通知运输 / notify transport
- 最终确认 / final confirm
- 拒绝 / reject
- 取消 / cancel

日志应包括: / Logs should include:

- 订单ID / order_id
- 操作人 / operator
- 操作类型 / action_type
- 时间戳 / timestamp

---

### 5 通知持久化 / Notification Persistence

验证通知记录已存储。 / Verify notification records are stored.

检查: / Check:

- 通知表存在 / notification table exists
- 消息内容已存储 / message content stored
- 发送状态已存储 / send status stored
- 时间戳已记录 / timestamps recorded

---

### 6 前端和 API 映射 / Frontend and API Mapping

验证前端字段与后端 API 响应匹配。 / Verify frontend fields match backend API responses.

检查: / Check:

- 字段名 / field names
- 必填字段 / required fields
- 状态值 / status values
- ID 引用 / ID references

---

## 输出 / Output

生成报告: / Generate report:

`docs/RELEASE_PRECHECK_REPORT.md`

报告必须包含: / The report must contain:

- 系统概览 / system overview
- 检测到的不一致 / detected inconsistencies
- 严重性分类 / severity classification
- 建议的修复 / recommended fixes

严重性级别: / Severity levels:

- 严重 / Critical
- 高 / High
- 中 / Medium
- 低 / Low

---

## 约束 / Constraints

此技能严禁: / This skill must NOT:

- 修改后端代码 / modify backend code
- 修改数据库 Schema / modify database schema
- 修改前端代码 / modify frontend code
- 重命名文件 / rename files
- 删除文件 / delete files

它仅执行分析并生成发布预检报告。 / It only performs analysis and produces the release precheck report.
