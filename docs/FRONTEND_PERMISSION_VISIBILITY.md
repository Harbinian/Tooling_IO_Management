# Frontend Permission Visibility Control

This document describes the implementation of frontend permission visibility control based on RBAC.

## Overview

The frontend now dynamically responds to user permissions provided by the backend. This ensures that users only see the menus, buttons, and pages they are authorized to interact with.

## Components

### 1. Permission Utility

Location: `frontend/src/utils/permission.js`

Provides helper functions to check permissions:
- `hasPermission(permissionCode)`: Checks for a single permission.
- `hasAnyPermission(permissionList)`: Checks if the user has at least one permission from the list.
- `hasAllPermissions(permissionList)`: Checks if the user has all permissions in the list.

### 2. Global Directive: `v-permission`

Location: `frontend/src/main.js`

A custom Vue directive used to conditionally remove elements from the DOM if the user lacks the required permission.

Example usage:
```vue
<Button v-permission="'order:create'">New Order</Button>
```

### 3. Menu Visibility

Location: `frontend/src/layouts/MainLayout.vue`

The navigation sidebar filters menu items based on the user's permission set.

Mapped permissions:
- Dashboard -> `dashboard:view`
- Registry -> `order:list`
- New Request -> `order:create`
- Workbench -> `order:keeper_confirm`

### 4. Page Access Guard

Location: `frontend/src/router/index.js`

A global route guard (`beforeEach`) checks if the user has the permission defined in the route's `meta.permission` property. Unauthorized access redirects to the Dashboard.

### 5. Component-Level Logic

Action buttons in pages are controlled using `v-permission` or `session.hasPermission()`:
- **Dashboard**: "New Request" and "History" buttons, plus Quick Action cards.
- **Order List**: "Submit", "Cancel", and "Final Confirm" buttons.
- **Order Create**: "Submit" and "Save Draft" buttons.
- **Keeper Process**: "Final Confirm", "Approve", "Reject", and "Send Feishu" buttons.

## Interaction with Backend

The frontend loads user permissions via `GET /api/auth/me` during the hydration process in the session store. If the backend returns an updated permission set, the UI will automatically reflect the changes on the next reload or re-hydration.
