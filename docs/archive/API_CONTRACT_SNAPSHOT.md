# API Contract Snapshot

**Date:** 2026-03-13
**Version:** 1.0
**Purpose:** Freeze current API contract for regression baseline

---

## 1. API Inventory

| # | Endpoint | Method | Permission | Description |
|---|----------|--------|------------|-------------|
| 1 | `/api/auth/login` | POST | None | User login |
| 2 | `/api/auth/me` | GET | Required | Get current user info |
| 3 | `/api/tools/search` | GET | `tool:search` | Search tool inventory |
| 4 | `/api/tools/batch-query` | POST | `tool:view` | Batch query tools |
| 5 | `/api/tool-io-orders` | GET | `order:list` | List orders |
| 6 | `/api/tool-io-orders` | POST | `order:create` | Create order |
| 7 | `/api/tool-io-orders/<order_no>` | GET | `order:view` | Get order detail |
| 8 | `/api/tool-io-orders/<order_no>/submit` | POST | `order:submit` | Submit order |
| 9 | `/api/tool-io-orders/<order_no>/keeper-confirm` | POST | `order:keeper_confirm` | Keeper confirmation |
| 10 | `/api/tool-io-orders/<order_no>/final-confirm` | POST | `order:final_confirm` | Final confirmation |
| 11 | `/api/tool-io-orders/<order_no>/final-confirm-availability` | GET | `order:view` | Check final confirm availability |
| 12 | `/api/tool-io-orders/<order_no>/assign-transport` | POST | `order:keeper_confirm` | Assign transport operator |
| 13 | `/api/tool-io-orders/<order_no>/transport-start` | POST | `order:transport_execute` | Start transport |
| 14 | `/api/tool-io-orders/<order_no>/transport-complete` | POST | `order:transport_execute` | Complete transport |
| 15 | `/api/tool-io-orders/<order_no>/reject` | POST | `order:cancel` | Reject order |
| 16 | `/api/tool-io-orders/<order_no>/cancel` | POST | `order:cancel` | Cancel order |
| 17 | `/api/tool-io-orders/<order_no>/logs` | GET | `order:view` | Get order logs |
| 18 | `/api/tool-io-orders/<order_no>/notification-records` | GET | `notification:view` | Get notification records |
| 19 | `/api/notifications` | GET | `notification:view` | Get current user notifications |
| 20 | `/api/notifications/<notification_id>/read` | POST | `notification:view` | Mark notification as read |
| 21 | `/api/tool-io-orders/pending-keeper` | GET | `order:keeper_confirm` | Get pending keeper orders |
| 22 | `/api/tool-io-orders/<order_no>/generate-keeper-text` | GET | `notification:create` | Generate keeper notification text |
| 23 | `/api/tool-io-orders/<order_no>/generate-transport-text` | GET | `notification:create` | Generate transport notification text |
| 24 | `/api/tool-io-orders/<order_no>/notify-transport` | POST | `notification:send_feishu` | Send transport notification |
| 25 | `/api/tool-io-orders/<order_no>/notify-keeper` | POST | `notification:send_feishu` | Send keeper notification |
| 26 | `/api/orgs` | GET | `dashboard:view` | List organizations |
| 27 | `/api/orgs/tree` | GET | `dashboard:view` | Get org tree |
| 28 | `/api/orgs/<org_id>` | GET | `dashboard:view` | Get org detail |
| 29 | `/api/orgs` | POST | `admin:user_manage` | Create organization |
| 30 | `/api/orgs/<org_id>` | PUT | `admin:user_manage` | Update organization |
| 31 | `/api/health` | GET | None | Health check |
| 32 | `/api/db/test` | GET | `dashboard:view` | Database connection test |
| 33 | `/api/admin/roles` | GET | `admin:user_manage` | List assignable roles |
| 34 | `/api/admin/users` | GET | `admin:user_manage` | List users for account admin |
| 35 | `/api/admin/users/<user_id>` | GET | `admin:user_manage` | Get account detail |
| 36 | `/api/admin/users` | POST | `admin:user_manage` | Create account |
| 37 | `/api/admin/users/<user_id>` | PUT | `admin:user_manage` | Update account basic info |
| 38 | `/api/admin/users/<user_id>/roles` | PUT | `admin:user_manage` | Replace assigned roles |
| 39 | `/api/admin/users/<user_id>/status` | PUT | `admin:user_manage` | Enable or disable account |
| 40 | `/api/admin/users/<user_id>/password-reset` | PUT | `admin:user_manage` | Reset account password |

