# AI 协作规则 / AI Collaboration Rules

---

## 概述 / Overview

本文档定义多个AI Agent协同开发时的协作规则和职责划分。 / This document defines collaboration rules and responsibility division when multiple AI Agents collaborate on development.

---

## Agent 角色定义 / Agent Role Definition

| Agent | 角色 / Role | 主要职责 / Primary Responsibilities |
|-------|------|----------|
| CC (Claude Code) | 首席架构师 / Chief Architect | 架构设计、状态机、任务规划、文档审查 / Architecture design, state machines, task planning, document review |
| Codex | 后端工程师 / Backend Engineer | 后端实现、数据库集成、服务层、API开发 / Backend implementation, database integration, service layer, API development |
| Gemini | 前端工程师 / Frontend Engineer | 前端页面、用户体验、字段映射 / Frontend pages, user experience, field mapping |

---

## CC (Claude Code) 职责 / CC (Claude Code) Responsibilities

### 架构设计 / Architecture Design

- 设计系统架构和技术选型 / Design system architecture and technology selection
- 定义数据库表结构 / Define database table structure
- 设计状态机流转规则 / Design state machine transition rules
- 制定API接口规范 / Define API interface specifications

### 文档产出 / Document Output

- 编写/更新 PRD.md
- 编写/更新 ARCHITECTURE.md
- 编写/更新 DB_SCHEMA.md
- 编写/更新 API_SPEC.md
- 编写/更新 TASKS.md
- 编写/更新 COLLABORATION.md
- 编写 INHERITED_DB_ACCESS_REVIEW.md

### 代码审查 / Code Review

- 审查后端代码质量 / Review backend code quality
- 审查前端代码质量 / Review frontend code quality
- 确保实现符合架构设计 / Ensure implementation follows architecture design
- 审查与现有数据库模块的一致性 / Review consistency with existing database modules

### 任务规划 / Task Planning

- 分解开发阶段 / Break down development phases
- 定义任务依赖关系 / Define task dependencies
- 指定任务负责Agent / Assign responsible agents for tasks
- 标记任务类型（修复/扩展/新增）/ Mark task types (fix/extension/new)

---

## Codex 职责 / Codex Responsibilities

### 核心约束 / Core Constraints

- **必须**在现有 database.py 模块基础上进行开发 / **Must** develop based on existing database.py module
- **禁止**引入全新的 ORM/Repository 模式（除非获得批准）/ **Prohibited** from introducing new ORM/Repository patterns (unless approved)
- **必须**复用现有的 CRUD 函数 / **Must** reuse existing CRUD functions
- **必须**保持 SQL Server + pyodbc 兼容性 / **Must** maintain SQL Server + pyodbc compatibility

### 后端实现 / Backend Implementation

- 修复现有 database.py 中的 schema 不一致 / Fix schema inconsistencies in existing database.py
- 实现 REST API 接口 / Implement REST API endpoints
- 集成现有数据库 CRUD 脚本 / Integrate existing database CRUD scripts
- 实现业务逻辑 / Implement business logic
- 实现通知服务 / Implement notification service

### 数据访问 / Data Access

- 使用现有的 DatabaseManager 和 ConnectionPool / Use existing DatabaseManager and ConnectionPool
- 使用参数化查询 / Use parameterized queries
- 实现事务管理 / Implement transaction management
- 创建/修改数据库表 / Create/modify database tables

### 服务层 / Service Layer

- 在现有函数基础上包装服务层 / Wrap service layer on existing functions
- 扩展而非替换现有模块 / Extend rather than replace existing modules

### 代码规范 / Code Standards

- 遵循 PEP 8 / Follow PEP 8
- 添加必要的类型注解 / Add necessary type annotations
- 编写清晰的注释 / Write clear comments
- 处理异常情况 / Handle exceptions

---

## Gemini 职责 / Gemini Responsibilities

### 前端页面 / Frontend Pages

- 订单列表页面 / Order list page
- 创建订单页面 / Order creation page
- 订单详情页面 / Order detail page
- 保管员工作台 / Keeper workstation

### 用户体验 / User Experience

- 表单验证 / Form validation
- 错误提示 / Error messages
- 加载状态 / Loading states
- 响应式布局 / Responsive layout

### 字段映射 / Field Mapping

- API 响应到前端数据的映射 / API response to frontend data mapping
- 表单数据到 API 请求的映射 / Form data to API request mapping
- 状态码到用户友好消息的转换 / Status code to user-friendly message conversion

### 组件开发 / Component Development

- 工装搜索组件 / Tool search component
- 工装选择组件 / Tool selection component
- 状态展示组件 / Status display component
- 操作按钮组件 / Action button component

---

## 单一事实来源 / Single Source of Truth (Single Source of Truth)

以下文档作为开发的唯一事实来源： / The following documents serve as the single source of truth for development:

