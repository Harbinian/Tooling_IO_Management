# RBAC Role Assignment and Account Admin Page

## Overview

This document describes the first usable administrator-only account management flow for the Tooling IO Management System.

The implementation keeps the current authentication and organization model intact and adds:

- explicit `employee_no` support on `sys_user`
- administrator-only user management APIs
- administrator-only `/admin/users` frontend page
- organization-aware role assignment using the current RBAC relation tables
- hashed initial password and password reset workflow

## User Model Fields Used

The effective account model remains `sys_user`.

Fields used by authentication and account management:

| Field | Purpose |
|---|---|
| `user_id` | stable internal identifier |
| `login_name` | login username |
| `display_name` | employee display name |
| `employee_no` | employee ID / work number |
| `password_hash` | PBKDF2 password hash |
| `status` | `active` or `disabled` |
| `default_org_id` | default organization / department |
| `last_login_at` | last login timestamp |
| `created_at`, `created_by`, `updated_at`, `updated_by` | audit fields |

`employee_no` is added compatibly through RBAC table bootstrap logic if it does not already exist.

## Account Management APIs

All endpoints below require `admin:user_manage`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/admin/roles` | GET | list active roles for assignment |
| `/api/admin/users` | GET | list users with role and org summary |
| `/api/admin/users/<user_id>` | GET | read one user detail |
| `/api/admin/users` | POST | create user |
| `/api/admin/users/<user_id>` | PUT | update basic user info |
| `/api/admin/users/<user_id>/roles` | PUT | replace assigned roles and org context |
| `/api/admin/users/<user_id>/status` | PUT | enable or disable account |
| `/api/admin/users/<user_id>/password-reset` | PUT | reset password |

Create and update validation includes:

- required `login_name`
- required `display_name`
- required `employee_no`
- duplicate `login_name` rejection
- duplicate `employee_no` rejection
- invalid organization rejection
- invalid or inactive role rejection

## Role Assignment Flow

Role assignment uses the existing relation model only:

- `sys_role`
- `sys_user_role_rel`
- `sys_role_permission_rel`

Behavior:

1. Admin selects one or more roles.
2. Backend validates that all role IDs exist and are active.
3. Existing `sys_user_role_rel` rows for the user are marked `disabled`.
4. New active rows are inserted for the selected roles.
5. The first selected role is marked `is_primary = 1`.
6. The chosen organization context is written to `sys_user_role_rel.org_id`.

This keeps the current RBAC resolution logic intact.

## Organization Assignment Flow

Organization assignment uses the current organization model only:

- `sys_org`
- `sys_user.default_org_id`
- `sys_user_role_rel.org_id`

Behavior:

1. Admin selects one default organization from the existing org tree.
2. Backend validates the selected `org_id` against `sys_org`.
3. `sys_user.default_org_id` is updated.
4. Role assignments are written with the same `org_id` so role context and default organization remain aligned in this first version.

## Password Strategy

The first-version password strategy is administrator-set password bootstrap.

Rules:

- account creation requires `initial_password`
- password is stored only as PBKDF2 hash
- plaintext password is never stored
- later resets use `/api/admin/users/<user_id>/password-reset`

This keeps the workflow practical for internal testing and controlled account creation.

## Admin Page Structure

Frontend route:

- `/admin/users`

Page layout:

- left: searchable user list
- right: create/edit account panel
- inline role checklist
- default organization selector
- status control
- password reset block for existing accounts

Core fields exposed:

- login name
- employee name
- employee ID / work number
- default department / organization
- one or more roles
- account status
- initial password on create

## Permission Protection Rules

Protection is enforced in three places:

1. Backend APIs use `@require_permission("admin:user_manage")`
2. Frontend route `/admin/users` uses `meta.permission = "admin:user_manage"`
3. Sidebar navigation item is shown only when the current session has `admin:user_manage`

This feature does not introduce a second authorization model.

## Recommended Test Accounts

Recommended role coverage for testing:

| Role | Suggested login | Suggested employee_no |
|---|---|---|
| Team Leader | `team.leader` | `EMP-TL-001` |
| Keeper | `keeper.user` | `EMP-KP-001` |
| Planner | `planner.user` | `EMP-PL-001` |
| System Administrator | `admin` | `EMP-AD-001` |
| Auditor | `auditor.user` | `EMP-AU-001` |

These can all be created through the administrator page after deployment.
