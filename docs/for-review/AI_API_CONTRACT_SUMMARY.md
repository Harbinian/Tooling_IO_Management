# AI Review: API Contract Summary

## Base URL

```
http://localhost:8151
```

## Authentication

All API requests require authentication token in header:
```
Authorization: Bearer <token>
```

## Endpoints Summary

### Auth API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/auth/login | User login |
| GET | /api/auth/me | Get current user |

### Order API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/tool-io-orders | List orders (paginated, filtered) |
| POST | /api/tool-io-orders | Create new order |
| GET | /api/tool-io-orders/{order_no} | Get order detail |
| POST | /api/tool-io-orders/{order_no}/submit | Submit order |
| POST | /api/tool-io-orders/{order_no}/keeper-confirm | Keeper confirmation |
| POST | /api/tool-io-orders/{order_no}/final-confirm | Final confirmation |
| GET | /api/tool-io-orders/{order_no}/final-confirm-availability | Check final confirm eligibility |
| POST | /api/tool-io-orders/{order_no}/assign-transport | Assign transport |
| POST | /api/tool-io-orders/{order_no}/transport-start | Start transport |
| POST | /api/tool-io-orders/{order_no}/transport-complete | Complete transport |
| POST | /api/tool-io-orders/{order_no}/reject | Reject order |
| POST | /api/tool-io-orders/{order_no}/cancel | Cancel order |
| GET | /api/tool-io-orders/{order_no}/logs | Get order logs |
| GET | /api/tool-io-orders/{order_no}/notification-records | Get notifications |
| POST | /api/tool-io-orders/{order_no}/notify-transport | Send transport notification |
| POST | /api/tool-io-orders/{order_no}/notify-keeper | Send keeper notification |
| GET | /api/tool-io-orders/pending-keeper | Get pending keeper items |

### Tool API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/tools/search | Search tools in inventory |
| POST | /api/tools/batch-query | Batch query tools |

### Dashboard API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/dashboard/metrics | Get dashboard metrics |

### Organization API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/orgs | List organizations |
| GET | /api/orgs/tree | Get org tree |
| GET | /api/orgs/{org_id} | Get org detail |
| POST | /api/orgs | Create org |
| PUT | /api/orgs/{org_id} | Update org |

### Admin User API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/admin/roles | List roles |
| GET | /api/admin/users | List users |
| GET | /api/admin/users/{user_id} | Get user detail |
| POST | /api/admin/users | Create user |
| PUT | /api/admin/users/{user_id} | Update user |
| PUT | /api/admin/users/{user_id}/roles | Assign roles |
| PUT | /api/admin/users/{user_id}/status | Toggle user status |
| PUT | /api/admin/users/{user_id}/password-reset | Reset password |

### Notification API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/notifications | Get current user notifications |
| POST | /api/notifications/{id}/read | Mark notification as read |

### System API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/health | Health check |
| GET | /api/system/health | Detailed health |
| GET | /api/system/diagnostics/recent-errors | Recent errors |
| GET | /api/system/diagnostics/notification-failures | Failed notifications |
| GET | /api/db/test | Database connection test |

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## Query Parameters

### Order List Filtering
- `page`: Page number
- `page_size`: Items per page
- `order_type`: 出库/入库
- `order_status`: Order status
- `org_id`: Organization filter
