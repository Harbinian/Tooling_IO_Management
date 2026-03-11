# AI 开发流水线 / AI Development Pipeline

---

## 概述 / Overview

本文档描述工装出入库管理系统的 AI 驱动开发流水线，定义各 AI 代理的职责、提示词任务生命周期和标准流水线阶段。 / This document describes the AI-driven development pipeline for the Tooling IO Management System, defining the responsibilities of each AI agent, prompt task lifecycle, and standard pipeline stages.

---

## 1. 提示词驱动开发工作流 / 1 Prompt-Driven Development Workflow

本项目采用多代理协作模式，通过提示词队列驱动开发流程： / This project uses a multi-agent collaboration model, driving the development process through a prompt queue:

```
promptsRec/ 提示词队列 / Prompt Queue
      ↓
  AI Agent 执行 / AI Agent Execution
      ↓
  生成文档/代码 / Generate Docs/Code
      ↓
  归档提示词 / Archive Prompt
      ↓
  下一任务 / Next Task
```

### 核心原则 / Core Principles

- **单一职责**: 每个提示词专注于一个任务 / Single Responsibility: Each prompt focuses on one task
- **可追溯性**: 所有执行记录保存在 `logs/prompt_task_runs/` / Traceability: All execution records saved in `logs/prompt_task_runs/`
- **协作分工**: Claude Code 负责架构，Codex 负责实现，Gemini 负责前端 / Collaboration: Claude Code handles architecture, Codex handles implementation, Gemini handles frontend

---

## 2. AI 代理职责 / 2 AI Agent Responsibilities

### Claude Code

| 职责范围 / Responsibility | 说明 / Description |
|----------|------|
| 架构设计 / Architecture Design | 设计系统架构、技术选型 / Design system architecture, technology selection |
| 技术设计 / Technical Design | 数据库设计、API 规格、模块划分 / Database design, API specification, module division |
| 架构审查 / Architecture Review | 审查实现是否符合架构规范 / Review implementation against architecture specifications |
| 流水线协调 / Pipeline Coordination | 管理提示词任务队列、协调各代理 / Manage prompt task queue, coordinate agents |

### Codex

| 职责范围 / Responsibility | 说明 / Description |
|----------|------|
| 后端实现 / Backend Implementation | 业务逻辑、API 端点、服务层 / Business logic, API endpoints, service layer |
| 数据库修复 / Database Fix | Schema 修订、代码对齐 / Schema revision, code alignment |
| 前端实现 / Frontend Implementation | 页面组件、交互逻辑 / Page components, interaction logic |

### Gemini

| 职责范围 / Responsibility | 说明 / Description |
|----------|------|
| 前端设计 / Frontend Design | 页面布局、交互设计 / Page layout, interaction design |
| 组件结构 / Component Structure | 组件划分、状态管理 / Component division, state management |
| 字段映射 / Field Mapping | 前后端字段对齐 / Frontend-backend field alignment |

---

## 3. 提示词任务生命周期 / 3 Prompt Task Lifecycle

```
001_task.md          ← 提示词文件 / Prompt File
      ↓
  创建锁文件         ← 001.lock / Create Lock File
 执行任务           ← 生成文档      ↓ / Execute Task / Generate Docs
 /代码 / Code
      ↓
  删除锁文件 / Delete Lock File
      ↓
  归档提示词         ← ✅_00001_001_task_summary.md / Archive Prompt
```

### 步骤详解 / Step Details

| 步骤 / Step | 操作 / Operation | 说明 / Description |
|------|------|------|
| 1 | 发现任务 / Discover Task | 扫描 `promptsRec/` 查找待执行文件 / Scan `promptsRec/` for pending files |
| 2 | 创建锁 / Create Lock | 创建 `.lock` 文件防止并发 / Create `.lock` file to prevent concurrency |
| 3 | 读取提示词 / Read Prompt | 理解任务目标和要求 / Understand task objectives and requirements |
| 4 | 执行任务 / Execute Task | 生成所需的文档或代码 / Generate required docs or code |
| 5 | 验证完成 / Verify Completion | 检查输出是否符合要求 / Check if output meets requirements |
| 6 | 写执行报告 / Write Report | 记录执行结果到 `logs/prompt_task_runs/` / Record execution results to `logs/prompt_task_runs/` |
| 7 | 归档重命名 / Archive Rename | 使用 `✅_` 前缀重命名提示词 / Rename prompt with `✅_` prefix |
| 8 | 删除锁 / Delete Lock | 仅在归档成功后删除 / Delete only after successful archive |

---

## 4. 流水线阶段 / 4 Pipeline Stages

本项目定义了以下标准流水线阶段： / This project defines the following standard pipeline stages:

| 阶段 / Stage | 英文 / English | 执行代理 / Executor | 交付物 / Deliverables |
|------|------|----------|--------|
| 架构设计 / Architecture Design | Architecture Design | Claude Code | PRD.md, ARCHITECTURE.md |
| 技术设计 / Technical Design | Technical Design | Claude Code | DB_SCHEMA.md, API_SPEC.md |
| 数据库修订 / Database Revision | Database Revision | Claude Code | SQLSERVER_SCHEMA_REVISION.md |
| 数据库对齐 / Database Alignment | Database Alignment | Codex | 修复后的 database.py / Fixed database.py |
| 后端实现 / Backend Implementation | Backend Implementation | Codex | API 端点、业务逻辑 / API endpoints, business logic |
| 架构审查 / Architecture Review | Architecture Review | Claude Code | 审查报告 / Review report |
| 前端设计 / Frontend Design | Frontend Design | Gemini | 页面设计稿、组件结构 / Page design, component structure |
| 前端实现 / Frontend Implementation | Frontend Implementation | Gemini/Codex | 前端页面代码 / Frontend page code |
| 发布检查 / Release Precheck | Release Precheck | Claude Code | 发布检查清单 / Release checklist |

---

## 5. 目录结构 / 5 Directory Structure

```
ToolingIOManagement/
├── promptsRec/          # 提示词队列 / Prompt Queue
│   ├── 001.md          # 待执行提示词 / Pending prompts
│   └── ✅_00001_*.md   # 已归档提示词 / Archived prompts
├── docs/               # 文档 / Documentation
├── backend/            # 后端代码 / Backend code
├── frontend/           # 前端代码 / Frontend code
├── rules/              # 开发规范 / Development rules
├── skills/             # 技能定义 / Skill definitions
├── logs/
│   └── prompt_task_runs/  # 执行记录 / Execution records
```

---

## 6. 协作规则 / 6 Collaboration Rules

### Claude Code ↔ Codex

- Claude Code 提供技术设计和数据库 Schema / Claude Code provides technical design and database Schema
- Codex 依据设计文档进行实现 / Codex implements based on design documents
- 实现偏差需记录到 `logs/codex_rectification/` / Implementation deviations must be recorded to `logs/codex_rectification/`

### Claude Code ↔ Gemini

- Claude Code 提供 API 规格和字段映射 / Claude Code provides API specification and field mapping
- Gemini 依据规格设计前端界面 / Gemini designs frontend based on specifications
- 设计结果记录在提示词归档中 / Design results recorded in prompt archive

### Codex ↔ Gemini

- 通过 API_SPEC.md 协调前后端接口 / Coordinate frontend-backend interfaces through API_SPEC.md
- 字段命名必须保持一致 / Field naming must remain consistent

---

## 相关文档 / Related Documents

- [PROMPT_TASK_CONVENTION.md](./PROMPT_TASK_CONVENTION.md)
- [CLAUDE.md](./CLAUDE.md)
- [AGENTS.md](./AGENTS.md)
