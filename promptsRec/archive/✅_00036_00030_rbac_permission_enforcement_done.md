Primary Executor: Codex
Task Type: Feature Implementation
Category: Platform Infrastructure
Goal: Implement RBAC permission enforcement across backend APIs and expose permission-aware user context for frontend usage.
Execution: RUNPROMPT

---

# Context

The system has already completed or is completing:

- RBAC design
- RBAC database schema
- RBAC initial data
- architecture index
- user authentication system
- organization structure module

Relevant documents:

docs/ARCHITECTURE_INDEX.md  
docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/RBAC_INIT_DATA.md  
docs/ORG_STRUCTURE_IMPLEMENTATION.md  

Before implementation, load these documents to ensure:

- permission model consistency
- role-permission relation correctness
- organization-aware authorization compatibility
- future data scope extension readiness

The project now needs real permission enforcement.

Without permission enforcement:

- login only proves identity
- APIs remain unprotected
- role definitions have no operational value
- frontend cannot reliably hide or show features by permission

This task implements the first working version of RBAC enforcement.

---

# Objectives

Implement a minimal but production-ready RBAC permission enforcement system.

The system must support:

- loading permissions from RBAC tables
- attaching permissions to authenticated user context
- checking required permissions at API level
- returning 403 when permission is missing
- exposing permission-aware current-user data to frontend
- preparing for future data scope enforcement

---

# Required Components

Implement the following components.

---

# 1 Permission Resolution Service

Create a backend permission service.

Possible location:

backend/services/rbac_service.py

Responsibilities:

- resolve current user roles
- resolve permissions from role-permission mapping
- merge permissions across multiple roles
- support organization-context-aware role lookup if needed
- return normalized permission set for current user

---

# 2 Permission Guard

Implement a reusable permission guard for backend APIs.

Possible forms:

- decorator
- middleware helper
- route guard utility

Example usage:

require_permission("order:create")
require_permission("order:keeper_confirm")
require_permission("notification:send_feishu")

Behavior:

- allow request if current user has permission
- reject with HTTP 403 if permission is missing
- return clear error message
- do not expose sensitive internal details

---

# 3 Integrate With Authentication Context

Extend the current authentication flow so the request context includes:

- current user id
- roles
- permissions
- current organization context if available

The permission guard must work with the existing authentication middleware or token/session validation logic.

Do not redesign authentication from scratch.

---

# 4 Protect Core APIs

Apply permission checks to core APIs where appropriate.

At minimum review and protect APIs related to:

- dashboard access
- tool search
- order creation
- order submission
- order listing
- order detail
- keeper confirmation
- final confirmation
- notification viewing
- Feishu sending
- user/role/admin endpoints if already present

Use the permission model defined in RBAC_DESIGN.md.

Do not invent a different permission naming scheme.

---

# 5 Current User Permission Exposure

Ensure the current user endpoint returns permission-aware user context.

The frontend should be able to retrieve:

- user identity
- roles
- permissions
- default organization or current organization context if available

This is needed for menu visibility, button visibility, and page-level access control.

---

# 6 Frontend Compatibility Support

This task is backend-focused, but it must expose stable permission data for frontend use.

At minimum the frontend should be able to consume:

- current user roles
- permission list

Do not build the full frontend permission control system in this task unless the current project already has a small integration point ready.

---

# 7 Error Handling

Permission failures must be handled consistently.

Requirements:

- return HTTP 401 for unauthenticated requests if applicable
- return HTTP 403 for authenticated but unauthorized requests
- return structured JSON error response
- keep behavior consistent across protected APIs

Do not silently bypass permission checks.

---

# 8 Documentation

Create:

docs/RBAC_PERMISSION_ENFORCEMENT.md

This document must include:

1. permission resolution flow
2. role-permission lookup logic
3. request context fields
4. permission guard design
5. protected API list
6. 401/403 behavior
7. frontend integration notes
8. future data scope extension notes

---

# Constraints

Do not redesign RBAC tables.

Use the schema and naming defined in:

docs/RBAC_DATABASE_SCHEMA.md  
docs/RBAC_DESIGN.md  

Do not invent a second permission model.

Keep the code and comments in English.

Keep implementation minimal, modular, and production-oriented.

Do not fully implement data scope filtering in this task unless needed for small supporting utilities.

---

# Completion Criteria

The task is complete when:

1. permissions can be resolved from RBAC tables
2. authenticated request context includes permissions
3. permission guard works
4. protected APIs return 403 when permission is missing
5. current user endpoint exposes permission-aware context
6. docs/RBAC_PERMISSION_ENFORCEMENT.md exists