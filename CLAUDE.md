# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述 / Project Overview

工装出入库管理系统 (Tooling IO Management System) - 一个基于 Flask + Vue.js 的工装/设备出入库订单管理系统，具有基于角色的工作流和飞书 (Feishu) 通知集成。

Tooling IO Management System - A Flask + Vue.js system for managing tool/equipment outbound and inbound orders with role-based workflows and Feishu notification integration.

## 架构 / Architecture

- **后端**: Flask REST API (`web_server.py`) + SQL Server 数据库 (`database.py`)
- **前端**: Vue 3 + Element Plus + Vite (位于 `frontend/`)
- **配置**: 通过 `config/settings.py` 的环境驱动设置
- **通知**: 飞书 Webhook 集成 (`utils/feishu_api.py`)

Backend: Flask REST API + SQL Server database. Frontend: Vue 3 + Element Plus + Vite. Configuration: Environment-based settings via config/settings.py. Notifications: Feishu webhook integration.

## 运行应用 / Running the Application

```powershell
# 后端 / Backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python web_server.py

# 前端 (单独终端) / Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

服务器运行在 `http://localhost:5000` (后端) 和 `http://localhost:5173` (前端)。

Server runs on port 5000 (backend) and 5173 (frontend).

## 关键命令 / Key Commands

```powershell
# 后端语法检查 / Backend syntax check
python -m py_compile web_server.py database.py backend/services/tool_io_service.py config/settings.py

# 前端构建 / Frontend build
cd frontend && npm run build

# 前端开发服务器 / Frontend dev server
cd frontend && npm run dev
```

## 数据库 / Database

表通过首次 API 调用时 `ensure_tool_io_tables()` 自动创建。核心表:

Tables are auto-created via ensure_tool_io_tables() on first API call. Core tables:

- `工装出入库单_主表` - 订单主表 / Order main table
- `工装出入库单_明细` - 订单明细项 / Order line items
- `工装出入库单_操作日志` - 操作审计跟踪 / Operation audit trail
- `工装出入库单_通知记录` - 通知历史 / Notification history

## 工作流 / Workflow

**出库**: 草稿 → 已提交 → 保管员已确认 → (运输) → 班组长最终确认 → 已完成

**入库**: 草稿 → 已提交 → 保管员已确认 → (运输) → 保管员最终确认 → 已完成

Outbound: Draft → Submitted → Keeper Confirmed → Transport → Team Leader Final Confirm → Completed

Inbound: Draft → Submitted → Keeper Confirmed → Transport → Keeper Final Confirm → Completed

## 角色 / Roles

- `team_leader` (班组长): 创建订单、出库最终确认
- `keeper` (保管员): 确认明细、拒绝订单、入库最终确认
- `admin`: 完全访问权限

team_leader: Create orders, final confirm outbound. keeper: Confirm items, reject orders, final confirm inbound. admin: Full access.

## 编码约定 / Coding Conventions

- 代码使用英文，注释允许中英双语
- 4空格缩进，函数/变量使用 `snake_case`，类使用 `PascalCase`
- 文件操作使用 `encoding='utf-8'`
- 配置集中在 `config/settings.py`，勿在整个代码库散布 `os.getenv()` 调用
- 无占位符代码 (TODO、"insert code here") - 所有代码必须完整可执行

Code in English, comments bilingual allowed. 4-space indentation, snake_case for functions/variables, PascalCase for classes. Use encoding='utf-8' for file operations. Centralize config in config/settings.py. No placeholder code - all code must be complete and executable.

## 文档真相来源 / Documentation Source of Truth

`docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/API_SPEC.md`、`docs/DB_SCHEMA.md` - 代码不得偏离这些文档，更新时必须同步修改。

docs/PRD.md, docs/ARCHITECTURE.md, docs/API_SPEC.md, docs/DB_SCHEMA.md - code must not deviate without updating these.

## 提示任务工作流 / Prompt Task Workflow

任务存储在 `promptsRec/` 并遵循生命周期:

Tasks are stored in promptsRec/ and follow a lifecycle:

1. 待处理任务: `promptsRec/*.md` / Pending tasks
2. 运行中任务: `promptsRec/*.lock` / Running tasks
3. 已完成任务: `promptsRec/✅_<5位序列>_<原始名称>.md` / Completed tasks

完成提示任务后:
- 使用 `✅_` 前缀和5位序列归档提示
- 编写运行报告到 `logs/prompt_task_runs/`

After completing a prompt task:
- Archive the prompt with the ✅_ prefix and 5-digit sequence
- Write a run report to logs/prompt_task_runs/

详见 `docs/PROMPT_TASK_CONVENTION.md` 和 `docs/AI_PIPELINE.md`。

See docs/PROMPT_TASK_CONVENTION.md and docs/AI_PIPELINE.md for full workflow details.

## 服务层架构 / Service Layer Architecture

后端使用服务层模式:

The backend uses a service layer pattern:

- `web_server.py` - Flask 路由和 HTTP 处理 / Flask routes and HTTP handling
- `backend/services/tool_io_service.py` - 业务逻辑包装器 / Business logic wrappers
- `database.py` - 直接 SQL Server 访问 (表、查询、连接池) / Direct SQL Server access
- `config/settings.py` - 集中配置 / Centralized configuration
- `utils/feishu_api.py` - 飞书 Webhook 通知 / Feishu webhook notifications

路由应使用服务层处理业务逻辑，而不是直接调用 database.py。

Routes should use the service layer for business logic rather than calling database.py directly.

## 提交风格 / Commit Style

使用祈使句主题: `fix keeper confirmation flow`、`feat: add order submission API`

Use imperative subjects: fix keeper confirmation flow, feat: add order submission API

## 测试 / Testing

- 后端: 启动 Flask 服务器并测试受影响路由 (如 `/api/tool-io-orders`、`/api/tools/search`、`/api/health`)
- 前端: 运行 `npm run build` 并手动验证受影响屏幕
- 测试位置: `tests/test_*.py`

Backend: Start Flask server and test affected routes. Frontend: Run npm run build and verify impacted screens manually. Tests location: tests/test_*.py

## 安全 / Security

永不提交凭据; 使用 `.env` (不提交) 并以 `.env.example` 为模板。

Never commit credentials; use .env (not committed) with .env.example as template.
