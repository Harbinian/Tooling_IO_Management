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
| docs/ARCHITECTURE_REVIEW.md | 架构审查记录 / Architecture review records |
| docs/DB_SCHEMA.md | 数据库 Schema 定义 / Database schema definition |
| docs/API_SPEC.md | API 规范 / API specification |
| docs/PRD.md | 产品需求文档 / Product requirements document |

---

## 安全与 RBAC / Security & RBAC

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/RBAC_DESIGN.md | RBAC 设计规范 / RBAC design specification |
| docs/RBAC_DATABASE_SCHEMA.md | RBAC 数据库 Schema / RBAC database schema |
| docs/RBAC_INIT_DATA.md | RBAC 初始化数据 / RBAC initialization data |

**重要: 任何与 RBAC 相关的更改必须先阅读 RBAC_DESIGN.md**/ **Important: Any RBAC-related changes must read RBAC_DESIGN.md first**

---

## 数据库设计 / Database Design

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/DB_SCHEMA.md | 主数据库 Schema / Main database schema |
| docs/RBAC_DATABASE_SCHEMA.md | RBAC 数据库 Schema / RBAC database schema |
| docs/SQLSERVER_SCHEMA_REVISION.md | SQL Server Schema 修订 / SQL Server schema revision |
| docs/DATABASE_ALIGNMENT_IMPLEMENTATION.md | 数据库对齐实现 / Database alignment implementation |
| docs/DATABASE_SETTINGS_COMPATIBILITY_FIX.md | 数据库设置兼容性修复 / Database settings compatibility fix |
| docs/INHERITED_DB_ACCESS_REVIEW.md | 继承数据库访问审查 / Inherited database access review |

**重要: 任何数据库更改必须先阅读 RBAC_DATABASE_SCHEMA.md**/ **Important: Any database changes must read RBAC_DATABASE_SCHEMA.md first**

---

## 工作流与业务逻辑 / Workflow & Business Logic

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/ORDER_SUBMISSION_IMPLEMENTATION.md | 订单提交流程实现 / Order submission workflow implementation |
| docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md | 保管员确认流程 / Keeper confirmation workflow |
| docs/FINAL_CONFIRMATION_IMPLEMENTATION.md | 最终确认流程 / Final confirmation workflow |
| docs/NOTIFICATION_RECORD_USAGE_IMPLEMENTATION.md | 通知记录使用 / Notification record usage |
| docs/FEISHU_INTEGRATION_IMPLEMENTATION.md | 飞书集成实现 / Feishu integration implementation |

---

## 前端架构 / Frontend Architecture

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/FRONTEND_DESIGN.md | 前端设计 / Frontend design |
| docs/FRONTEND_UI_COMPONENT_MAP.md | 前端 UI 组件映射 / Frontend UI component map |
| docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md | 前端 UI 基础实现 / Frontend UI foundation implementation |
| docs/FRONTEND_STYLE_MIGRATION_PLAN.md | 前端样式迁移计划 / Frontend style migration plan |
| docs/ORDER_LIST_UI_MIGRATION.md | 订单列表 UI 迁移 / Order list UI migration |
| docs/ORDER_DETAIL_UI_MIGRATION.md | 订单详情 UI 迁移 / Order detail UI migration |
| docs/ORDER_CREATE_UI_MIGRATION.md | 订单创建 UI 迁移 / Order create UI migration |
| docs/KEEPER_PROCESS_UI_MIGRATION.md | 保管员流程 UI 迁移 / Keeper process UI migration |
| docs/STRUCTURED_MESSAGE_PREVIEW_UI.md | 结构化消息预览 UI / Structured message preview UI |
| docs/TOOL_SEARCH_DIALOG_IMPLEMENTATION.md | 工装搜索对话框实现 / Tool search dialog implementation |
| docs/TOOL_MASTER_FIELD_MAPPING.md | 工装主数据字段映射 / Tool master field mapping |
| docs/TOOL_SEARCH_DB_INTEGRATION.md | 工装搜索数据库集成 / Tool search database integration |

---

## AI 开发工作流 / AI Development Workflow

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/AI_DEVOPS_ARCHITECTURE.md | AI DevOps 架构 / AI DevOps architecture |
| docs/AI_DEVOPS_SYSTEM_ARCHITECTURE.md | AI DevOps 系统架构 / AI DevOps system architecture |
| docs/AI_PIPELINE.md | AI 流水线 / AI pipeline |
| docs/PROMPT_TASK_CONVENTION.md | 提示词任务规范 / Prompt task convention |
| docs/COLLABORATION.md | 协作规范 / Collaboration guidelines |

---

## Bug 处理 / Bug Handling

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/BUG_WORKFLOW_RULES.md | Bug 工作流规则 / Bug workflow rules |
| docs/INCIDENT_RESPONSE_FLOW.md | 事件响应流程 / Incident response flow |
| docs/TROUBLESHOOTING_FRONTEND_API_ERRORS.md | 前端 API 错误排查 / Frontend API error troubleshooting |
| docs/RELEASE_PRECHECK_REPORT.md | 发布预检报告 / Release precheck report |

