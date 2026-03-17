Primary Executor: Gemini
Task Type: Feature Implementation
Category: Frontend Authentication UX
Goal: Implement the login page and authentication flow UI so users can log in, restore session state, and enter the system with role-aware frontend behavior.
Execution: RUNPROMPT

---

# Context

The system has already completed or is completing:

- RBAC design
- RBAC database schema
- RBAC initial data
- user authentication backend
- organization structure module
- RBAC permission enforcement
- frontend permission visibility control
- organization-scoped order data access

Relevant documents:

docs/ARCHITECTURE_INDEX.md  
docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/RBAC_PERMISSION_ENFORCEMENT.md  
docs/FRONTEND_PERMISSION_VISIBILITY.md  

The backend now provides authentication and permission-aware user context.

The frontend must now implement a complete login experience and authenticated app entry flow.

This task focuses on frontend authentication UI and auth-state behavior.

It does NOT redesign backend authentication.

---

# Objectives

Implement a production-ready frontend authentication flow.

The system must support:

- login page
- login form submission
- login success handling
- token/session persistence
- current user bootstrap on app startup
- logout
- unauthorized redirect handling
- auth-aware route entry

The UI must remain consistent with:

- Tailwind CSS
- shadcn/ui
- Tailark Mist-style design language

---

# Required Components

---

# 1 Login Page

Create or migrate a login page using the current frontend design system.

Suggested location:

src/pages/auth/LoginPage.vue

The page should include:

- login_name input
- password input
- submit button
- loading state
- error feedback
- minimal calm internal-tool layout

Use a Mist-style auth page direction.

Do not over-design it like a marketing page.

---

# 2 Authentication API Integration

Integrate the login page with the existing backend login API.

Expected flow:

1. user enters login_name and password
2. frontend calls POST /api/auth/login
3. frontend receives token or session response
4. frontend stores auth state
5. frontend loads current user info
6. frontend redirects into the system

Do not redesign the backend API contract.

Use the existing backend response shape.

---

# 3 Auth State Store

Implement or complete a frontend auth store.

Suggested location:

src/stores/authStore.ts

The auth store must manage:

- token
- current user
- roles
- permissions
- login status
- loading state

The store must support:

- set token after login
- clear token on logout
- restore auth state on page refresh
- bootstrap current user by calling /api/auth/me

---

# 4 App Bootstrap Flow

Implement auth-aware app startup behavior.

When the app loads:

1. read token/session from storage
2. if token exists, call GET /api/auth/me
3. populate auth store
4. load permissions for route and menu control
5. if bootstrap fails, clear auth state and redirect to login

This must integrate with the existing permission-aware frontend.

---

# 5 Route Guard Integration

Extend route handling so protected pages require authentication.

Requirements:

- unauthenticated users are redirected to login
- authenticated users can access protected routes
- permission guard remains compatible with auth guard
- login page should not require authentication

Suggested route guard behavior:

- no token -> redirect to login
- token exists but /api/auth/me fails -> clear auth and redirect
- token valid but permission missing -> redirect to dashboard or forbidden page

Do not redesign routing architecture unnecessarily.

---

# 6 Logout Flow

Implement logout behavior.

The frontend must support:

- clearing token/session from storage
- clearing auth store
- redirecting to login page
- resetting permission-aware UI state

If backend logout API exists, use it.
If not, implement safe frontend logout and document the current limitation.

---

# 7 Error and State Handling

Handle at least the following cases:

- invalid username/password
- disabled user
- backend unavailable
- login loading state
- expired token
- bootstrap failure on refresh
- forbidden page access

The UI must show calm, enterprise-style feedback.

Avoid raw browser errors.

---

# 8 Layout and Visual Design

The login page must fit the current design system.

Requirements:

- Tailwind + shadcn/ui + Mist style
- calm whitespace
- clear form hierarchy
- minimal decoration
- readable error feedback
- visually consistent with the new system shell

If the app already has a global layout system, the login page may use a separate auth layout.

---

# 9 Header / User Entry Integration

Once authenticated, the app shell should show basic current-user information in the header or account area.

At minimum support:

- display_name
- logout action

If role display already exists or is useful, show it in a clean way.

Do not redesign the full header system beyond what is needed.

---

# 10 Documentation

Create:

docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md

The document must include:

1. login page structure  
2. login API integration flow  
3. auth store design  
4. app bootstrap flow  
5. route guard behavior  
6. logout flow  
7. error handling strategy  
8. compatibility with backend authentication and RBAC

---

# Constraints

Do not redesign backend authentication.

Use the auth APIs and permission context already provided by backend.

Do not invent a second auth model.

Keep code and comments in English.

Keep UI style consistent with Tailwind + shadcn + Mist.

Keep implementation modular and production-oriented.

---

# Completion Criteria

The task is complete when:

1. login page exists and works
2. login API integration works
3. token/session is stored and restored correctly
4. current user bootstrap works on app startup
5. protected routes require authentication
6. logout works
7. permission-aware frontend remains compatible
8. docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md exists and is up-to-date