Primary Executor: Claude Code
Task Type: Validation & Release Preparation
Stage: 044
Goal: Prepare the system for go-live by validating release readiness, consolidating deployment requirements, and producing a structured release checklist with risk assessment.
Execution: RUNPROMPT

---

# Context

The Tooling IO Management System has already completed or is completing:

- tool search
- order workflow
- keeper confirmation
- transport workflow
- final confirmation
- RBAC design and enforcement
- authentication and login flow
- organization structure and scoped data access
- notification framework
- Feishu notification adapter
- audit logging
- tool location management
- real-time dashboard metrics
- backend modular refactor
- API contract snapshot

At this stage, the project should move from feature construction into release preparation.

This task is not for adding major new features.

Its purpose is to determine whether the system is ready for controlled internal release and to identify the remaining gaps, risks, and deployment actions.

---

# Required References

Read before validating:

docs/ARCHITECTURE_INDEX.md
docs/ARCHITECTURE.md
docs/API_CONTRACT_SNAPSHOT.md
docs/END_TO_END_RBAC_WORKFLOW_VALIDATION.md if it exists
docs/OPERATION_AUDIT_LOG_SYSTEM.md
docs/NOTIFICATION_SERVICE_FRAMEWORK.md
docs/FEISHU_NOTIFICATION_ADAPTER.md
docs/TRANSPORT_WORKFLOW_STATE.md
docs/TOOL_LOCATION_MANAGEMENT.md
docs/DASHBOARD_REAL_TIME_METRICS.md
docs/RBAC_DESIGN.md
docs/RBAC_PERMISSION_ENFORCEMENT.md
docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md

Also inspect the current backend and frontend structure, environment configuration patterns, and startup scripts if present.

---

# Core Task

Perform a release preparation review for the current system.

This task must:

1. validate overall release readiness
2. identify missing release requirements
3. consolidate deployment prerequisites
4. produce a go-live checklist
5. classify remaining risks and blockers
6. recommend whether the project is ready for:
   - internal testing release
   - pilot release
   - production release

---

# Required Work

## A. Release Scope Review

Review the currently implemented scope and determine what is actually available for release.

At minimum review:

- authentication and login
- RBAC and permission enforcement
- organization-scoped data access
- order creation
- order list
- order detail
- keeper workflow
- transport workflow
- final confirmation
- notification record flow
- Feishu delivery path
- dashboard metrics
- audit log coverage
- tool location consistency

Identify what is:

- complete
- partially complete
- not release-ready
- optional for first release

---

## B. Deployment Prerequisites

Identify all deployment prerequisites.

At minimum include:

- required environment variables
- SQL Server connectivity requirements
- Feishu configuration requirements
- authentication secret / token configuration
- frontend build requirements
- backend startup requirements
- required seed / initial data
- RBAC bootstrap requirements

Do not invent infrastructure beyond what the project currently uses.
Document the real minimum release prerequisites.

---

## C. Release Readiness Validation

Validate release readiness across these dimensions:

1. Functional completeness
2. Security / authentication
3. RBAC correctness
4. Data scope correctness
5. Workflow state consistency
6. Notification safety
7. Auditability
8. UI availability
9. Environment configuration
10. Operational recoverability

For each dimension, assess:

- Ready
- Needs attention
- Blocked

---

## D. Risk Assessment

Identify release risks and classify them by severity.

Examples may include:

- missing seed data
- missing admin bootstrap
- incomplete route protection
- inconsistent state transition
- notification failure handling gaps
- dashboard metric mismatch
- location state inconsistency
- frontend route/auth edge cases

For each risk include:

- description
- affected layer
- severity
- mitigation recommendation
- release impact

---

## E. Go-Live Checklist

Create a practical checklist for internal deployment.

The checklist must include sections such as:

- database readiness
- RBAC initialization
- auth configuration
- backend startup
- frontend build/deploy
- Feishu config
- smoke tests
- role-based test accounts
- order workflow verification
- notification verification
- rollback / fallback considerations

Keep the checklist operational and concise.

---

## F. Release Recommendation

Based on the findings, provide a clear recommendation:

- not ready
- ready for internal test release
- ready for pilot release
- ready for production release

This recommendation must be grounded in actual implementation status and identified risks.

---

## G. Documentation

Create:

docs/RELEASE_PREPARATION_AND_GO_LIVE_CHECKLIST.md

This document must include:

1. release scope summary
2. implemented capability review
3. deployment prerequisites
4. readiness assessment by dimension
5. risk list with severity
6. go-live checklist
7. release recommendation

If needed, also update or align with any existing release-precheck documentation instead of creating overlapping guidance.

---

# Constraints

1. Do not add major new features in this task.
2. Do not redesign architecture in this task.
3. Focus on readiness assessment and operational preparation.
4. Keep findings grounded in the current codebase and current documents.
5. Keep technical content and notes in English.
6. Be explicit about anything that could not be verified.

---

# Completion Criteria

The task is complete when:

1. release scope is reviewed
2. deployment prerequisites are documented
3. release risks are identified and classified
4. a practical go-live checklist exists
5. docs/RELEASE_PREPARATION_AND_GO_LIVE_CHECKLIST.md exists
6. a clear release recommendation is given based on the assessment of readiness, risks, and prerequisites
7. docs/RELEASE_PREPARATION_AND_GO_LIVE_CHECKLIST.md is up to date with the latest release scope, implemented features, and risk assessments