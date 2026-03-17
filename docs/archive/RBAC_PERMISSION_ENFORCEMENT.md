# RBAC Permission Enforcement

## Overview

This document describes the first production-ready RBAC enforcement layer for the Tooling IO Management System.

The implementation keeps the existing authentication model and organization model intact while adding:

- centralized permission resolution
- reusable API permission guards
- permission-aware request context
- structured 401 and 403 API responses
- frontend-consumable current-user permission data

## Permission Resolution Flow

1. The client authenticates through `POST /api/auth/login`.
2. The backend issues a signed bearer token containing the `user_id`.
3. Each authenticated request is resolved through `get_current_user_from_token()`.
4. `backend/services/rbac_service.py` loads:
   - active user-role assignments from `sys_user_role_rel`
   - active role definitions from `sys_role`
   - active role-permission mappings from `sys_role_permission_rel`
   - active permissions from `sys_permission`
5. The resolved role assignments and permissions are attached to the current user identity.
6. Organization context is merged from `default_org_id`, `sys_user_role_rel.org_id`, and `sys_org`.

## Role-Permission Lookup Logic

The backend uses `backend/services/rbac_service.py` as the central permission resolver.

Key functions:

- `load_user_roles(user_id)`
- `load_permissions_for_role_ids(role_ids)`
- `resolve_user_permissions(user_id, roles=None)`
- `build_permission_context(user_id, roles=None)`
- `has_permission(user, permission_code)`

Resolution rules:

- only active user-role relations are used
- only active roles are used
- only active role-permission relations are used
- only active permissions are returned
- duplicate permissions across multiple roles are merged into one normalized list
- role assignments keep organization context for future data-scope enforcement

## Request Context Fields

Authenticated requests expose the following fields:

- `g.current_user`
- `request.current_user`
- `request.user_id`
- `request.roles`
- `request.role_codes`
- `request.permissions`
- `request.current_org`
- `request.current_org_id`
- `request.default_org`
- `request.default_org_id`

The current-user payload returned by `GET /api/auth/me` includes:

- `user_id`
- `login_name`
- `display_name`
- `status`
- `default_org_id`
- `roles`
- `role_codes`
- `permissions`
- `default_org`
- `current_org`
- `role_orgs`

## Permission Guard Design

The API layer uses two decorators in `web_server.py`:

- `require_auth`
- `require_permission(permission_code)`

Guard behavior:

- no authenticated user context -> HTTP 401
- authenticated but missing permission -> HTTP 403
- valid authenticated permission match -> request proceeds normally

The permission decorator relies on `backend.services.auth_service.require_permission()`, which in turn uses the centralized RBAC service.

## Protected API List

Current protected endpoints include:

- `GET /api/auth/me`
- `GET /api/orgs`
- `GET /api/orgs/tree`
- `GET /api/orgs/{org_id}`
- `POST /api/orgs`
- `PUT /api/orgs/{org_id}`
- `GET /api/tool-io-orders`
- `POST /api/tool-io-orders`
- `GET /api/tool-io-orders/{order_no}`
- `POST /api/tool-io-orders/{order_no}/submit`
- `POST /api/tool-io-orders/{order_no}/keeper-confirm`
- `POST /api/tool-io-orders/{order_no}/final-confirm`
- `GET /api/tool-io-orders/{order_no}/final-confirm-availability`
- `POST /api/tool-io-orders/{order_no}/reject`
- `POST /api/tool-io-orders/{order_no}/cancel`
- `GET /api/tool-io-orders/{order_no}/logs`
- `GET /api/tool-io-orders/{order_no}/notification-records`
- `GET /api/tool-io-orders/pending-keeper`
- `GET /api/tools/search`
- `POST /api/tools/batch-query`
- `GET /api/tool-io-orders/{order_no}/generate-keeper-text`
- `GET /api/tool-io-orders/{order_no}/generate-transport-text`
- `POST /api/tool-io-orders/{order_no}/notify-transport`
- `POST /api/tool-io-orders/{order_no}/notify-keeper`
- `GET /api/db/test`

Permission mapping follows `docs/RBAC_DESIGN.md` and `docs/RBAC_INIT_DATA.md`.

## 401 and 403 Behavior

Unauthenticated response format:

```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "authentication required"
  }
}
```

Unauthorized response format:

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "missing required permission: order:list",
    "details": {
      "required_permission": "order:list"
    }
  }
}
```

Design notes:

- 401 is used when the request is not authenticated
- 403 is used when the request is authenticated but lacks the required permission
- permission failures do not expose internal table or role details

## Frontend Integration Notes

Frontend code can use `GET /api/auth/me` as the single source of truth for:

- current identity
- resolved roles
- resolved permissions
- default organization
- current organization

The frontend HTTP client must handle both legacy string errors and structured RBAC error payloads.

## Future Data Scope Extension Notes

This implementation prepares for organization-aware filtering without implementing full data scope enforcement yet.

Future work can reuse:

- `roles`
- `role_codes`
- `permissions`
- `current_org`
- `default_org`
- `role_orgs`

The next data-scope layer should extend authorization with:

- `ALL`
- `ORG`
- `ORG_AND_CHILDREN`
- `SELF`
- `ASSIGNED`

using the existing RBAC schema and the existing organization tree service.
