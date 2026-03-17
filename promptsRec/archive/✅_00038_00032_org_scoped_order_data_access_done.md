Primary Executor: Codex
Task Type: Feature Implementation
Category: Backend RBAC Data Scope
Goal: Implement organization-scoped order data access so users only see and operate on orders within their allowed organizational scope.
Execution: RUNPROMPT

---

# Context

The system has already completed or is completing:

- RBAC design
- RBAC database schema
- RBAC initial data
- user authentication
- organization structure module
- RBAC permission enforcement
- frontend permission visibility control

Relevant documents:

docs/ARCHITECTURE_INDEX.md  
docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/ORG_STRUCTURE_IMPLEMENTATION.md  
docs/RBAC_PERMISSION_ENFORCEMENT.md  

The project now needs real data-scope enforcement.

At the moment, permission control may already restrict what actions users can perform, but without organization-scoped data filtering, users may still see orders outside their intended scope.

This task implements the first working version of **organization-aware data access** for core order queries and operations.

---

# Objectives

Implement organization-scoped order data access.

The system must support:

- resolving the current user's organization context
- resolving the user's role-based data scope
- filtering order list and detail access by organization scope
- supporting basic scope types such as:
  - ALL
  - ORG
  - ORG_AND_CHILDREN
  - SELF
  - ASSIGNED
- preserving current business workflow behavior

This task focuses on order data first.

---

# Required Components

---

# 1 Data Scope Resolution Service

Create or extend a backend RBAC data scope service.

Suggested location:

backend/services/rbac_data_scope_service.py

Responsibilities:

- load current user roles
- load role data scopes
- merge scope rules if multiple roles exist
- resolve current organization context
- resolve descendant organizations when required
- produce query-ready scope constraints for order data

Do not hardcode a second RBAC model.

Use existing RBAC tables and organization structure.

---

# 2 Scope Types to Support

Implement support for these scope types defined in RBAC:

ALL  
ORG  
ORG_AND_CHILDREN  
SELF  
ASSIGNED  

Expected meanings:

ALL  
User may access all orders

ORG  
User may access orders belonging to the current organization

ORG_AND_CHILDREN  
User may access orders belonging to current organization and descendant organizations

SELF  
User may access orders created by themselves

ASSIGNED  
User may access orders assigned to themselves or to their keeper/processing context, based on the current real schema

Do not invent new scope types.

---

# 3 Organization Tree Resolution

Use the real organization structure module to resolve organization hierarchies.

Requirements:

- resolve current user's default organization
- resolve parent-child relationships
- return descendant organization IDs when needed

Do not create a separate organization tree model.

---

# 4 Apply Data Scope to Order List API

Update the order list query logic so it applies organization-aware filtering.

This should affect APIs such as:

GET /api/tool-io-orders

Use the current real schema and existing business model to determine how orders relate to organizations.

Potential query anchors may include:

- initiator organization
- keeper organization
- current processing organization
- creator user
- assigned processor

Do not assume fixed field names.
Inspect the real schema and current order implementation first.

---

# 5 Apply Data Scope to Order Detail Access

Update order detail access logic so users cannot open orders outside their scope.

For example:

- a team leader should not open unrelated organization orders
- a keeper should not access orders outside their assigned org/warehouse scope
- an admin with ALL scope should still access everything

This must apply to detail APIs and backend service methods.

---

# 6 Apply Data Scope to Core Workflow Operations

Protect workflow actions using both permission and data scope.

At minimum review operations such as:

- order detail fetch
- keeper confirmation
- final confirmation
- notification record access
- Feishu send trigger if already implemented

A user must not operate on records outside their allowed scope even if they hold the permission.

---

# 7 Scope Combination Rules

If a user has multiple roles, combine scopes safely.

Suggested principles:

- ALL overrides narrower scopes
- ORG_AND_CHILDREN includes ORG
- SELF remains additive
- ASSIGNED remains additive
- do not broaden scope beyond assigned role definitions

Document the merge logic clearly.

---

# 8 Error Handling

When a user accesses data outside allowed scope:

- return HTTP 403 or 404 based on the current system style
- do not leak sensitive record existence unnecessarily
- keep behavior consistent across list and detail APIs

Use the project's current error response style.

---

# 9 Documentation

Create:

docs/ORG_SCOPED_ORDER_DATA_ACCESS.md

The document must include:

1. data scope resolution flow  
2. supported scope types  
3. organization tree resolution logic  
4. order list filtering strategy  
5. order detail protection strategy  
6. workflow action protection strategy  
7. scope merge rules  
8. limitations or assumptions

---

# Constraints

Do not redesign RBAC tables.

Use the models defined in:

docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  

Do not invent a second organization model.

Do not assume fixed order field names without inspecting the real schema.

Keep code and comments in English.

Keep implementation minimal, modular, and production-oriented.

This task focuses on order-related data access only, not every table in the system.

---

# Completion Criteria

The task is complete when:

1. current user data scope can be resolved
2. organization tree can be used for ORG_AND_CHILDREN scope
3. order list results are filtered by scope
4. order detail access is filtered by scope
5. core workflow operations respect both permission and scope
6. docs/ORG_SCOPED_ORDER_DATA_ACCESS.md exists