---

## 2. Request Contracts

### 2.1 Authentication

#### POST /api/auth/login
```json
{
  "login_name": "string (required)",
  "password": "string (required)"
}
```

#### GET /api/auth/me
- **Auth:** Required (session-based)
- **Response:** Returns current user object with roles and permissions

---

### 2.2 Tools

#### GET /api/tools/search
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | No | Search keyword |
| status | string | No | Tool status filter |
| location | string | No | Location filter |
| location_id | string | No | Location ID filter |
| page_no | int | No | Page number (default: 1) |
| page_size | int | No | Page size (default: 20) |

#### POST /api/tools/batch-query
```json
{
  "tool_codes": ["string"] (required, array)
}
```

---

### 2.3 Orders

#### GET /api/tool-io-orders
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| order_type | string | No | "outbound" or "inbound" |
| order_status | string | No | Status filter |
| initiator_id | string | No | Filter by initiator |
| keeper_id | string | No | Filter by keeper |
| keyword | string | No | Keyword search |
| date_from | string | No | Start date (YYYY-MM-DD) |
| date_to | string | No | End date (YYYY-MM-DD) |
| page_no | int | No | Page number (default: 1) |
| page_size | int | No | Page size (default: 20) |

#### POST /api/tool-io-orders
```json
{
  "order_type": "outbound|inbound (required)",
  "items": [
    {
      "tool_code": "string (required)",
      "quantity": "number (required)"
    }
  ],
  "remark": "string (optional)"
}
```

#### POST /api/tool-io-orders/<order_no>/submit
```json
{
  "remark": "string (optional)"
}
```

#### POST /api/tool-io-orders/<order_no>/keeper-confirm
```json
{
  "items": [
    {
      "tool_code": "string (required)",
      "quantity": "number (required)",
      "confirmed": "boolean (optional, default true)"
    }
  ],
  "remark": "string (optional)"
}
```

#### POST /api/tool-io-orders/<order_no>/final-confirm
```json
{
  "remark": "string (optional)"
}
```

#### POST /api/tool-io-orders/<order_no>/reject
```json
{
  "reject_reason": "string (required)"
}
```

#### POST /api/tool-io-orders/<order_no>/cancel
```json
{
  "cancel_reason": "string (optional)"
}
```

---

### 2.4 Organizations

#### GET /api/orgs
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| include_disabled | bool | No | Include disabled orgs (default: true) |

#### POST /api/orgs
```json
{
  "org_name": "string (required)",
  "org_code": "string (required)",
  "parent_org_id": "string (optional)",
  "enabled": "boolean (optional)"
}
```

### 2.5 Administrator Account Management

#### POST /api/admin/users
```json
{
  "login_name": "string (required)",
  "display_name": "string (required)",
  "employee_no": "string (required)",
  "default_org_id": "string (optional)",
  "role_ids": ["string"] ,
  "status": "active|disabled (optional)",
  "initial_password": "string (required)"
}
```

#### PUT /api/admin/users/<user_id>
```json
{
  "login_name": "string (required)",
  "display_name": "string (required)",
  "employee_no": "string (required)",
  "default_org_id": "string (optional)",
  "status": "active|disabled (required)"
}
```

#### PUT /api/admin/users/<user_id>/roles
```json
{
  "role_ids": ["string"] ,
  "org_id": "string (optional)"
}
```

