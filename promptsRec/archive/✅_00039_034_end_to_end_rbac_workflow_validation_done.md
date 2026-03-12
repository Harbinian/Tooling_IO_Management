Primary Executor: Claude Code
Task Type: Validation & Consistency Review
Stage: 034
Goal: Perform end-to-end validation of authentication, RBAC, organization scope, and core tool IO workflows, then produce a structured validation report and issue list.
Execution: RUNPROMPT

---

# Context

The project has already completed or is completing:

- RBAC design
- RBAC database schema
- RBAC initial data
- architecture index
- user authentication system
- organization structure module
- RBAC permission enforcement
- frontend permission visibility control
- organization-scoped order data access
- login page and auth flow UI

At this stage, the platform layer and business layer must be validated together as one integrated system.

This task is NOT for adding new features.
This task is for end-to-end validation, consistency review, and issue identification.

---

# Required References

Read before validating:

docs/ARCHITECTURE_INDEX.md  
docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/RBAC_INIT_DATA.md  
docs/ORG_STRUCTURE_IMPLEMENTATION.md  
docs/RBAC_PERMISSION_ENFORCEMENT.md  
docs/FRONTEND_PERMISSION_VISIBILITY.md  
docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md  
docs/AI_DEVOPS_ARCHITECTURE.md  
docs/PRD.md  
docs/ARCHITECTURE.md  

Also inspect relevant backend and frontend implementation files.

---

# Core Task

Validate the integrated system end to end.

The validation must cover:

1. authentication
2. current-user loading
3. RBAC permission resolution
4. frontend permission-based visibility
5. organization-scoped data access
6. order creation workflow
7. keeper confirmation workflow
8. final confirmation workflow
9. notification record visibility
10. Feishu trigger access control if already available

The result must be a structured validation report plus a clear issue list.

---

# Required Work

## A. Authentication Validation

Validate:

- login works with valid credentials
- invalid credentials are rejected correctly
- disabled users are rejected correctly if supported
- current user endpoint works after login
- logout works
- page refresh restores auth state correctly if designed that way

Check both backend behavior and frontend experience.

---

## B. RBAC Permission Validation

Validate that permission enforcement works consistently across:

- menu visibility
- button visibility
- page access
- backend API access

At minimum verify permissions related to:

- dashboard:view
- tool:search
- order:create
- order:submit
- order:list
- order:view
- order:keeper_confirm
- order:final_confirm
- notification:view
- notification:send_feishu
- admin:user_manage
- admin:role_manage

Do not assume all permissions are fully wired unless validated.

---

## C. Organization Scope Validation

Validate organization-aware access behavior.

At minimum test scenarios for:

- SELF scope
- ORG scope
- ORG_AND_CHILDREN scope
- ASSIGNED scope if already implemented
- ALL scope

Validate that users cannot improperly access orders outside allowed scope.

Check:

- order list filtering
- order detail access
- keeper action access
- final confirmation access where relevant

---

## D. Business Workflow Validation

Validate the core business flow under authenticated and permission-controlled conditions:

1. log in as valid role
2. search tool
3. create order
4. submit order
5. keeper processes order
6. final confirmation
7. notification record visibility
8. Feishu action visibility and protection if already implemented

The validation must confirm that platform controls and business logic work together.

---

## E. Role Scenario Validation

Validate at least these role scenarios if test users/data exist:

- Team Leader
- Keeper
- Planner
- System Administrator
- Auditor

For each role, validate:

- what pages are visible
- what actions are visible
- what APIs are allowed
- what data scope is visible

If real test users do not yet exist, document the gap clearly and validate as much as possible from current configuration.

---

## F. Consistency Review

Review whether the following are internally consistent:

- RBAC design vs backend implementation
- RBAC design vs frontend visibility rules
- organization model vs data scope filtering
- auth flow vs route guard behavior
- role-permission mapping vs actual page/action access

Record all inconsistencies.

---

## G. Issue Classification

For all discovered problems, classify issues by severity:

Critical  
High  
Medium  
Low  

For each issue include:

- summary
- affected layer
- probable root cause
- recommended next action
- whether it should become a bug prompt

Do NOT directly implement fixes in this task unless the issue is trivial and clearly within validation cleanup scope.
Primary purpose is validation and reporting.

---

## H. Documentation

Create:

docs/END_TO_END_RBAC_WORKFLOW_VALIDATION.md

This document must include:

1. validation scope
2. validation scenarios
3. role-based results
4. auth flow results
5. permission results
6. organization scope results
7. workflow results
8. consistency findings
9. issue list with severity
10. recommended next actions

---

# Constraints

1. Do not redesign architecture in this task.
2. Do not introduce new features.
3. Focus on validation, consistency, and issue discovery.
4. Keep findings grounded in actual behavior.
5. Keep code comments and technical notes in English.
6. Be explicit about anything not validated due to missing data or environment limitations.

---

# Completion Criteria

The task is complete when:

1. end-to-end validation is performed across auth, RBAC, org scope, and workflow
2. role-based behavior is reviewed
3. inconsistencies are documented
4. issues are classified by severity
5. docs/END_TO_END_RBAC_WORKFLOW_VALIDATION.md exists