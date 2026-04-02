# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述 / Project Overview

工装出入库管理系统 (Tooling IO Management System) - 基于 Flask + Vue.js 的工装/设备出入库订单管理系统，具有基于角色的工作流和飞书 (Feishu) 通知集成。

Backend: Flask REST API + SQL Server (pyodbc). Frontend: Vue 3 + Element Plus + Vite. Configuration: Environment-based via config/settings.py. Notifications: Feishu webhook integration.

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

## 关键命令 / Key Commands

```powershell
# 后端语法检查 / Backend syntax check
python -m py_compile web_server.py database.py backend/services/tool_io_service.py config/settings.py

# 前端构建 / Frontend build
cd frontend && npm run build

# API E2E 测试（直接调用后端 API）
python test_runner/api_e2e.py

# Playwright E2E 测试（模拟浏览器）
python test_runner/playwright_e2e.py
```

测试运行器在执行前会检查端口可用性，服务未启动时立即退出。

## 架构 / Architecture

### 分层结构

```
web_server.py                              → Flask 路由和 HTTP 处理
backend/routes/*.py                        → API 路由层
backend/services/*.py                      → 业务逻辑层
backend/database/repositories/*.py         → 数据访问层
backend/database/core/*.py                → 数据库核心 (connection_pool, executor)
backend/database/schema/*.py              → Schema 管理 (schema_manager.py, column_names.py)
config/settings.py                         → 集中配置
utils/feishu_api.py                        → 飞书 Webhook 通知
```

**路由 → 服务层 → Repository 层 → 数据库**，禁止跨层调用。

### 后端路由 / Backend Routes

| 文件 | 用途 |
|------|------|
| `order_routes.py` | 工装出入库订单 API |
| `tool_routes.py` | 工装搜索 API |
| `auth_routes.py` | 认证 API |
| `mpl_routes.py` | MPL (工装可拆卸件清单) API |
| `system_config_routes.py` | 系统配置 API |
| `admin_user_routes.py` | 管理员用户 API |
| `dashboard_routes.py` | 仪表盘 API |
| `org_routes.py` | 组织架构 API |
| `feedback_routes.py` | 反馈 API |
| `page_routes.py` | 页面渲染 |
| `system_routes.py` | 系统 API |

### 核心服务 / Core Services

| 服务 | 用途 |
|------|------|
| `tool_io_service.py` | 工装出入库核心业务逻辑 |
| `order_workflow_service.py` | 订单状态机和工作流 |
| `mpl_service.py` | MPL (可拆卸件清单) 管理 |
| `rbac_service.py` | 角色权限控制 |
| `notification_service.py` | 通知服务 |
| `feishu_notification_adapter.py` | 飞书通知适配器 |
| `transport_issue_service.py` | 运输异常处理（支持 Base64 图片） |
| `feature_flag_service.py` | 功能开关管理 |

### 数据访问层 / Repository Layer

| Repository | 用途 |
|------------|------|
| `order_repository.py` | 订单数据访问 |
| `tool_repository.py` | 工装数据访问 |
| `mpl_repository.py` | MPL 数据访问 |
| `system_config_repository.py` | 系统配置数据访问 |
| `transport_issue_repository.py` | 运输异常数据访问 |

## 数据库 / Database

表通过首次 API 调用时 `ensure_tool_io_tables()` 自动创建。核心表:

- `tool_io_order` - 订单主表
- `tool_io_order_item` - 订单明细项
- `tool_io_operation_log` - 操作审计跟踪
- `tool_io_notification` - 通知发送历史
- `tool_io_location` - 工装位置信息
- `tool_io_transport_issue` - 运输异常记录
- `tool_io_mpl` - 工装可拆卸件清单

RBAC 表: `sys_org`, `sys_user`, `sys_role`, `sys_permission`, `tool_io_order_no_sequence`

> **注意**: `Tooling_ID_Main` 是外部系统表，禁止修改其 Schema，必须通过 `column_names.py` 中的常量访问。

## 前端结构 / Frontend Structure

```
frontend/src/
├── pages/          # 页面组件
│   ├── tool-io/    # 订单相关 (OrderList, OrderDetail, OrderCreate, KeeperProcess)
│   ├── admin/      # 管理页面 (UserAdmin, FeedbackAdmin)
│   ├── dashboard/  # 仪表盘
│   ├── auth/       # 登录
│   └── settings/   # 设置
├── components/    # 可复用 UI 组件
├── api/            # API 包装器 (统一封装所有 /api/* 调用)
├── store/          # 共享状态 (Pinia)
└── router/         # 路由配置
```

**API 层 (`api/`) 是所有前端 HTTP 通信的单一入口**，禁止在组件内直接调用 `axios`。