#### PUT /api/admin/users/<user_id>/status
```json
{
  "status": "active|disabled (required)"
}
```

#### PUT /api/admin/users/<user_id>/password-reset
```json
{
  "new_password": "string (required)"
}
```

---

## 3. Response Contracts

### 3.1 Authentication

#### POST /api/auth/login - Success
```json
{
  "success": true,
  "user": {
    "user_id": "string",
    "login_name": "string",
    "display_name": "string",
    "roles": ["string"],
    "permissions": ["string"],
    "org_id": "string"
  },
  "token": "string (session-based)"
}
```

#### POST /api/auth/login - Error
```json
{
  "success": false,
  "error": "string"
}
```

#### GET /api/auth/me - Success
```json
{
  "success": true,
  "user": {
    "user_id": "string",
    "login_name": "string",
    "display_name": "string",
    "roles": ["string"],
    "permissions": ["string"],
    "org_id": "string"
  }
}
```

---

### 3.2 Orders

#### GET /api/tool-io-orders - Success
```json
{
  "success": true,
  "data": [
    {
      "order_no": "string",
      "order_type": "outbound|inbound",
      "order_status": "string",
      "initiator_id": "string",
      "initiator_name": "string",
      "keeper_id": "string",
      "keeper_name": "string",
      "org_id": "string",
      "org_name": "string",
      "created_at": "string (ISO datetime)",
      "updated_at": "string (ISO datetime)"
    }
  ],
  "pagination": {
    "page_no": 1,
    "page_size": 20,
    "total_count": 100
  }
}
```

#### GET /api/tool-io-orders/<order_no> - Success
```json
{
  "success": true,
  "data": {
    "order_no": "string",
    "order_type": "outbound|inbound",
    "order_status": "string",
    "initiator_id": "string",
    "initiator_name": "string",
    "keeper_id": "string",
    "keeper_name": "string",
    "org_id": "string",
    "org_name": "string",
    "created_at": "string",
    "updated_at": "string",
    "remark": "string",
    "items": [
      {
        "tool_code": "string",
        "tool_name": "string",
        "quantity": "number",
        "confirmed_quantity": "number",
        "location": "string"
      }
    ]
  }
}
```

---

### 3.3 Tools

#### GET /api/tools/search - Success
```json
{
  "success": true,
  "data": [
    {
      "tool_id": "string",
      "tool_code": "string",
      "tool_name": "string",
      "specification": "string",
      "current_location_text": "string",
      "status_text": "string",
      "available_quantity": "number"
    }
  ],
  "pagination": {
    "page_no": 1,
    "page_size": 20,
    "total_count": 100
  }
}
```

---

### 3.4 Organizations

#### GET /api/orgs - Success
```json
{
  "success": true,
  "data": [
    {
      "org_id": "string",
      "org_code": "string",
      "org_name": "string",
      "parent_org_id": "string|null",
      "enabled": true
    }
  ]
}
```

### 3.5 Administrator User Management

#### GET /api/admin/users - Success
```json
{
  "success": true,
  "data": [
    {
      "user_id": "string",
      "login_name": "string",
      "display_name": "string",
      "employee_no": "string",
      "status": "active|disabled",
      "default_org_id": "string|null",
      "default_org_name": "string|null",
      "roles": [
        {
          "role_id": "string",
          "role_code": "string",
          "role_name": "string",
          "org_id": "string|null",
          "org_name": "string|null",
          "is_primary": true
        }
      ]
    }
  ]
}
```

---

## 4. Frontend/Backend Contract Reconciliation

### 4.1 Identified Mismatches

| Issue | Severity | Description |
|-------|----------|-------------|
| Tool search field mapping | Low | Frontend normalizes multiple field names (`tool_id`, `current_location_text`, `status_text`) from various backend response formats |
| Order detail normalization | Low | Frontend applies `normalizeOrder` to handle variations in backend response |
| Notification records | Low | Backend returns different structures, frontend normalizes with `normalizeNotification` |

