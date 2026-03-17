# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述 / Project Overview

工装出入库管理系统 (Tooling IO Management System) - 基于 Flask + Vue.js 的工装/设备出入库订单管理系统，具有基于角色的工作流和飞书 (Feishu) 通知集成。

Backend: Flask REST API + SQL Server (pyodbc). Frontend: Vue 3 + Element Plus + Vite. Configuration: Environment-based via config/settings.py. Notifications: Feishu webhook integration.

## 架构 / Architecture

- **后端**: Flask REST API (`web_server.py`) + SQL Server (`database.py`)
- **前端**: Vue 3 + Element Plus + Vite (`frontend/src/`)
- **配置**: 环境驱动设置 (`config/settings.py`)
- **通知**: 飞书 Webhook (`utils/feishu_api.py`)
- **服务层**: `backend/services/tool_io_service.py`

## 运行应用 / Running the Application

```powershell
# 后端 / Backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python web_server.py

# 前端 (单独终端) / Frontend
cd frontend
npm install
npm run dev
```

服务端口: `http://localhost:8151` (后端), `http://localhost:8150` (前端)

## 关键 API 路由 / Key API Routes

| 端点 | 说明 |
|------|------|
| `GET /api/tool-io-orders` | 订单列表 (支持分页/过滤) |
| `POST /api/tool-io-orders` | 创建订单 |
| `GET /api/tool-io-orders/<order_no>` | 订单详情 |
| `POST /api/tool-io-orders/<order_no>/submit` | 提交订单 |
| `POST /api/tool-io-orders/<order_no>/keeper-confirm` | 保管员确认 |
| `POST /api/tool-io-orders/<order_no>/confirm-final` | 最终确认 |
| `POST /api/tool-io-orders/<order_no>/reject` | 拒绝订单 |
| `GET /api/tools/search` | 工装搜索 |
| `POST /api/tool-io-orders/<order_no>/notify-transport` | 运输通知 |
| `GET /api/health` | 健康检查 |

## 关键命令 / Key Commands

```powershell
# 后端语法检查 / Backend syntax check
python -m py_compile web_server.py database.py backend/services/tool_io_service.py config/settings.py

# 前端构建 / Frontend build
cd frontend && npm run build
```

## 数据库 / Database

表通过首次 API 调用时 `ensure_tool_io_tables()` 自动创建。核心表:

- `tool_io_order` - 订单主表
- `tool_io_order_item` - 订单明细项
- `tool_io_operation_log` - 操作审计跟踪
- `tool_io_notification` - 通知历史
- `tool_io_location` - 工装位置信息
- `tool_io_transport_issue` - 运输异常记录

RBAC 表: `sys_org`, `sys_user`, `sys_role`, `sys_permission`, `tool_io_order_no_sequence`

> **注意**: `工装身份卡_主表` 是外部系统表，禁止修改其 Schema，必须通过 `column_names.py` 中的常量访问。

## 工作流 / Workflow

**出库**: 草稿 → 已提交 → 保管员已确认 → (运输) → 班组长最终确认 → 已完成

**入库**: 草稿 → 已提交 → 保管员已确认 → (运输) → 保管员最终确认 → 已完成

## 角色 / Roles

- `team_leader` (班组长): 创建订单、出库最终确认
- `keeper` (保管员): 确认明细、拒绝订单、入库最终确认
- `admin`: 完全访问权限

## 编码约定 / Coding Conventions

- 代码使用英文，注释允许中英双语
- 4空格缩进，`snake_case` 函数/变量，`PascalCase` 类
- 文件操作使用 `encoding='utf-8'`
- 配置集中在 `config/settings.py`，勿散布 `os.getenv()`
- 无占位符代码 - 所有代码必须完整可执行

## 前端结构 / Frontend Structure

```
frontend/src/
├── pages/          # 页面组件 (OrderList.vue, OrderDetail.vue, OrderCreate.vue)
├── components/     # 可复用 UI 组件
├── api/            # API 包装器
├── store/          # 共享状态 (Pinia)
└── router/         # 路由配置
```

## 服务层架构 / Service Layer Architecture

```
web_server.py                  → Flask 路由和 HTTP 处理
backend/routes/*.py            → API 路由层
backend/services/*.py         → 业务逻辑层 (tool_io_service, notification_service 等)
backend/database/repositories/*.py → 数据访问层 (order_repository, tool_repository 等)
backend/database/core/*.py    → 数据库核心 (connection_pool, executor, database_manager)
backend/database/schema/*.py  → Schema 管理 (schema_manager.py, column_names.py)
database.py                    → SQL Server 直接访问
config/settings.py             → 集中配置
utils/feishu_api.py            → 飞书 Webhook 通知
```

**路由 → 服务层 → Repository 层 → 数据库**，禁止跨层调用。

## 字段名规范 / Field Name Convention

**所有 SQL 查询中的中文字段名必须使用 `backend/database/schema/column_names.py` 中定义的常量。**

禁止在 SQL 字符串中直接使用中文字段名字面量。详见 `.claude/rules/00_global.md`。

## 开发规则 / Development Rules

`.claude/rules/` 目录包含强制执行的开发规则：

| 规则文件 | 用途 |
|---------|------|
| `00_global.md` | 全局编码规范（UTF-8、字段名常量、外部表访问） |
| `10_cc_architect.md` | 架构师协议（架构设计、Schema 变更） |
| `20_codex_backend.md` | Codex 后端实现规则 |
| `30_gemini_frontend.md` | Gemini 前端设计协议 |
| `40_debug_8d.md` | 8D 问题解决协议 |
| `50_hotfix_sop.md` | 热修复 SOP |
| `60_ADP-Protocol.md` | ADP 开发协议（四阶段流程） |
| `70_prompt_task_convention.md` | 提示词任务编号约定 |

## 文档真相来源 / Documentation Source of Truth

`docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/API_SPEC.md`、`docs/DB_SCHEMA.md`、`docs/RBAC_DESIGN.md`、`docs/RBAC_PERMISSION_MATRIX.md` - 代码不得偏离这些文档。

## 提示任务工作流 / Prompt Task Workflow

1. 待处理: `promptsRec/active/*.md`
2. 运行中: `promptsRec/active/*.lock`
3. 已完成: `promptsRec/archive/✅_<5位序列>_<原始名称>.md`

完成后:
- 归档提示: `✅_<序列>_<原始名称>.md`
- 编写运行报告: `logs/prompt_task_runs/run_YYYYMMDD_<序号>_<任务名>.md`
- 如有代码修正，编写纠正日志: `logs/codex_rectification/`

详见 `docs/PROMPT_TASK_CONVENTION.md`。

## 提交风格 / Commit Style

使用简短祈使句: `fix keeper confirmation flow`、`feat: add order submission API`

## 安全 / Security

- 永不提交凭据，使用 `.env` (不提交) 以 `.env.example` 为模板
- 外保持 `FLASK_DEBUG=False`
- 测试前验证数据库连接

## 测试运行器 / Test Runners

E2E 测试框架位于 `test_runner/`：

```powershell
# API E2E 测试（直接调用后端 API）
python test_runner/api_e2e.py

# Playwright E2E 测试（模拟浏览器）
python test_runner/playwright_e2e.py

# 端口要求：前端 8150，后端 8151 必须已启动
```

测试运行器在执行前会检查端口可用性，服务未启动时立即退出。

感知模块位于 `.skills/human-e2e-tester/sensing/`，提供页面状态观察和工作流检测。

## 测试 / Testing

- 后端: 启动 Flask 测试受影响路由
- 前端: `npm run build` + 手动验证
- 测试位置: `tests/test_*.py`
