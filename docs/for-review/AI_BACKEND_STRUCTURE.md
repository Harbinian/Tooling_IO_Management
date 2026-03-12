# AI Review: Backend Structure

## Entry Point

**File**: `web_server.py`

- Flask application factory
- Blueprint registration
- Settings import from `config/settings.py`

## Directory Structure

```
backend/
├── routes/
│   ├── admin_user_routes.py   # User management API
│   ├── auth_routes.py         # Login, session
│   ├── common.py              # Request identity hook
│   ├── dashboard_routes.py    # Dashboard metrics
│   ├── order_routes.py        # Order CRUD + workflow
│   ├── org_routes.py         # Organization API
│   ├── page_routes.py         # Server-side page routes
│   ├── system_routes.py      # Health, diagnostics
│   └── tool_routes.py        # Tool search
├── services/
│   ├── admin_user_service.py    # User CRUD + role assignment
│   ├── audit_log_service.py     # Operation logging
│   ├── auth_service.py          # Authentication logic
│   ├── feishu_notification_adapter.py  # Feishu message formatting
│   ├── notification_service.py  # Notification delivery
│   ├── org_service.py           # Organization management
│   ├── rbac_data_scope_service.py  # Data scope filtering
│   ├── rbac_service.py          # Role-based access control
│   ├── tool_io_runtime.py       # Runtime order processing
│   ├── tool_io_service.py       # Core order workflow
│   └── tool_location_service.py  # Tool location tracking
└── database/
    ├── acceptance_queries.py  # Acceptance test queries
    ├── core.py               # Database manager
    ├── monitor_queries.py    # Monitoring queries
    └── tool_io_queries.py   # Order-specific queries
```

## Key Service Files

### tool_io_service.py

**Purpose**: Core business logic for 工装出入库 orders

**Key Functions**:

| Function | Purpose |
|----------|---------|
| create_order() | Create new order |
| list_orders() | Query orders with filters |
| get_order_detail() | Get order by order_no |
| submit_order() | Submit order for approval |
| keeper_confirm() | Keeper approves items |
| final_confirm() | Final confirmation (team_leader/keeper) |
| reject_order() | Reject order |
| cancel_order() | Cancel order |
| notify_transport() | Send transport notification |
| notify_keeper() | Send keeper notification |
| get_dashboard_stats() | Dashboard metrics |

### rbac_service.py

**Purpose**: Role-based access control

**Key Functions**:

| Function | Purpose |
|----------|---------|
| ensure_rbac_tables() | Create RBAC tables |
| load_user_roles() | Get user's roles |
| load_permissions_for_role_ids() | Get permissions for roles |
| resolve_user_permissions() | Get all user permissions |
| has_permission() | Check if user has permission |

### auth_service.py

**Purpose**: Authentication logic

### notification_service.py

**Purpose**: Feishu webhook notifications

## API Routes

### Order Routes (order_bp)

```
GET    /api/tool-io-orders                  # List orders
POST   /api/tool-io-orders                  # Create order
GET    /api/tool-io-orders/<order_no>       # Get order detail
POST   /api/tool-io-orders/<order_no>/submit
POST   /api/tool-io-orders/<order_no>/keeper-confirm
POST   /api/tool-io-orders/<order_no>/final-confirm
GET    /api/tool-io-orders/<order_no>/final-confirm-availability
POST   /api/tool-io-orders/<order_no>/assign-transport
POST   /api/tool-io-orders/<order_no>/transport-start
POST   /api/tool-io-orders/<order_no>/transport-complete
POST   /api/tool-io-orders/<order_no>/reject
POST   /api/tool-io-orders/<order_no>/cancel
GET    /api/tool-io-orders/<order_no>/logs
GET    /api/tool-io-orders/<order_no>/notification-records
POST   /api/tool-io-orders/<order_no>/notify-transport
POST   /api/tool-io-orders/<order_no>/notify-keeper
GET    /api/tool-io-orders/pending-keeper
GET    /api/tool-io-orders/<order_no>/generate-keeper-text
GET    /api/tool-io-orders/<order_no>/generate-transport-text
```

### Auth Routes (auth_bp)

```
POST   /api/auth/login
GET    /api/auth/me
```

### Tool Routes (tool_bp)

```
GET    /api/tools/search
POST   /api/tools/batch-query
```

### Dashboard Routes (dashboard_bp)

```
GET    /api/dashboard/metrics
```

### Org Routes (org_bp)

```
GET    /api/orgs
GET    /api/orgs/tree
GET    /api/orgs/<org_id>
POST   /api/orgs/<org_id>
PUT    /api/orgs/<org_id>
```

### Admin User Routes (admin_user_bp)

```
GET    /api/admin/roles
GET    /api/admin/users
GET    /api/admin/users/<user_id>
POST   /api/admin/users
PUT    /api/admin/users/<user_id>
PUT    /api/admin/users/<user_id>/roles
PUT    /api/admin/users/<user_id>/status
PUT    /api/admin/users/<user_id>/password-reset
```

### System Routes (system_bp)

```
GET    /api/health
GET    /api/system/health
GET    /api/system/diagnostics/recent-errors
GET    /api/system/diagnostics/notification-failures
GET    /api/db/test
```

## Database Connection

**File**: `database.py`

- Uses pyodbc for SQL Server connection
- Connection pool management
- Connection string from config/settings.py
