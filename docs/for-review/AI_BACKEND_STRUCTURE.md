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
│   ├── dashboard_routes.py    # Dashboard metrics
│   ├── feedback_routes.py     # User feedback API
│   ├── order_routes.py        # Order CRUD + workflow
│   ├── org_routes.py         # Organization API
│   ├── page_routes.py         # Server-side page routes
│   ├── system_routes.py      # Health, diagnostics
│   └── tool_routes.py        # Tool search
├── services/
│   ├── admin_user_service.py    # User CRUD + role assignment
│   ├── auth_service.py          # Authentication logic
│   ├── feedback_service.py       # User feedback handling
│   ├── feishu_notification_adapter.py  # Feishu message formatting
│   ├── notification_service.py    # Notification delivery
│   ├── org_service.py           # Organization management
│   ├── rbac_data_scope_service.py  # Data scope filtering
│   ├── rbac_service.py          # Role-based access control
│   ├── tool_io_service.py       # Core order workflow
│   ├── tool_location_service.py   # Tool location tracking
│   └── transport_issue_service.py # Transport issue handling
└── database/
    ├── core/
    │   ├── database_manager.py   # Database manager (connection pool)
    │   └── executor.py          # SQL executor
    ├── repositories/
    │   ├── order_repository.py  # Order data access
    │   └── tool_repository.py  # Tool data access
    ├── schema/
    │   ├── column_names.py     # Column name constants
    │   └── schema_manager.py   # Schema management
    └── utils/
        └── sql_utils.py        # SQL utilities
```

## Key Service Files

### tool_io_service.py

**Purpose**: Core business logic for 工装出入库 orders

### rbac_service.py

**Purpose**: Role-based access control

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
DELETE /api/tool-io-orders/<order_no>        # Delete draft order
GET    /api/tool-io-orders/<order_no>/logs
GET    /api/tool-io-orders/<order_no>/notification-records
POST   /api/tool-io-orders/<order_no>/notify-transport
POST   /api/tool-io-orders/<order_no>/notify-keeper
GET    /api/tool-io-orders/<order_no>/generate-keeper-text
GET    /api/tool-io-orders/<order_no>/generate-transport-text
GET    /api/tool-io-orders/<order_no>/transport-issues
POST   /api/tool-io-orders/<order_no>/report-transport-issue
POST   /api/tool-io-orders/<order_no>/resolve-transport-issue
GET    /api/tool-io-orders/pending-keeper
GET    /api/tool-io-orders/pre-transport
PATCH  /api/tools/batch-status
GET    /api/tools/status-history/<tool_code>
```

### Auth Routes (auth_bp)

```
POST   /api/auth/login
GET    /api/auth/me
POST   /api/user/change-password
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
POST   /api/orgs
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

### Feedback Routes (feedback_bp)

```
GET    /api/feedback
POST   /api/feedback
DELETE /api/feedback/<id>
GET    /api/feedback/all
PUT    /api/feedback/<id>/status
POST   /api/feedback/<id>/reply
GET    /api/feedback/<id>/replies
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

**File**: `database.py` and `backend/database/core/database_manager.py`

- Uses pyodbc for SQL Server connection
- Connection pool management
- Connection string from config/settings.py

## Column Name Constants

**File**: `backend/database/schema/column_names.py`

All SQL queries should use column name constants from this file:

```python
from backend.database.schema.column_names import ORDER_COLUMNS, ITEM_COLUMNS

sql = f"SELECT {ORDER_COLUMNS['order_no']} FROM tool_io_order"
```
