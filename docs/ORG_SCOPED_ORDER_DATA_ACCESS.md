# Organization-Scoped Order Data Access

## Overview

This document describes the first production-ready organization-aware data-scope layer for order access.

The implementation extends RBAC authorization with order data filtering while keeping the existing:

- RBAC schema
- organization hierarchy model
- authentication model
- order workflow model

The current scope layer applies to order list queries, order detail access, and core order workflow actions.

## Data Scope Resolution Flow

1. Authentication resolves the current user identity, roles, permissions, and organization context.
2. `backend/services/rbac_data_scope_service.py` loads active role data-scope rows from `sys_role_data_scope_rel`.
3. The service resolves scope rows per active role assignment instead of flattening all roles first.
4. Organization identifiers are taken from the specific role assignment that granted `ORG` or `ORG_AND_CHILDREN`.
5. If `ORG_AND_CHILDREN` is present for one assignment, descendants are expanded only for that assignment's organization anchor.
6. The resolved scope is converted into:
   - SQL conditions for order list queries
   - in-memory record checks for detail and workflow operations

## Supported Scope Types

The order-access layer currently supports:

- `ALL`
- `ORG`
- `ORG_AND_CHILDREN`
- `SELF`
- `ASSIGNED`

Meaning:

- `ALL`: access all orders
- `ORG`: access orders owned by the organization bound to the matching role assignment
- `ORG_AND_CHILDREN`: access orders owned by the organization bound to the matching role assignment and its descendants
- `SELF`: access orders initiated by the current user
- `ASSIGNED`: access orders assigned to the current user as keeper or transport assignee

## Organization Tree Resolution Logic

Organization hierarchy is resolved through `backend/services/org_service.py`.

Current logic uses:

- `get_descendant_org_ids(org_id)`
- `resolve_user_org_context(user_id, default_org_id)`

The data-scope layer does not create a second organization model. It reuses:

- `sys_org`
- `sys_user.default_org_id`
- `sys_user_role_rel.org_id`

## Order List Filtering Strategy

Order list filtering is applied in SQL through `database.get_tool_io_orders(...)`.

The service builds extra SQL conditions from resolved scope context:

- `SELF` -> matches the order initiator column
- `ASSIGNED` -> matches keeper or transport assignee columns
- `ORG` / `ORG_AND_CHILDREN` -> matches the persisted order `org_id`

This keeps pagination and total counts aligned with the filtered result set.

## Order Detail Protection Strategy

Order detail access is checked in `backend/services/tool_io_service.py`.

Flow:

1. Load the order through runtime-safe detail queries
2. Resolve the current user's merged data scope
3. Match order participants against the scope rules
4. Return an empty result when the order is outside scope

The API layer then returns `404` for out-of-scope order access to avoid leaking record existence.

## Workflow Action Protection Strategy

The following order-related operations now require both permission and scope:

- detail fetch
- submit
- keeper confirmation
- final confirmation
- reject
- cancel
- notification record access
- keeper text generation
- transport text generation
- keeper notification send
- transport notification send
- pending keeper list

If an order is outside scope, service methods return `order not found`, and the API layer maps that to `404` for order-specific endpoints.

## Scope Merge Rules

The current merge behavior is:

- `ALL` overrides narrower scopes
- `ORG_AND_CHILDREN` expands all direct organization anchors to include descendants
- `ORG` keeps direct organization anchors only
- `SELF` adds creator-based access
- `ASSIGNED` adds keeper/transport-assignee-based access
- merged scopes never broaden beyond active role assignments and resolved organization relationships

## Limitations and Assumptions

- The order schema now stores a dedicated `org_id` used as the authoritative ownership field for organization scope checks.
- If a caller bypasses request-context-aware service usage and does not pass `current_user`, data-scope checks are not enforced. Web API routes now pass the authenticated user explicitly.
- This task focuses on order-related data access only. It does not yet apply scope filtering to every table in the system.
