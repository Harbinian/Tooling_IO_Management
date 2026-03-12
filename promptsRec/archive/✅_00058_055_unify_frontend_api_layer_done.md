Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 055
Goal: Create unified frontend API layer with centralized error handling
Dependencies: None
Execution: RUNPROMPT

---

## Context

Code review found that the frontend lacks a unified API layer. Only `api/adminUsers.js` exists as a dedicated API module. Other pages use inline fetch calls, resulting in:
- Duplicated token injection logic
- No centralized error handling (401 redirect, 500 toast)
- No loading state management
- Inconsistent error messages

## Required References

- `frontend/src/api/adminUsers.js` — existing API pattern
- `frontend/src/pages/tool-io/OrderList.vue` — inline fetch example
- `frontend/src/pages/tool-io/OrderCreate.vue` — inline fetch example
- `frontend/src/pages/tool-io/OrderDetail.vue` — inline fetch example
- `frontend/src/pages/dashboard/DashboardOverview.vue` — inline fetch example
- `frontend/src/store/` — Pinia stores
- `AI_API_CONTRACT_SUMMARY.md` — all API endpoints

## Core Task

Create a centralized API client and per-domain API modules, then migrate all inline fetch calls.

## Required Work

1. Inspect all page components to catalog every inline fetch/axios call
2. Create `frontend/src/api/client.js`:
   - Base URL configuration
   - Automatic Bearer token injection from auth store
   - Response interceptor: 401 → redirect to login, 500 → global error toast
   - Request/response logging in development mode
3. Create domain API modules:
   - `frontend/src/api/auth.js` — login, getCurrentUser
   - `frontend/src/api/orders.js` — all order CRUD and workflow endpoints
   - `frontend/src/api/tools.js` — tool search
   - `frontend/src/api/dashboard.js` — dashboard stats
   - `frontend/src/api/orgs.js` — organization management
4. Migrate all inline fetch calls in page components to use new API modules
5. Add global loading indicator support (optional but recommended)

## Constraints

- Do NOT change any API endpoint paths or parameters
- Do NOT modify backend code
- Maintain existing UI behavior exactly
- Use the same HTTP library already in the project (fetch or axios — check first)
- Follow existing code style in `adminUsers.js`

## Acceptance Tests

- All pages load and function identically to before migration
- 401 response automatically redirects to login page
- 500 response shows user-friendly error message
- No inline fetch/axios calls remain in page components
- Token is automatically included in all API requests

## Completion Criteria

- [ ] `api/client.js` created with interceptors
- [ ] At least 5 domain API modules created
- [ ] All inline fetch calls in pages replaced
- [ ] 401 auto-redirect working
- [ ] 500 error toast working
- [ ] No functional regression in any page
