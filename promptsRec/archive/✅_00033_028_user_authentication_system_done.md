Primary Executor: Codex
Task Type: Feature Implementation
Category: Platform Infrastructure
Goal: Implement the basic user authentication system that integrates with RBAC and enables login, token/session authentication, and current user identity retrieval.
Execution: RUNPROMPT

---

# Context

The system has completed:

- RBAC architecture design
- RBAC database schema
- RBAC initial data

Relevant documents:

docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/RBAC_INIT_DATA.md  
docs/ARCHITECTURE_INDEX.md  

Before implementing authentication logic, load these documents to ensure:

- consistent RBAC usage
- correct database schema usage
- correct role/permission handling

The project currently lacks a user authentication system.

Without authentication:

- RBAC cannot work
- operations cannot be audited
- user identity is unknown
- permission checks cannot be enforced

This task implements the **first version of authentication** using **local accounts**.

---

# Objectives

Implement a minimal but production-ready authentication system.

The system must support:

- login with username and password
- password verification
- session or token generation
- retrieving current user identity
- loading RBAC permissions for the logged-in user

---

# Required Components

Implement the following components.

---

# 1 User Authentication Service

Create a backend authentication service responsible for:

- validating login credentials
- retrieving user information
- loading user roles
- loading permissions
- issuing authentication tokens or sessions

Possible file location:

backend/services/auth_service.py

Responsibilities:

- login validation
- RBAC permission loading
- user identity construction

---

# 2 Login API

Create an API endpoint.

POST /api/auth/login

Request example

{
  "login_name": "username",
  "password": "password"
}

Processing steps:

1. find user by login_name
2. verify password_hash
3. check user status
4. load roles from sys_user_role_rel
5. load permissions via sys_role_permission_rel
6. generate authentication token or session

Response example

{
  "token": "...",
  "user": {
    "user_id": "...",
    "display_name": "...",
    "roles": [...]
  }
}

---

# 3 Current User API

Create endpoint:

GET /api/auth/me

Purpose:

Return the current authenticated user.

Response example

{
  "user_id": "...",
  "display_name": "...",
  "roles": [...],
  "permissions": [...]
}

This endpoint allows the frontend to:

- determine user identity
- determine available UI actions
- render menus and buttons

---

# 4 Authentication Middleware

Implement a middleware or request guard that:

1. reads authentication token
2. validates token/session
3. loads user identity
4. attaches user context to the request

Example request context

request.user_id  
request.roles  
request.permissions  

All protected APIs should depend on this middleware.

---

# 5 Permission Guard

Create a permission checking mechanism for APIs.

Example usage

order:create  
order:submit  
order:keeper_confirm  

The guard should check:

- whether the current user has the required permission

Example usage in backend

require_permission("order:create")

If permission is missing:

Return HTTP 403.

---

# 6 Password Handling

Password must be stored as a hash.

Recommended approach:

- bcrypt
or
- secure salted hash

Never store plain text passwords.

---

# 7 Initial Admin User

Ensure the system can bootstrap with an admin account.

Add documentation or SQL example for creating the first user.

Example:

login_name: admin  
password: admin123  

The admin user should receive the role:

ROLE_SYS_ADMIN

---

# 8 Frontend Login Integration

Expose the login endpoint for frontend usage.

Frontend flow:

1 open login page  
2 submit login_name/password  
3 receive token  
4 store token in local storage or cookie  
5 attach token to API requests

---

# 9 Security Requirements

Authentication must enforce:

- password hash verification
- disabled user check
- token validation
- permission guard on protected APIs

---

# Constraints

Do not redesign RBAC.

Use the existing RBAC tables defined in:

docs/RBAC_DATABASE_SCHEMA.md

Follow permission rules defined in:

docs/RBAC_DESIGN.md

---

# Completion Criteria

The task is complete when:

1 login API works
2 token/session is issued
3 current user API works
4 RBAC roles load correctly
5 RBAC permissions load correctly
6 permission guard protects APIs
7 admin account can log in
8 authentication integrates with existing backend services
