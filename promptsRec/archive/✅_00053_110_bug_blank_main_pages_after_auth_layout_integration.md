Primary Executor: Gemini
Task Type: Bug Fix
Category: Frontend Layout / Routing / Auth Integration
Goal: Diagnose and fix the issue where Dashboard, Order List, New Order, and Keeper Workspace render as blank content areas after authentication and layout integration.
Execution: RUNPROMPT

---

# Context

After recent authentication, RBAC, layout, and frontend integration work, the application shell renders successfully:

- login works
- authenticated user card is visible
- left navigation is visible
- top header is visible

However, the main content pages are blank for:

- Dashboard
- Order List
- New Order
- Keeper Workspace

This indicates that the overall app shell loads, but route-level page content is not rendering correctly.

This is a bug, not a feature request.

The issue likely involves one or more of:

- router-view mounting
- page component rendering
- auth/bootstrap state timing
- route guards
- permission gating
- content container styling
- silent runtime errors
- blank fallback rendering

---

# Required References

Read before making changes:

docs/ARCHITECTURE_INDEX.md
docs/API_CONTRACT_SNAPSHOT.md
docs/FRONTEND_PERMISSION_VISIBILITY.md
docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md
docs/RBAC_DESIGN.md
docs/RBAC_PERMISSION_ENFORCEMENT.md
docs/DASHBOARD_REAL_TIME_METRICS.md if it exists

Also inspect relevant frontend files, including but not limited to:

- App.vue
- main layout files
- router configuration
- auth store
- permission utility
- permission route guard
- Dashboard page
- Order List page
- Order Create page
- Keeper Workspace page
- sidebar / shell layout components

---

# Core Task

Diagnose and fix the bug where authenticated main pages render as blank content areas.

The final result must ensure:

1. route content mounts correctly inside the layout
2. dashboard content renders
3. order list content renders
4. new order page renders
5. keeper workspace renders
6. permission checks remain correct
7. authenticated app shell continues to work

Do NOT redesign the app.
This is a focused bug-fix task.

---

# Required Work

## A. Reproduce and Inspect the Failure

Inspect the current frontend runtime path for these pages:

- Dashboard
- Order List
- New Order
- Keeper Workspace

Check for:

- route matching
- nested router-view rendering
- auth bootstrap timing
- permission guard logic
- page-level conditional rendering
- content container visibility / CSS collapse
- silent catch blocks or fallback returns

Use the real current codebase rather than assumptions.

---

## B. Inspect Router and Layout Integration

Determine whether the issue is caused by:

1. the layout shell mounting correctly but child pages not being injected
2. route guard redirect loops or aborted navigation
3. permission-aware route filtering removing page content
4. a missing or misplaced router-view
5. nested routes not matching expected paths

Confirm the actual rendering chain from:

router
→ layout
→ page component

---

## C. Inspect Auth and Permission State Timing

Check whether the page content depends on auth state that may not be ready when the page first renders.

Possible failure modes:

- auth store not initialized before route render
- permission list empty during first render
- page returns null/empty state instead of loading state
- guard allows route but page body blocks itself

If this is a timing problem, apply a minimal safe fix.

---

## D. Inspect Page-Level Rendering Guards

Review the Dashboard, Order List, New Order, and Keeper Workspace pages for:

- permission checks
- store readiness checks
- API loading checks
- blank-state fallback logic
- render conditions that may incorrectly return empty content

Do not remove valid RBAC behavior.
Fix only the incorrect logic producing blank content.

---

## E. Inspect Network-Dependent Rendering

Check whether these pages stay blank because their data-loading path fails silently.

Pay attention to APIs such as:

- /api/auth/me
- /api/dashboard/metrics
- /api/tool-io-orders
- any page bootstrap endpoint used by the layout or auth store

If data fetch fails, the UI should not collapse into unexplained blank content.

Implement safe loading/error states if needed.

---

## F. Inspect CSS / Layout Visibility Issues

Check whether the content exists in the DOM but is visually hidden by layout or styling.

Possible causes include:

- zero-height container
- overflow clipping
- absolute positioning mistakes
- hidden class
- incorrect flex/grid sizing
- wrong min-height/max-height behavior

Fix only what is necessary to restore visible content.

---

## G. Preserve Existing Behavior

The fix must preserve:

- authentication flow
- left sidebar navigation
- current-user display
- top header
- RBAC menu visibility
- route protection

Do not weaken authentication or permission logic just to make pages render.

---

## H. Documentation

Create:

docs/BUG_BLANK_MAIN_PAGES_AFTER_AUTH_LAYOUT_INTEGRATION.md

This document must include:

1. observed symptom
2. confirmed root cause
3. affected layers
4. fix applied
5. pages verified
6. remaining edge cases if any

---

# Constraints

1. Do not redesign the routing architecture unless absolutely required.
2. Do not remove RBAC checks globally.
3. Do not remove authentication guards.
4. Apply the smallest safe fix necessary.
5. Keep code and comments in English.
6. Preserve the current UI direction and layout shell.

---

# Completion Criteria

The task is complete when:

1. Dashboard renders visible content
2. Order List renders visible content
3. New Order renders visible content
4. Keeper Workspace renders visible content
5. auth shell remains intact
6. permission logic still works
7. docs/BUG_BLANK_MAIN_PAGES_AFTER_AUTH_LAYOUT_INTEGRATION.md exists