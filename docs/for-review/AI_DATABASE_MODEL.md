# AI Review: Database Model

## Overview

- **Database**: SQL Server (via pyodbc)
- **Configuration**: `config/settings.py`
- **Tables**: Auto-created on first API call via `ensure_tool_io_tables()`

## Core Tables

### 工装出入库单_主表 (Order Master)

| Column | Type | Description |
|--------|------|-------------|
| 单据编号 | NVARCHAR | Order number (primary key) |
| 单据类型 | NVARCHAR | Order type (出库/入库) |
| 申请部门 | NVARCHAR | Requesting department |
| 申请人 | NVARCHAR | Applicant user ID |
| 申请时间 | DATETIME | Application timestamp |
| 单据状态 | NVARCHAR | Order status |
| 备注 | NVARCHAR | Notes |
| 创建时间 | DATETIME | Record creation time |
| 更新时间 | DATETIME | Last update time |

### 工装出入库单_明细 (Order Items)

| Column | Type | Description |
|--------|------|-------------|
| 明细ID | INT | Line item ID (primary key) |
| 单据编号 | NVARCHAR | Order number (foreign key) |
| 工装编号 | NVARCHAR | Tool code |
| 工装名称 | NVARCHAR | Tool name |
| 数量 | INT | Quantity |
| 明细状态 | NVARCHAR | Item status |
| 库位 | NVARCHAR | Storage location |
| 备注 | NVARCHAR | Notes |

### 工装出入库单_操作日志 (Operation Log)

| Column | Type | Description |
|--------|------|-------------|
| 日志ID | INT | Log ID (primary key) |
| 单据编号 | NVARCHAR | Order number |
| 操作类型 | NVARCHAR | Operation type |
| 操作人 | NVARCHAR | Operator user ID |
| 操作时间 | DATETIME | Operation timestamp |
| 备注 | NVARCHAR | Notes |

### 工装出入库单_通知记录 (Notification Record)

| Column | Type | Description |
|--------|------|-------------|
| 通知ID | INT | Notification ID (primary key) |
| 单据编号 | NVARCHAR | Order number |
| 通知类型 | NVARCHAR | Notification type |
| 通知渠道 | NVARCHAR | Channel (feishu/internal) |
| 接收人 | NVARCHAR | Recipient |
| 状态 | NVARCHAR | Status (pending/sent/failed) |
| 发送时间 | DATETIME | Send timestamp |

## RBAC Tables

### RBAC_角色 (Roles)

| Column | Type | Description |
|--------|------|-------------|
| 角色ID | NVARCHAR | Role ID (primary key) |
| 角色名称 | NVARCHAR | Role name |
| 角色描述 | NVARCHAR | Description |
| 创建时间 | DATETIME | Creation timestamp |

### RBAC_权限 (Permissions)

| Column | Type | Description |
|--------|------|-------------|
| 权限ID | NVARCHAR | Permission ID (primary key) |
| 权限名称 | NVARCHAR | Permission name |
| 所属模块 | NVARCHAR | Module |
| 权限代码 | NVARCHAR | Permission code |

### RBAC_角色权限 (Role-Permission)

| Column | Type | Description |
|--------|------|-------------|
| 角色ID | NVARCHAR | Role ID |
| 权限ID | NVARCHAR | Permission ID |

### RBAC_用户角色 (User-Role)

| Column | Type | Description |
|--------|------|-------------|
| 用户ID | NVARCHAR | User ID |
| 角色ID | NVARCHAR | Role ID |
| 组织ID | NVARCHAR | Organization ID |

## Query Files

| File | Purpose |
|------|---------|
| database.py | Core database operations |
| backend/database/tool_io_queries.py | Order-specific queries |
| backend/database/core.py | Database manager |
| backend/database/acceptance_queries.py | Acceptance test queries |
| backend/database/monitor_queries.py | Monitoring queries |

## Key Query Patterns

- Connection pool management via pyodbc
- Parameterized queries for security
- Organization-scope filtering via RBAC data scope

## Stage 115 Update

- `工装出入库单_明细` now includes nullable line-item confirmation fields for `确认人`, `确认时间`, and `驳回原因`.
- `确认人` stores the keeper/operator user ID that confirmed the line item.
- `驳回原因` is populated for rejected line items and remains null for approved ones.