### Bug 修复记录 / Bug Fix Records

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/BUG_TOOL_SEARCH_REQUEST_ROUTING.md | 工装搜索请求路由 Bug / Tool search request routing bug |
| docs/BUG_VITE_ENTRY_COMPILE_FAILURE.md | Vite 入口编译失败 Bug / Vite entry compile failure bug |
| docs/BUG_ORDER_LIST_API_500.md | 订单列表 API 500 错误 Bug / Order list API 500 error bug |
| docs/BUG_DUPLICATE_SIDEBAR_LAYOUT_CONFLICT.md | 重复侧边栏布局冲突 Bug / Duplicate sidebar layout conflict bug |

---

## 项目管理 / Project Management

| 文档 / Document | 描述 / Description |
|----------------|-------------------|
| docs/TASKS.md | 任务列表 / Task list |
| docs/README_AI_SYSTEM.md | AI 系统自述 / AI system README |

---

## 架构使用规则 / Architecture Usage Rules

### RBAC 相关 / RBAC Related

1. 任何与 RBAC 相关的更改必须先阅读 `docs/RBAC_DESIGN.md`。
   / Any RBAC-related changes must read `docs/RBAC_DESIGN.md` first.

2. 任何权限相关的更改必须先阅读 `docs/RBAC_DATABASE_SCHEMA.md`。
   / Any permission-related changes must read `docs/RBAC_DATABASE_SCHEMA.md` first.

3. 任何权限初始化必须参考 `docs/RBAC_INIT_DATA.md`。
   / Any permission initialization must reference `docs/RBAC_INIT_DATA.md`.

4. 禁止在未检查这些文档的情况下重新定义 RBAC 逻辑。
   / No model should redefine RBAC logic without checking these documents.

### 数据库相关 / Database Related

1. 任何数据库 Schema 更改必须先阅读 `docs/RBAC_DATABASE_SCHEMA.md`。
   / Any database schema changes must read `docs/RBAC_DATABASE_SCHEMA.md` first.

2. 任何数据库更改必须参考 `docs/DB_SCHEMA.md`。
   / Any database changes must reference `docs/DB_SCHEMA.md`.

3. SQL Server 特定更改必须参考 `docs/SQLSERVER_SCHEMA_REVISION.md`。
   / SQL Server-specific changes must reference `docs/SQLSERVER_SCHEMA_REVISION.md`.

### API 相关 / API Related

1. 任何 API 更改必须先阅读 `docs/API_SPEC.md`。
   / Any API changes must read `docs/API_SPEC.md` first.

2. 任何新端点实现必须与 API 规范对齐。
   / Any new endpoint implementation must align with the API specification.

### 前端相关 / Frontend Related

1. 任何前端 UI 更改必须参考 `docs/FRONTEND_UI_COMPONENT_MAP.md`。
   / Any frontend UI changes must reference `docs/FRONTEND_UI_COMPONENT_MAP.md`.

2. 任何样式更改必须参考 `docs/FRONTEND_STYLE_MIGRATION_PLAN.md`。
## AI 模型工作流 / AI Model Workflow

### 实现前必须加载的文档 / Documents to Load Before Implementation

在实现任何后端逻辑之前，模型必须首先加载: / Before implementing any backend logic, models must first load:

1. `docs/ARCHITECTURE_INDEX.md` (本文档) / (this document)
2. 然后根据任务类型加载相关架构文档 / Then load relevant architecture documents based on task type

### 具体任务类型 / Specific Task Types

| 任务类型 / Task Type | 必须加载的文档 / Required Documents |
|---------------------|-----------------------------------|
| 认证 / Authentication | docs/RBAC_DESIGN.md, docs/API_SPEC.md |
| 授权 / Authorization | docs/RBAC_DESIGN.md, docs/RBAC_DATABASE_SCHEMA.md |
| 数据库 Schema / Database Schema | docs/RBAC_DATABASE_SCHEMA.md, docs/DB_SCHEMA.md |
| 状态机 / State Machine | docs/ARCHITECTURE.md, docs/API_SPEC.md |
| 前端 UI / Frontend UI | docs/FRONTEND_UI_COMPONENT_MAP.md, docs/FRONTEND_DESIGN.md |
| Bug 修复 / Bug Fix | docs/BUG_WORKFLOW_RULES.md, 相关 Bug 文档 / Related bug document |

### RUNPROMPT 集成 / RUNPROMPT Integration

在执行任何提示词任务之前: / Before executing any prompt task:

1. 加载 `docs/ARCHITECTURE_INDEX.md`
2. 识别相关架构文档
3. 加载相关文档
4. 开始实现

---

## 文档版本 / Document Version

| 版本 / Version | 日期 / Date | 描述 / Description |
|---------------|-------------|-------------------|
| 1.0 | 2026-03-12 | 初始版本 / Initial version |

---

## 维护 / Maintenance

本索引文档由架构师维护。/ This index document is maintained by the architect.

任何新增架构文档应更新本文档。/ Any new architecture documents should update this document.

**重要: 在实现任何功能之前，始终先参考本架构索引**/ **Important: Always reference this architecture index before implementing any feature**