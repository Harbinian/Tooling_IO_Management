# AI Review: Codebase Overview

## Project Summary

**Project Name**: 工装出入库管理系统 (Tooling IO Management System)

**Type**: Full-stack web application

**Core Functionality**: 工装/设备出入库订单管理系统，具有基于角色的工作流和飞书通知集成

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask REST API + SQL Server (pyodbc) |
| Frontend | Vue 3 + Element Plus + Vite |
| Database | SQL Server |
| Notifications | Feishu Webhook |
| Configuration | Environment-based via config/settings.py |

## Architecture Layers

```
web_server.py                    → Flask routes and HTTP handling
backend/routes/*.py              → API endpoints
backend/services/*.py           → Business logic
backend/database/repositories/*.py → Data access layer
backend/database/core/*.py      → Database core (connection pool, executor)
backend/database/schema/*.py     → Schema management
database.py                     → SQL Server direct access
config/settings.py              → Centralized configuration
```

## Frontend Structure

```
frontend/src/
├── pages/               # Page components
│   ├── auth/           → LoginPage
│   ├── dashboard/      → DashboardOverview
│   ├── tool-io/        → OrderList, OrderDetail, OrderCreate, KeeperProcess
│   └── admin/          → UserAdminPage
├── components/         → Reusable UI components
│   ├── tool-io/        → ToolSearchDialog, ToolSelectionTable, LogTimeline
├── api/               → API wrappers
├── store/             → Pinia state management
└── router/            → Vue Router configuration
```

## Key Modules

### Backend Services

| Module | Purpose |
|--------|---------|
| tool_io_service.py | Core order workflow logic |
| rbac_service.py | Role-based access control |
| auth_service.py | Authentication |
| notification_service.py | Feishu notifications |
| admin_user_service.py | User management |
| org_service.py | Organization management |
| rbac_data_scope_service.py | Data scope filtering |
| feedback_service.py | User feedback handling |
| transport_issue_service.py | Transport issue handling |

### Backend Routes

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| auth_bp | /api/auth | Login, session |
| order_bp | /api/tool-io-orders | Order CRUD and workflow |
| tool_bp | /api/tools | Tool search |
| dashboard_bp | /api/dashboard | Dashboard metrics |
| org_bp | /api/orgs | Organization tree |
| admin_user_bp | /api/admin | User management |
| feedback_bp | /api/feedback | User feedback |
| system_bp | /api/system | Health, diagnostics |

## Database Tables

Created on first API call via `ensure_tool_io_tables()`:

- `tool_io_order` - Order master table
- `tool_io_order_item` - Order line items
- `tool_io_operation_log` - Operation audit trail
- `tool_io_notification` - Notification history
- `tool_io_location` - Tool locations
- `tool_io_transport_issue` - Transport issue records
- `tool_status_change_history` - Tool status change history
- `tool_io_feedback` - User feedback
- `tool_io_feedback_reply` - Feedback replies
- RBAC tables: `sys_org`, `sys_user`, `sys_role`, `sys_permission`, etc.

## Workflow States

**出库 (Outbound)**: 草稿 → 已提交 → 保管员已确认 → 运输通知 → 运输中 → 待最终确认 → 已完成

**入库 (Inbound)**: 草稿 → 已提交 → 保管员已确认 → 运输通知 → 运输中 → 待最终确认 → 已完成

## RBAC Roles

| Role | Description |
|------|-------------|
| team_leader | Create orders, final confirm outbound |
| keeper | Confirm items, reject orders, final confirm inbound |
| planner | Create and submit orders |
| production_prep | Execute transport operations |
| auditor | View logs and reports |
| sys_admin | Full system access |

## API Base URL

- Backend: `http://localhost:8151`
- Frontend: `http://localhost:8150`

## Entry Points

- Backend: `python web_server.py`
- Frontend: `cd frontend && npm run dev`

## Development Commands

```powershell
# Backend syntax check
python -m py_compile web_server.py database.py backend/services/tool_io_service.py config/settings.py

# Frontend build
cd frontend && npm run build
```
