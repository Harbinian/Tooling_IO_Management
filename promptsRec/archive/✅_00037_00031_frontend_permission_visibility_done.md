Primary Executor: Gemini
Task Type: Feature Implementation
Category: Frontend RBAC Integration
Goal: Implement frontend permission visibility control so UI components, menus, and actions respond dynamically to RBAC permissions returned by the backend.
Execution: RUNPROMPT
Prompt: Implement frontend permission visibility control

---

# Context

The backend now supports:

- RBAC tables
- user authentication
- permission resolution
- permission enforcement on APIs
- current user permission exposure

Relevant documents:

docs/ARCHITECTURE_INDEX.md  
docs/RBAC_DESIGN.md  
docs/RBAC_PERMISSION_ENFORCEMENT.md  

Frontend currently uses:

- Vue
- Tailwind CSS
- shadcn/ui
- Tailark Mist layout system

The frontend must now become **permission-aware**.

Without frontend permission awareness:

- users see actions they cannot perform
- UI becomes confusing
- permission failures happen only after API calls

This task integrates RBAC into the frontend rendering layer.

---

# Objectives

Implement permission-based UI rendering.

The system must support:

- permission-based menu visibility
- permission-based button visibility
- page access control
- simple permission checking utilities
- compatibility with the existing UI architecture

The frontend should use permissions returned from:

GET /api/auth/me

---

# Required Components

---

# 1 Permission Utility

Create a reusable permission checking utility.

Suggested location:

frontend/src/utils/permission.ts

Example functions:

hasPermission(permissionCode)

hasAnyPermission(permissionList)

hasAllPermissions(permissionList)

Responsibilities:

- read permissions from the current user state
- return boolean results for UI logic
- keep logic simple and predictable

---

# 2 User Permission Store

Ensure the frontend state includes:

- user_id
- display_name
- roles
- permissions

Permissions should be loaded from:

GET /api/auth/me

Store location example:

frontend/src/stores/authStore.ts

or existing user store if already present.

This store must expose permissions to UI components.

---

# 3 Menu Visibility Control

Update the navigation menu configuration so menu items may include permission requirements.

Example menu configuration concept:

dashboard → dashboard:view  
order list → order:list  
create order → order:create  
keeper workspace → order:keeper_confirm  

Menus without required permission must not be rendered.

This logic must integrate with the Mist sidebar layout.

---

# 4 Button Visibility Control

Buttons must only appear if the user has permission.

Examples:

Create Order button → order:create

Submit Order → order:submit

Keeper Confirm → order:keeper_confirm

Send Feishu → notification:send_feishu

Example approach:

conditional rendering in Vue components using permission utility.

Avoid complex inline logic.

---

# 5 Page Access Guard

Certain pages require permission to access.

Examples:

order creation page → order:create

keeper workspace → order:keeper_confirm

admin pages → admin:user_manage

Implement route guard logic.

Suggested location:

frontend/src/router/permissionGuard.ts

Behavior:

- if user lacks permission
- redirect to dashboard or error page

---

# 6 Empty State UX

When permission is missing:

- hide action buttons
- show safe fallback UI if necessary
- avoid broken layouts

Example:

If user cannot create order:

hide "New Order" button.

---

# 7 Compatibility With Existing Pages

Apply permission visibility rules to existing UI modules such as:

Dashboard  
Order List  
Order Detail  
Order Creation  
Keeper Processing Workspace  

Do not redesign the UI layout.

Only add permission awareness.

---

# 8 Error Handling

Frontend must gracefully handle:

HTTP 403 responses.

If a forbidden response occurs:

- show friendly message
- optionally redirect user
- avoid application crash

---

# 9 Documentation

Create:

docs/FRONTEND_PERMISSION_VISIBILITY.md

The document must include:

1 permission utility design  
2 permission store structure  
3 menu permission mapping  
4 button permission examples  
5 route guard behavior  
6 interaction with backend permission system

---

# Constraints

Do not redesign backend permission logic.

Use permission codes defined in:

docs/RBAC_DESIGN.md

Do not create a new permission naming scheme.

Keep code and comments in English.

Keep UI style consistent with Tailwind + shadcn + Mist layout.

---

# Completion Criteria

The task is complete when:

1 frontend loads user permissions from backend
2 permission utility functions exist
3 menus hide correctly without permission
4 buttons hide correctly without permission
5 route guard prevents unauthorized page access
6 UI remains visually consistent
7 docs/FRONTEND_PERMISSION_VISIBILITY.md exists