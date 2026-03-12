Primary Executor: Codex
Task Type: Feature Implementation
Stage: 052
Goal: Implement RBAC role assignment and an administrator-only account management page so admins can create user accounts, enter employee name and employee ID, and assign department and role.
Execution: RUNPROMPT

---

# Context

The project has already implemented or partially implemented:

- authentication foundation
- RBAC design and schema
- organization structure
- login flow
- frontend permission visibility
- admin-only debug tooling

However RBAC is still incomplete in practical usage because real user-role assignment has not been fully landed.

At the moment, the system lacks:

1. reliable test accounts for different business roles
2. admin-driven user creation
3. admin-driven role assignment
4. admin-driven department / organization assignment

Without these capabilities, realistic multi-role testing and real RBAC validation cannot proceed.

This task must complete the first usable RBAC account assignment workflow.

---

# Required References

Read before implementation:

docs/ARCHITECTURE_INDEX.md
docs/RBAC_DESIGN.md
docs/RBAC_DATABASE_SCHEMA.md
docs/RBAC_INIT_DATA.md
docs/RBAC_PERMISSION_ENFORCEMENT.md
docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md
docs/ORG_STRUCTURE_IMPLEMENTATION.md
docs/API_CONTRACT_SNAPSHOT.md

Also inspect the real current backend and frontend implementation, especially:

- auth-related APIs
- current user context API
- RBAC permission loading
- organization APIs
- existing admin-related routes if any
- current frontend routing and page layout

Use the real current codebase and database schema as source of truth.

---

# Core Task

Implement the first usable RBAC account management flow.

The system must support an administrator creating and managing user accounts through a dedicated admin page.

The administrator must be able to:

1. create a user account
2. enter employee name
3. enter employee ID / work number
4. assign department / organization
5. assign one or more roles
6. manage account status

This must be implemented safely and consistently with the existing RBAC model.

---

# Required Work

## A. Confirm and Extend User Model Safely

Inspect the current user schema and determine the correct fields for:

- login name
- display name / employee name
- employee ID / work number
- default organization
- status
- password hash

If employee ID / work number is not currently modeled explicitly, add it in the safest compatible way.

Do not redesign the entire schema.
Keep changes minimal and compatible with current auth logic.

---

## B. Backend Account Management APIs

Implement administrator-only backend APIs for account management.

At minimum support:

1. create user
2. list users
3. read user detail
4. update user basic info
5. assign organization / department
6. assign one or more roles
7. enable / disable account
8. reset password if practical in current design

Suggested conceptual APIs:

GET /api/admin/users
GET /api/admin/users/{user_id}
POST /api/admin/users
PUT /api/admin/users/{user_id}
PUT /api/admin/users/{user_id}/roles
PUT /api/admin/users/{user_id}/status
PUT /api/admin/users/{user_id}/password-reset

Use the existing backend style and permission model.

These APIs must be accessible only to administrators.

---

## C. Role Assignment Logic

Use the existing RBAC tables to assign roles properly.

At minimum support assigning these roles if they already exist in current seed/init data:

- Team Leader
- Keeper
- Planner
- System Administrator
- Auditor

Use the current role model from the real database.

Do not invent a second role system.

Support user-role assignment through the current relation table and current organization context model.

---

## D. Department / Organization Assignment Logic

Allow admin to assign a user to a department / organization.

This should integrate with the current organization structure.

At minimum support:

- selecting one default department / organization
- storing that organization on the user or relation model consistently
- using real organization tree/list data from existing organization APIs

Do not invent a separate department system outside the current organization model.

---

## E. Password Bootstrap Strategy

Define and implement a safe first-version password strategy.

Recommended practical options:

- admin sets an initial password at account creation
- or system generates a temporary password
- or admin creates account then performs reset-password action

Whichever approach is chosen, document it clearly.

Passwords must remain hashed.
Never store plaintext passwords.

---

## F. Administrator-Only Frontend Page

Create an administrator-only frontend page for account management.

The page must allow administrators to:

- view user list
- create account
- input employee name
- input employee ID / work number
- select department / organization
- assign role
- view current account status
- enable / disable users
- trigger password reset if implemented

Suggested page direction:

- clear admin form layout
- practical internal-tool UI
- table + drawer/modal or table + side panel
- consistent with Tailwind + shadcn + Mist

Suggested route example:

/admin/users

This route must be protected by admin permission.

---

## G. Frontend Form Requirements

At minimum the admin account creation UI must include:

- login name
- employee name
- employee ID / work number
- organization / department selector
- role selector
- initial password or reset strategy entry if supported
- account status

Validation must include:

- required fields
- duplicate login name handling
- duplicate employee ID handling if relevant
- invalid organization selection
- invalid role assignment

Use safe error feedback.

---

## H. Permission Protection

This capability must be restricted to administrators only.

At minimum enforce:

- backend API permission checks
- frontend route guard
- frontend menu visibility

Use the current RBAC permission model.

If necessary, use or add permissions such as:

- admin:user_manage
- admin:role_manage

Do not weaken the current security model.

---

## I. Test Account Preparation

Use this task to make the system testable.

At minimum after implementation it should be easy to create or maintain test accounts for:

- Team Leader
- Keeper
- Planner
- Admin
- Auditor

This is important because later human testing and RBAC validation depend on these accounts.

---

## J. Documentation

Create:

docs/RBAC_ROLE_ASSIGNMENT_AND_ACCOUNT_ADMIN_PAGE.md

This document must include:

1. user model fields actually used
2. account management APIs
3. role assignment flow
4. organization assignment flow
5. password strategy
6. admin page structure
7. permission protection rules
8. recommended test accounts

---

# Constraints

1. Do not redesign RBAC from scratch.
2. Do not create a second organization model.
3. Keep implementation compatible with current auth flow.
4. Keep code and comments in English.
5. Keep UI practical and internal-tool oriented.
6. Restrict all account-management capability to administrators only.
7. Use the real current schema and APIs as source of truth.

---

# Completion Criteria

The task is complete when:

1. administrator can open a dedicated account management page
2. administrator can create a user account
3. administrator can enter employee name
4. administrator can enter employee ID / work number
5. administrator can assign department / organization
6. administrator can assign role
7. administrator-only protection works on both frontend and backend
8. test accounts for business roles can now be created
9. docs/RBAC_ROLE_ASSIGNMENT_AND_ACCOUNT_ADMIN_PAGE.md exists and is up-to-date