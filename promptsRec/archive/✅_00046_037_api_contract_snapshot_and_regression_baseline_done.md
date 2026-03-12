Primary Executor: Claude Code
Task Type: Documentation & Validation Infrastructure
Stage: 037
Goal: Freeze the current backend API contract into a stable snapshot and create a regression baseline so future refactors do not accidentally break frontend integration.
Execution: RUNPROMPT

---

# Context

The project has already completed or is completing:

- core tool IO workflow
- RBAC design and enforcement
- authentication and organization structure
- frontend permission visibility
- backend modular refactor for context efficiency

A major backend refactor has just been introduced.

Even if the API paths and JSON behavior were intended to remain unchanged, the project now needs a formal API contract snapshot to reduce future breakage risk.

This task does NOT introduce new business features.

Its purpose is to:

1. document the current stable API contract
2. record request/response baselines
3. identify contract inconsistencies
4. create a regression reference for future prompts and refactors

---

# Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md
docs/ARCHITECTURE.md
docs/API_SPEC.md if it exists
docs/BACKEND_REFACTOR_CONTEXT_OPTIMIZATION.md if it exists
docs/RBAC_DESIGN.md
docs/RBAC_PERMISSION_ENFORCEMENT.md
docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md

Also inspect the current backend route modules and frontend API wrapper files.

---

# Core Task

Create a stable API contract snapshot for the current system.

The snapshot must cover the APIs that are actively used by the frontend and core workflows.

This task must:

1. inspect real route implementations
2. inspect real frontend API usage
3. reconcile any differences
4. produce a canonical API contract snapshot
5. define a regression baseline for future development

---

# Required Work

## A. Inventory Active APIs

Inspect backend routes and frontend API wrapper usage.

Identify all active APIs used by the current system, including but not limited to:

- authentication
- current user
- tool search
- order creation
- order list
- order detail
- keeper confirmation
- final confirmation
- notification records
- Feishu trigger if currently implemented
- dashboard statistics
- organization APIs
- RBAC-related APIs if exposed

Do not rely only on old docs.
Use the current codebase as the source of truth.

---

## B. Snapshot Request Contracts

For each active API, record:

- method
- path
- required auth status
- required permission if known
- request parameters
- query parameters
- request body shape
- required vs optional fields

Use actual current behavior rather than assumptions.

---

## C. Snapshot Response Contracts

For each active API, record:

- response status codes
- success body structure
- error body structure
- field names used by frontend
- pagination structure if applicable

Pay special attention to APIs used directly by frontend pages.

---

## D. Reconcile Frontend and Backend Usage

Compare:

- backend route implementation
- frontend API wrapper expectations
- page-level field usage

Identify any mismatches such as:

- frontend expecting field names not returned by backend
- backend returning fields no longer used
- inconsistent pagination structure
- inconsistent error structure

Document these mismatches clearly.

Do NOT silently fix them in this task unless they are trivial documentation-only inconsistencies.
Primary goal is snapshot and baseline creation.

---

## E. Define Regression Baseline

Create a regression checklist for future refactors.

At minimum include:

- auth login still works
- current user endpoint still returns roles and permissions
- tool search still returns frontend-required fields
- order list still returns frontend-required pagination and rows
- order detail still returns workflow and item data
- keeper confirm request contract remains stable
- final confirmation contract remains stable

This checklist should be usable by future prompts and release-precheck tasks.

---

## F. Documentation

Create:

docs/API_CONTRACT_SNAPSHOT.md

This document must include:

1. API inventory
2. request contract by endpoint
3. response contract by endpoint
4. permission/auth notes
5. frontend/backend mismatch findings
6. regression baseline checklist

If useful, also create a short companion file:

docs/API_REGRESSION_CHECKLIST.md

only if the checklist becomes too large for the main snapshot document.

---

# Constraints

1. Do not redesign APIs in this task.
2. Do not change frontend behavior in this task.
3. Do not change backend routes unless absolutely required for documentation accuracy.
4. Use the current codebase as source of truth.
5. Keep technical names and notes in English.
6. Keep the result concise, actionable, and suitable for future AI-assisted work.

---

# Completion Criteria

The task is complete when:

1. active APIs are inventoried
2. request/response contracts are documented
3. frontend/backend contract mismatches are identified
4. docs/API_CONTRACT_SNAPSHOT.md exists
5. a regression baseline is available for future refactors
6. the regression checklist is complete and documented in docs/API_REGRESSION_CHECKLIST.md if needed