| 文档 / Document | 用途 / Purpose |
|------|------|
| docs/PRD.md | 产品需求定义 / Product requirements definition |
| docs/ARCHITECTURE.md | 架构设计规范 / Architecture design specifications |
| docs/DB_SCHEMA.md | 数据库结构定义 / Database structure definition |
| docs/API_SPEC.md | API接口规范 / API interface specifications |
| docs/INHERITED_DB_ACCESS_REVIEW.md | 现有数据库模块审查 / Existing database module review |

### 文档更新规则 / Document Update Rules

1. **禁止绕过文档** / **Prohibited to bypass documents**
   - 实现必须遵循文档 / Implementation must follow documents
   - 不得在文档外增加功能 / Must not add features outside documents

2. **文档更新流程** / **Document update process**
   - CC 负责更新架构类文档 / CC is responsible for updating architecture documents
   - Codex 负责报告 schema 不一致 / Codex is responsible for reporting schema inconsistencies
   - 更新前需确认影响范围 / Confirm impact scope before updating
   - 更新后通知相关 Agent / Notify relevant agents after updating

3. **实现与文档一致性** / **Implementation and document consistency**
   - Codex 实现需符合 DB_SCHEMA.md 和 API_SPEC.md / Codex implementation must conform to DB_SCHEMA.md and API_SPEC.md
   - Gemini 实现需符合 API_SPEC.md / Gemini implementation must conform to API_SPEC.md

---

## API 修改规则 / API Modification Rules

### 禁止随意修改 / Prohibited to arbitrarily modify

- 不得随意修改 API 接口 / Must not arbitrarily modify API interfaces
- 不得随意修改数据库表结构 / Must not arbitrarily modify database table structure

### 修改流程 / Modification Process

1. 提出修改申请 / Submit modification request
2. CC 评估影响 / CC evaluates impact
3. 更新相关文档 / Update related documents
4. 通知实现 Agent / Notify implementation agent
5. 同步修改代码 / Synchronize code changes

---

## Schema 合规 / Schema Compliance

### 数据库 Schema / Database Schema

- 表结构必须符合 DB_SCHEMA.md / Table structure must conform to DB_SCHEMA.md
- 字段类型、长度必须匹配 / Field types and lengths must match
- 索引定义必须遵循 / Index definitions must be followed

### 现有实现一致性 / Existing Implementation Consistency

- Codex 必须审查现有 database.py 代码 / Codex must review existing database.py code
- 发现 schema 不一致必须报告 / Schema inconsistencies must be reported
- 修复后才能继续开发 / Development can only continue after fixes

### API Schema / API Schema

- 请求参数必须符合 API_SPEC.md / Request parameters must conform to API_SPEC.md
- 响应格式必须符合 API_SPEC.md / Response format must conform to API_SPEC.md
- 错误码必须统一 / Error codes must be unified

### 代码审查 / Code Review

- Codex 提交代码前自查 / Codex self-checks before submitting code
- CC 进行代码审查 / CC performs code review
- 不符合 Schema 的代码必须修改 / Code that does not conform to Schema must be modified

---

## 协作流程 / Collaboration Process

### Phase 启动流程 / Phase Start Process

1. CC 完成文档设计 / CC completes document design
2. CC 指定负责 Agent / CC assigns responsible agent
3. Agent 读取相关文档和现有代码 / Agent reads relevant documents and existing code
4. Agent 开始实现 / Agent starts implementation

### Phase 交接流程 / Phase Handover Process

1. 完成当前 Phase 任务 / Complete current Phase tasks
2. Codex 自查代码 / Codex self-checks code
3. CC 审查代码 / CC reviews code
4. 确认后进入下一 Phase / Confirm and move to next Phase

### 问题升级流程 / Issue Escalation Process

1. Agent 遇到问题 / Agent encounters issue
2. 尝试自行解决 / Try to resolve independently
3. 无法解决时升级给 CC / Escalate to CC when unable to resolve
4. CC 给出解决方案 / CC provides solution
5. 更新相关文档（如需要）/ Update related documents (if needed)

---

## 沟通规范 / Communication Standards

### 文档优先 / Documentation First

- 优先通过文档沟通 / Prioritize communication through documents
- 减少口头沟通依赖 / Reduce reliance on verbal communication
- 文档是唯一事实来源 / Documents are the single source of truth

### 变更通知 / Change Notification

- 文档更新后通知 / Notify after document updates
- 重大变更需确认 / Major changes require confirmation
- 保持文档时效性 / Keep documents up-to-date

---

## 相关文档 / Related Documents

- [产品需求文档 / Product Requirements Document](./PRD.md)
- [架构文档 / Architecture Document](./ARCHITECTURE.md)
- [数据库架构文档 / Database Architecture Document](./DB_SCHEMA.md)
- [API规格文档 / API Specification Document](./API_SPEC.md)
- [继承数据库访问审查 / Inherited Database Access Review](./INHERITED_DB_ACCESS_REVIEW.md)
- [任务分解文档 / Task Breakdown Document](./TASKS.md)