### 4.2 Field Expectations

**Frontend expects from order list:**
- `order_no`, `order_type`, `order_status`, `initiator_id`, `initiator_name`, `keeper_id`, `keeper_name`, `org_id`, `org_name`, `created_at`, `updated_at`

**Frontend expects from order detail:**
- All order list fields plus: `remark`, `items[]` (with `tool_code`, `tool_name`, `quantity`, `confirmed_quantity`, `location`)

**Frontend expects from tool search:**
- `tool_id`, `tool_code`, `tool_name`, `specification`, `current_location_text`, `status_text`, `available_quantity`

---

## 5. Error Response Patterns

### Standard Error Format
```json
{
  "success": false,
  "error": "string"
}
```

### Validation Error Format
```json
{
  "success": false,
  "error": "Validation failed: <details>",
  "code": "VALIDATION_ERROR"
}
```

### Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Server Error |

---

## 6. Permission Matrix

| Endpoint | Required Permission |
|----------|-------------------|
| `/api/auth/login` | None |
| `/api/auth/me` | Any authenticated |
| `/api/tools/search` | `tool:search` |
| `/api/tools/batch-query` | `tool:view` |
| `/api/tool-io-orders` (GET) | `order:list` |
| `/api/tool-io-orders` (POST) | `order:create` |
| `/api/tool-io-orders/<order_no>` | `order:view` |
| `/api/tool-io-orders/<order_no>/submit` | `order:submit` |
| `/api/tool-io-orders/<order_no>/keeper-confirm` | `order:keeper_confirm` |
| `/api/tool-io-orders/<order_no>/final-confirm` | `order:final_confirm` |
| `/api/tool-io-orders/<order_no>/assign-transport` | `order:keeper_confirm` |
| `/api/tool-io-orders/<order_no>/transport-start` | `order:transport_execute` |
| `/api/tool-io-orders/<order_no>/transport-complete` | `order:transport_execute` |
| `/api/tool-io-orders/<order_no>/reject` | `order:cancel` |
| `/api/tool-io-orders/<order_no>/cancel` | `order:cancel` |
| `/api/tool-io-orders/<order_no>/logs` | `order:view` |
| `/api/tool-io-orders/<order_no>/notification-records` | `notification:view` |
| `/api/notifications` | `notification:view` |
| `/api/notifications/<notification_id>/read` | `notification:view` |
| `/api/tool-io-orders/pending-keeper` | `order:keeper_confirm` |
| `/api/tool-io-orders/<order_no>/generate-keeper-text` | `notification:create` |
| `/api/tool-io-orders/<order_no>/generate-transport-text` | `notification:create` |
| `/api/tool-io-orders/<order_no>/notify-transport` | `notification:send_feishu` |
| `/api/tool-io-orders/<order_no>/notify-keeper` | `notification:send_feishu` |
| `/api/orgs` | `dashboard:view` |
| `/api/orgs/tree` | `dashboard:view` |
| `/api/orgs/<org_id>` | `dashboard:view` |
| `/api/orgs` (POST) | `admin:user_manage` |
| `/api/orgs/<org_id>` (PUT) | `admin:user_manage` |
| `/api/health` | None |
| `/api/db/test` | `dashboard:view` |
| `/api/admin/roles` | `admin:user_manage` |
| `/api/admin/users` | `admin:user_manage` |
| `/api/admin/users/<user_id>` | `admin:user_manage` |
| `/api/admin/users/<user_id>/roles` | `admin:user_manage` |
| `/api/admin/users/<user_id>/status` | `admin:user_manage` |
| `/api/admin/users/<user_id>/password-reset` | `admin:user_manage` |

---

## 7. Pagination Standard

All list endpoints use the same pagination structure:

```json
{
  "pagination": {
    "page_no": 1,
    "page_size": 20,
    "total_count": 100
  }
}
```

Default `page_no`: 1
Default `page_size`: 20