### 前端 API 模块

| 文件 | 用途 |
|------|------|
| `orders.js` | 订单 API |
| `tools.js` | 工装搜索 API |
| `mpl.js` | MPL API |
| `systemConfig.js` | 系统配置 API |
| `auth.js` | 认证 API |
| `dashboard.js` | 仪表盘 API |
| `orgs.js` | 组织架构 API |
| `adminUsers.js` | 用户管理 API |
| `feedback.js` | 反馈 API |
| `client.js` | 通用客户端封装 |

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
| `GET /api/mpl/<tool_code>` | 获取 MPL 清单 |
| `POST /api/admin/system-config/*` | 系统配置管理 |
| `POST /api/tool-io-orders/<order_no>/notify-transport` | 运输通知 |
| `GET /api/health` | 健康检查 |

## 工作流 / Workflow

**出库**: 草稿 → 已提交 → 保管员已确认 → (运输) → 班组长最终确认 → 已完成

**入库**: 草稿 → 已提交 → 保管员已确认 → (运输) → 保管员最终确认 → 已完成

## 角色 / Roles

| 角色 | 说明 |
|------|------|
| `team_leader` (班组长) | 创建订单、出库最终确认 |
| `keeper` (保管员) | 确认明细、拒绝订单、入库最终确认 |
| `admin` | 完全访问权限 |

## 编码约定 / Coding Conventions

- 代码使用英文，注释允许中英双语
- 4空格缩进，`snake_case` 函数/变量，`PascalCase` 类
- 文件操作使用 `encoding='utf-8'`
- 配置集中在 `config/settings.py`，勿散布 `os.getenv()`
- 无占位符代码 - 所有代码必须完整可执行
- **所有 SQL 查询中的中文字段名必须使用 `backend/database/schema/column_names.py` 中定义的常量**

## 开发规则 / Development Rules

`.claude/rules/` 目录包含强制执行的开发规则：

| 规则文件 | 用途 |
|---------|------|
| `00_core.md` | 核心规则（编码、字段名常量、命名、Git、数据库表范围） |
| `01_workflow.md` | ADP 四阶段开发流程 |
| `02_debug.md` | 8D 问题解决协议 |
| `03_hotfix.md` | 热修复 SOP |
| `04_frontend.md` | 前端开发规范 |
| `05_task_convention.md` | 提示词任务编号约定 |
| `06_testing.md` | 测试任务规范 |

## 文档真相来源 / Documentation Source of Truth

`docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/API_SPEC.md`、`docs/DB_SCHEMA.md`、`docs/RBAC_DESIGN.md`、`docs/RBAC_PERMISSION_MATRIX.md` - 代码不得偏离这些文档。

## 提示任务工作流 / Prompt Task Workflow

```
promptsRec/
├── active/          # 待处理任务: <5位编号>_<描述>.md
│   └── *.lock      # 运行中任务锁文件
└── archive/         # 已完成: ✅_<执行顺序号>_<类型编号>_<描述>_done.md
```

| 类型编号范围 | 类型 |
|-------------|------|
| `00001-09999` | 功能任务 |
| `10101-19999` | Bug修复 |
| `20101-29999` | 重构 |
| `30101-39999` | 测试 |

详见 `docs/PROMPT_TASK_CONVENTION.md`。

## 提交风格 / Commit Style

使用简短祈使句: `fix keeper confirmation flow`、`feat: add order submission API`

## 安全 / Security

- 永不提交凭据，使用 `.env` (不提交) 以 `.env.example` 为模板
- 外保持 `FLASK_DEBUG=False`
- 测试前验证数据库连接

## 照片存储 / Photo Storage

运输异常报告支持图片附件，采用 Base64 内嵌存储：
- 前端: `ReportTransportIssueDialog.vue` 中 el-upload 设置 `:auto-upload="false"`
- 后端: `transport_issue_service.py` 接收 `image_urls` 参数
- 限制: 单张图片 Base64 不超过 2MB

## 日志目录 / Logs

```
logs/
├── codex_rectification/     # Codex 纠正日志 (Bug 修复后记录)
└── prompt_task_runs/        # 提示词任务执行报告
```

## 调试和问题解决 / Debugging & Problem Solving

| 问题类型 | 规则文件 |
|---------|---------|
| Bug/回归问题 | `.claude/rules/02_debug.md` (8D 问题解决) |
| 数据/Schema 问题 | `.claude/rules/01_workflow.md` (ADP 四阶段) |
| 热修复 | `.claude/rules/03_hotfix.md` |
| 后端实现 | `.claude/rules/00_core.md` |
| 前端实现 | `.claude/rules/04_frontend.md` |
