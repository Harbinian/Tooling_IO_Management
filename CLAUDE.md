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

服务端口: `http://localhost:5000` (后端), `http://localhost:5173` (前端)

## 关键 API 路由 / Key API Routes

| 端点 | 说明 |
|------|------|
| `GET /api/tool-io-orders` | 订单列表 (支持分页/过滤) |
| `POST /api/tool-io-orders` | 创建订单 |
| `GET /api/tool-io-orders/<order_no>` | 订单详情 |
| `POST /api/tool-io-orders/<order_no>/submit` | 提交订单 |
| `POST /api/tool-io-orders/<order_no>/confirm-keeper` | 保管员确认 |
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

- `工装出入库单_主表` - 订单主表
- `工装出入库单_明细` - 订单明细项
- `工装出入库单_操作日志` - 操作审计跟踪
- `工装出入库单_通知记录` - 通知历史

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
web_server.py           → Flask 路由和 HTTP 处理
backend/services/*.py    → 业务逻辑包装器
database.py             → SQL Server 直接访问 (连接池、查询)
config/settings.py      → 集中配置
utils/feishu_api.py     → 飞书 Webhook 通知
```

路由应使用服务层处理业务逻辑，而非直接调用 database.py。

## 文档真相来源 / Documentation Source of Truth

`docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/API_SPEC.md`、`docs/DB_SCHEMA.md`、`docs/RBAC_DESIGN.md` - 代码不得偏离这些文档。

## 提示任务工作流 / Prompt Task Workflow

1. 待处理: `promptsRec/*.md`
2. 运行中: `promptsRec/*.lock`
3. 已完成: `promptsRec/✅_<5位序列>_<原始名称>.md`

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

## 测试 / Testing

- 后端: 启动 Flask 测试受影响路由
- 前端: `npm run build` + 手动验证
- 测试位置: `tests/test_*.py`
