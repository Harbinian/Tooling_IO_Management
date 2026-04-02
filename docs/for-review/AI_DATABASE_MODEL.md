# AI Review: Database Model

## Overview

- **Database**: SQL Server (via pyodbc)
- **Configuration**: `config/settings.py`
- **Tables**: Auto-created on first API call via `ensure_tool_io_tables()`

## Core Tables

### tool_io_order (Order Master)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key, auto-increment |
| order_no | VARCHAR(64) | Order number (unique) |
| order_type | VARCHAR(16) | outbound/inbound |
| order_status | VARCHAR(32) | Order status |
| initiator_id | VARCHAR(64) | Applicant user ID |
| initiator_name | VARCHAR(64) | Applicant name |
| initiator_role | VARCHAR(32) | Applicant role |
| department | VARCHAR(64) | Department |
| project_code | VARCHAR(64) | Project code |
| usage_purpose | VARCHAR(255) | Usage purpose |
| planned_use_time | DATETIME | Planned use time |
| planned_return_time | DATETIME | Planned return time |
| target_location_id | BIGINT | Target location ID |
| target_location_text | VARCHAR(255) | Target location |
| keeper_id | VARCHAR(64) | Keeper ID |
| keeper_name | VARCHAR(64) | Keeper name |
| transport_type | VARCHAR(32) | Transport type |
| transport_operator_id | VARCHAR(64) | Transport operator ID |
| transport_operator_name | VARCHAR(64) | Transport operator name |
| keeper_confirm_time | DATETIME | Keeper confirmation time |
| tool_quantity | INT | Tool quantity |
| confirmed_count | INT | Confirmed count |
| final_confirm_by | VARCHAR(64) | Final confirmer |
| final_confirm_time | DATETIME | Final confirmation time |
| cancel_reason | VARCHAR(500) | Cancel reason |
| reject_reason | VARCHAR(500) | Reject reason |
| remark | VARCHAR(500) | Notes |
| org_id | VARCHAR(64) | Organization ID |
| created_at | DATETIME | Creation time |
| updated_at | DATETIME | Update time |
| created_by | VARCHAR(64) | Creator |
| updated_by | VARCHAR(64) | Updater |
| is_deleted | TINYINT | Soft delete flag |

### tool_io_order_item (Order Items)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key, auto-increment |
| order_no | VARCHAR(64) | Order number (FK) |
| tool_id | BIGINT | Tool ID |
| tool_code | VARCHAR(64) | Tool code |
| tool_name | VARCHAR(255) | Tool name |
| drawing_no | VARCHAR(255) | Drawing number |
| spec_model | VARCHAR(255) | Specification model |
| apply_qty | DECIMAL(18,2) | Applied quantity |
| confirmed_qty | DECIMAL(18,2) | Confirmed quantity |
| item_status | VARCHAR(32) | Item status |
| tool_snapshot_status | VARCHAR(255) | Tool snapshot status |
| tool_snapshot_location_text | VARCHAR(255) | Tool snapshot location |
| tool_snapshot_location_id | BIGINT | Tool snapshot location ID |
| confirm_by | VARCHAR(255) | Confirmer |
| confirm_by_id | BIGINT | Confirmer ID |
| confirm_by_name | VARCHAR(64) | Confirmer name |
| confirm_time | DATETIME | Confirmation time |
| reject_reason | VARCHAR(500) | Reject reason |
| io_complete_time | DATETIME | IO complete time |
| sort_order | INT | Sort order |
| created_at | DATETIME | Creation time |
| updated_at | DATETIME | Update time |

### tool_io_operation_log (Operation Log)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key, auto-increment |
| order_no | VARCHAR(64) | Order number |
| item_id | BIGINT | Item ID |
| operation_type | VARCHAR(64) | Operation type |
| operator_id | VARCHAR(64) | Operator user ID |
| operator_name | VARCHAR(64) | Operator name |
| operator_role | VARCHAR(64) | Operator role |
| from_status | VARCHAR(64) | From status |
| to_status | VARCHAR(64) | To status |
| operation_content | TEXT | Operation content |
| operation_time | DATETIME | Operation time |

### tool_io_notification (Notification Record)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key, auto-increment |
| order_no | VARCHAR(64) | Order number |
| notify_type | VARCHAR(64) | Notification type |
| notify_channel | VARCHAR(64) | Channel (feishu/internal) |
| receiver | VARCHAR(255) | Recipient |
| notify_title | VARCHAR(255) | Notification title |
| notify_content | TEXT | Notification content |
| copy_text | TEXT | Copy text |
| send_status | VARCHAR(32) | Status (pending/success/failed) |
| send_time | DATETIME | Send time |
| send_result | TEXT | Send result |
| retry_count | INT | Retry count |
| created_at | DATETIME | Creation time |

## RBAC Tables

### sys_role (Roles)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| role_id | NVARCHAR(64) | Role ID |
| role_code | NVARCHAR(50) | Role code |
| role_name | NVARCHAR(100) | Role name |
| role_type | NVARCHAR(20) | business/system |
| status | NVARCHAR(20) | Status |
| created_at | DATETIME2 | Creation time |

### sys_permission (Permissions)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| permission_code | NVARCHAR(100) | Permission code |
| permission_name | NVARCHAR(100) | Permission name |
| resource_name | NVARCHAR(50) | Resource name |
| action_name | NVARCHAR(50) | Action name |

### sys_user_role_rel (User-Role)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| user_id | NVARCHAR(64) | User ID |
| role_id | NVARCHAR(64) | Role ID |
| is_primary | BIT | Is primary role |
| status | NVARCHAR(20) | Status |

### sys_role_permission_rel (Role-Permission)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| role_id | NVARCHAR(64) | Role ID |
| permission_code | NVARCHAR(100) | Permission code |

### sys_org (Organizations)

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| org_id | NVARCHAR(64) | Organization ID |
| org_name | NVARCHAR(100) | Organization name |
| org_code | NVARCHAR(100) | Organization code |
| org_type | NVARCHAR(50) | Organization type |
| parent_org_id | NVARCHAR(64) | Parent organization |
| sort_no | INT | Sort order |
| status | NVARCHAR(20) | Status |

## Query Files

| File | Purpose |
|------|---------|
| database.py | Core database operations |
| backend/database/core/database_manager.py | Database manager (connection pool) |
| backend/database/repositories/order_repository.py | Order-specific queries |
| backend/database/repositories/tool_repository.py | Tool queries |
| backend/database/schema/column_names.py | Column name constants |

## Key Query Patterns

- Connection pool management via pyodbc
- Parameterized queries for security
- Organization-scope filtering via RBAC data scope
- All Chinese column names must use constants from `column_names.py`
