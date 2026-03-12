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
web_server.py           → Flask routes and HTTP handling
backend/services/*.py    → Business logic wrappers
backend/routes/*.py      → API endpoints
backend/database/*.py    → Database queries
config/settings.py       → Centralized configuration
utils/feishu_api.py     → Feishu webhook notifications
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
│   ├── ui/            → Input, Button, Card, Select, Tabs
│   └── tool-io/        → ToolSearchDialog, ToolSelectionTable, LogTimeline
├── api/               → API wrappers
├── store/             → Pinia state management
├── directives/        → vDebugId directive
├── debug/             → debugIds.js
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
| tool_location_service.py | Tool location tracking |
| audit_log_service.py | Operation audit logging |

### Backend Routes

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| auth_bp | /api/auth | Login, session |
| order_bp | /api/tool-io-orders | Order CRUD and workflow |
| tool_bp | /api/tools | Tool search |
| dashboard_bp | /api/dashboard | Dashboard metrics |
| org_bp | /api/orgs | Organization tree |
| admin_user_bp | /api/admin | User management |
| system_bp | /api/system | Health, diagnostics |

## Database Tables

Created on first API call via `ensure_tool_io_tables()`:

- `工装出入库单_主表` - Order master table
- `工装出入库单_明细` - Order line items
- `工装出入库单_操作日志` - Operation audit trail
- `工装出入库单_通知记录` - Notification history
- RBAC tables: `RBAC_角色`, `RBAC_权限`, `RBAC_角色权限`

## Workflow States

**出库 (Outbound)**: 草稿 → 已提交 → 保管员已确认 → 运输中 → 班组长最终确认 → 已完成

**入库 (Inbound)**: 草稿 → 已提交 → 保管员已确认 → 运输中 → 保管员最终确认 → 已完成

## RBAC Roles

| Role | Permissions |
|------|-------------|
| team_leader | Create orders, final confirm outbound |
| keeper | Confirm items, reject orders, final confirm inbound |
| admin | Full access |

## API Base URL

- Backend: `http://localhost:5000`
- Frontend: `http://localhost:5173`

## Entry Points

- Backend: `python web_server.py`
- Frontend: `cd frontend && npm run dev`

## Development Commands

```powershell
# Backend syntax check
python -m py_compile web_server.py database.py

# Frontend build
cd frontend && npm run build
```
