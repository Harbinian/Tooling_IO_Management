# 架构索引 / Architecture Index

工装出入库管理系统架构文档中心入口

---

## 概述 / Overview

本文档是系统架构文档的**中心参考地图**。/ This document serves as the **central reference map for system architecture documentation**.

所有功能实现必须参考本架构索引。/ All feature implementations must reference this architecture index.

---

## 系统架构文档 / System Architecture Documents

### 核心架构 / Core Architecture

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/ARCHITECTURE.md | 系统总体架构 / System overall architecture |
| docs/API_SPEC.md | API 规范 / API specification |
| docs/PRD.md | 产品需求文档 / Product requirements document |

---

## 安全与 RBAC / Security & RBAC

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/RBAC_DESIGN.md | RBAC 设计规范 / RBAC design specification |
| docs/RBAC_PERMISSION_MATRIX.md | 权限矩阵 / Permission matrix |
| docs/RBAC_INIT_DATA.md | RBAC 初始化数据 / RBAC initialization data |

**重要: 任何与 RBAC 相关的更改必须先阅读 RBAC_DESIGN.md**/ **Important: Any RBAC-related changes must read docs/RBAC_DESIGN.md first**

---

## 数据库设计 / Database Design

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/SCHEMA_SNAPSHOT_20260325.md | **Schema 英语化后的实际结构快照** / Actual schema snapshot after English migration |
| docs/RBAC_INIT_DATA.md | RBAC 初始化数据 / RBAC initialization data |
| docs/SQLSERVER_SCHEMA_REVISION.md | SQL Server Schema 修订 / SQL Server schema revision |

**重要: 任何数据库更改必须先阅读 SCHEMA_SNAPSHOT_20260325.md**/ **Important: Any database changes must read docs/SCHEMA_SNAPSHOT_20260325.md first**

---

## 工作流与业务逻辑 / Workflow & Business Logic

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/ARCHITECTURE.md | 订单工作流和状态机 / Order workflow and state machine |
| docs/FEISHU_CONFIGURATION.md | 飞书配置与集成 / Feishu configuration and integration |

---

## 前端架构 / Frontend Architecture

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| frontend/src/ | 前端源代码 / Frontend source code |
| frontend/src/pages/ | 页面组件 / Page components |
| frontend/src/components/ | 可复用组件 / Reusable components |

---

## 需求文档 / Requirements

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/REQUIREMENTS/ | 需求文档目录 / Requirements documents directory |

---

## AI 开发工作流 / AI Development Workflow

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| .claude/rules/05_task_convention.md | 提示词任务编号约定 / Prompt task numbering convention |
| .claude/rules/01_workflow.md | ADP 四阶段开发流程 / ADP four-phase workflow |
| .claude/rules/02_debug.md | 8D 问题解决协议 / 8D problem solving protocol |
| .claude/rules/03_hotfix.md | 热修复 SOP / Hotfix SOP |

---

## 项目管理与运维 / Project Management & Operations

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/REPO_CONTEXT_FIREWALL.md | 仓库上下文隔离报告 / Repo context firewall report |
| docs/SKILLS_CLAUDE_RULES_CONSOLIDATION.md | 技能与规则整合记录 / Skills and rules consolidation record |
| docs/G1-4_DETECT_SECRETS_SETUP.md | G1-4 secrets 检测配置 / G1-4 detect-secrets setup |

---

## 归档文档 / Archived Documents

已完成或过时的文档归档在 `docs/archive/` 目录下。/ Completed or outdated documents are archived in `docs/archive/`.

包括：过往实现记录、Bug 修复报告、测试报告、架构审查记录等。/ Includes: past implementation records, bug fix reports, test reports, architecture review records, etc.

---

## 架构使用规则 / Architecture Usage Rules

### 实现前必须加载的文档 / Documents to Load Before Implementation

在实现任何功能之前，模型必须首先加载: / Before implementing any feature, models must first load:

1. `docs/ARCHITECTURE_INDEX.md` (本文档) / (this document)
2. 然后根据任务类型加载相关架构文档 / Then load relevant architecture documents based on task type

### 具体任务类型 / Specific Task Types

| 任务类型 / Task Type | 必须加载的文档 / Required Documents |
|---------------------|-----------------------------------|
| 认证 / Authentication | docs/RBAC_DESIGN.md, docs/API_SPEC.md |
| 授权 / Authorization | docs/RBAC_DESIGN.md, docs/RBAC_PERMISSION_MATRIX.md |
| 数据库 Schema / Database Schema | SCHEMA_SNAPSHOT_20260325.md, docs/RBAC_INIT_DATA.md |
| 状态机 / State Machine | docs/ARCHITECTURE.md, docs/API_SPEC.md |
| Bug 修复 / Bug Fix | .claude/rules/02_debug.md |

---

## 文档版本 / Document Version

| 版本 / Version | 日期 / Date | 描述 / Description |
|---------------|-------------|-------------------|
| 2.0 | 2026-04-10 | 清理不存在的文档引用，更新索引结构 / Clean up non-existent document references, update index structure |

---

## 维护 / Maintenance

本索引文档由架构师维护。/ This index document is maintained by the architect.

任何新增架构文档应更新本文档。/ Any new architecture documents should update this document.

**重要: 在实现任何功能之前，始终先参考本架构索引**/ **Important: Always reference this architecture index before implementing any feature**
