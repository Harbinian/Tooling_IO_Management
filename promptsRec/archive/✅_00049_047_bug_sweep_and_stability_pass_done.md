Primary Executor: Claude Code
Task Type: Stability Validation
Stage: 047
Goal: Perform a full-system bug sweep and stability validation across backend, frontend, RBAC, workflow, and integrations before pilot release.
Execution: RUNPROMPT

---

Context

The Tooling IO Management System is approaching release readiness.

Major capabilities already implemented include:

authentication and login flow  
RBAC permission enforcement  
organization structure and scoped data access  
tool search  
order lifecycle workflow  
keeper confirmation  
transport workflow  
final confirmation  
notification framework  
Feishu notification adapter  
operation audit logs  
tool location management  
real-time dashboard metrics  
API contract snapshot  
backend modular refactor  
Trae token optimization

At this stage the system must undergo a comprehensive bug sweep and stability pass.

The purpose is to identify hidden defects, edge cases, and inconsistencies before pilot release.

This task focuses on validation and remediation planning rather than feature expansion.

---

Required References

Read before starting:

docs/ARCHITECTURE_INDEX.md  
docs/API_CONTRACT_SNAPSHOT.md  
docs/RELEASE_PREPARATION_AND_GO_LIVE_CHECKLIST.md  
docs/OPERATION_AUDIT_LOG_SYSTEM.md  
docs/NOTIFICATION_SERVICE_FRAMEWORK.md  
docs/FEISHU_NOTIFICATION_ADAPTER.md  
docs/TRANSPORT_WORKFLOW_STATE.md  
docs/TOOL_LOCATION_MANAGEMENT.md  
docs/DASHBOARD_REAL_TIME_METRICS.md  
docs/RBAC_DESIGN.md  

Also inspect backend routes, service modules, and frontend UI components.

---

Core Task

Conduct a full-system stability sweep.

This includes:

functional verification  
permission validation  
workflow consistency checks  
integration reliability checks  
UI interaction checks  
error-handling verification

The goal is to identify defects and classify them into actionable bug tasks.

---

Part 1 — Authentication and RBAC Validation

Verify:

login flow works correctly

invalid credentials are rejected

RBAC permission checks are consistently enforced

protected APIs return appropriate responses

frontend hides actions without permission

organization-scoped data access behaves correctly

---

Part 2 — Workflow Stability

Validate the full workflow sequence:

create order  
submit order  
keeper confirm  
transport start  
transport complete  
final confirmation  

Verify that:

state transitions are valid

invalid transitions are rejected

workflow state is persisted correctly

location updates remain consistent

audit logs are generated for each transition

---

Part 3 — Notification Reliability

Verify:

notification records are generated correctly

Feishu adapter handles success and failure correctly

notification failure does not break workflow

notification status updates are recorded

---

Part 4 — Dashboard Accuracy

Verify that dashboard metrics reflect actual system state.

Check:

pending keeper confirmations

orders in transport

orders awaiting final confirmation

today's inbound and outbound counts

active order totals

Ensure metrics respect RBAC and organization scope.

---

Part 5 — UI Stability

Inspect frontend pages including:

dashboard  
order list  
order detail  
tool search dialog  
keeper workflow views  
transport workflow views  

Verify:

no console errors

correct API usage

proper loading and error states

permission-based UI rendering

---

Part 6 — Error Handling

Verify behavior when errors occur:

database failure

invalid workflow action

RBAC denial

Feishu send failure

unexpected state transition

The system should log the error but remain stable.

---

Part 7 — Issue Classification

All detected problems must be categorized:

Critical  
High  
Medium  
Low  

Each issue must include:

description  
affected module  
probable cause  
recommended fix  

Only generate bug prompts where appropriate.

Avoid duplicate bug tasks.

---

Part 8 — Stability Report

Create the document:

docs/SYSTEM_STABILITY_SWEEP_REPORT.md

Include:

summary of validation scope

validated subsystems

identified issues

severity classification

recommended remediation actions

pilot release readiness assessment

---

Constraints

Do not redesign the system in this task.

Do not implement major new features.

Focus on defect discovery and stability evaluation.

Keep technical notes and code references in English.

---

Completion Criteria

The task is complete when:

system-wide validation has been performed

all issues are documented

issues are classified by severity

docs/SYSTEM_STABILITY_SWEEP_REPORT.md exists

the system is assessed for pilot release readiness and documented in docs/RELEASE_PREPARATION_AND_GO_LIVE_CHECKLIST.md if needed