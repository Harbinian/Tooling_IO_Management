Primary Executor: Codex
Task Type: Bug Fix
Category: Runtime Integration
Goal: Diagnose and fix the tool search request routing issue where the frontend receives HTML instead of JSON.
Execution: RUNPROMPT

---

# Context

The tool search dialog is failing when attempting to search tools.

Observed behavior:

- request URL: /api/tools/search
- response status: 200
- response content-type: text/html
- frontend displays "tool search failed"

This indicates the request is not reaching the backend API and is instead being handled by the frontend development server.

The backend search API was previously verified to work correctly.

Therefore this task focuses on identifying why the frontend request is not reaching the backend and fixing the routing.

---

# Investigation Requirements

Before applying any fix, trace the request path.

You must inspect:

Frontend:

- tool search dialog component
- API wrapper for tool search
- axios or http client configuration
- environment configuration
- Vite development server configuration

Backend:

- route registration for tool search
- backend API prefix
- web server startup configuration

---

# Diagnosis Tasks

Determine:

1. where the frontend constructs the tool search URL
2. whether the request uses a relative path
3. whether the frontend dev server proxy is configured
4. whether the backend endpoint path matches the frontend path
5. whether the request is being intercepted by the dev server
6. whether the frontend expects JSON but receives HTML

Do not assume the cause.
Confirm it from the codebase.

---

# Fix Requirements

After identifying the root cause, apply the minimal safe fix.

The fix must ensure:

1. the frontend request reaches the backend API
2. the backend returns JSON data
3. the search dialog receives a valid response
4. the dialog table can render tool search results

Possible fix areas include:

- Vite proxy configuration
- frontend API baseURL
- axios instance configuration
- request path normalization
- environment configuration

Avoid hardcoding temporary solutions.

---

# Verification

After applying the fix, verify the following:

1. searching tools sends a request to the backend API port
2. response content-type is JSON
3. the dialog table renders tool results
4. selecting tools still works
5. no regression occurs in other APIs

---

# Documentation

Create:

docs/BUG_TOOL_SEARCH_REQUEST_ROUTING.md

Document:

1. observed problem
2. root cause
3. files modified
4. routing fix applied
5. frontend/backend path alignment
6. verification results

---

# Constraints

1. Do not modify working backend search logic.
2. Do not redesign unrelated modules.
3. Apply the smallest fix necessary.
4. Maintain current frontend architecture.
5. Keep code and comments in English.

---

# Completion Criteria

The task is complete when:

1. tool search request reaches backend API
2. response is JSON instead of HTML
3. search dialog successfully displays tool data
4. docs/BUG_TOOL_SEARCH_REQUEST_ROUTING.md exists
5. the bug fix is archived properly in the repository