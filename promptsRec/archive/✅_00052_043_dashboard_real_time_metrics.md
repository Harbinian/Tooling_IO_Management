Primary Executor: Gemini
Task Type: Feature Implementation
Stage: 043
Goal: Implement the real-time dashboard metrics and visual overview so users can quickly understand the current state of tool IO operations and workflow progress.
Execution: RUNPROMPT

---

# Context

The Tooling IO Management System already supports:

- tool search
- order creation and workflow
- keeper confirmation
- transport workflow
- final confirmation
- RBAC permission control
- organization scope
- notification system
- audit logging
- tool location management

However the dashboard currently does not fully reflect real operational metrics.

The dashboard must become the operational overview page for daily work.

Users should immediately understand:

- how many orders are active
- which steps require action
- how many tools are currently in transport
- whether there are pending confirmations

This task implements a structured real-time dashboard.

---

# Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md  
docs/PRD.md  
docs/API_CONTRACT_SNAPSHOT.md  
docs/TRANSPORT_WORKFLOW_STATE.md  
docs/TOOL_LOCATION_MANAGEMENT.md  
docs/RBAC_DESIGN.md  

Also inspect:

- existing dashboard-related backend queries
- dashboard components already used in frontend
- Mist UI layout used by the current dashboard page

---

# Core Task

Implement a dashboard that provides real-time operational metrics.

The dashboard must aggregate data from the order workflow and display operational indicators.

It should be optimized for internal operations rather than marketing-style visualization.

---

# Part 1 — Dashboard Metrics Design

Define key metrics that reflect system activity.

At minimum include:

today_outbound_orders

today_inbound_orders

orders_pending_keeper_confirmation

orders_in_transport

orders_pending_final_confirmation

active_orders_total

These metrics must be derived from real workflow data.

---

# Part 2 — Backend Metrics API

Implement backend API(s) to serve dashboard metrics.

Example conceptual endpoint:

GET /api/dashboard/metrics

The response should contain aggregated metrics for the current user scope.

If RBAC organization scope applies, the metrics must respect data visibility rules.

Do not bypass RBAC.

---

# Part 3 — Aggregation Queries

Implement efficient database queries for the metrics.

Examples may include:

count orders by status

count orders by creation date

count orders currently in transport

count orders awaiting confirmation

Ensure queries are optimized and do not create heavy load.

Reuse existing dashboard query logic if already present.

---

# Part 4 — Frontend Dashboard Components

Use the Mist-style UI blocks already adopted in the project.

Recommended layout:

statistics cards for key metrics

feature grid for quick navigation

clean whitespace layout

Avoid complex charts unless necessary.

The dashboard must remain simple and operational.

---

# Part 5 — Data Refresh Strategy

Ensure dashboard metrics remain reasonably up to date.

Options may include:

refresh on page load

manual refresh button

periodic polling if already supported by the frontend framework

Avoid overly aggressive refresh frequency.

---

# Part 6 — RBAC Compatibility

Dashboard metrics must respect RBAC and organization scope.

Examples:

team leader sees only their organization's orders

keeper sees orders they are responsible for

admin may see global metrics

Ensure backend queries enforce data scope.

---

# Part 7 — Quick Access Actions

Include shortcut actions from the dashboard.

Examples:

create new outbound order

create inbound order

open order list

open tool search

These actions should be displayed using Mist-style feature blocks.

---

# Part 8 — Error Handling

If metrics cannot be loaded:

display safe fallback UI

show user-friendly error message

avoid breaking the dashboard layout

---

# Part 9 — Validation

Verify the dashboard displays correct metrics in these scenarios:

no active orders

multiple pending confirmations

active transport operations

multiple organizations with scoped users

Verify numbers match actual database state.

---

# Part 10 — Documentation

Create:

docs/DASHBOARD_REAL_TIME_METRICS.md

The document must include:

dashboard metric definitions

backend aggregation logic

RBAC filtering behavior

frontend layout structure

refresh strategy

validation scenarios

---

# Constraints

1. Do not redesign existing workflow logic.
2. Do not bypass RBAC scope rules.
3. Keep UI aligned with Tailwind + shadcn + Mist style.
4. Prefer simple operational visualization over complex charts.
5. Keep code and comments in English.

---

# Completion Criteria

The task is complete when:

dashboard metrics API exists

frontend dashboard displays metrics

metrics respect RBAC scope

metrics update correctly based on real workflow data

docs/DASHBOARD_REAL_TIME_METRICS.md exists and is up to date with the latest metrics definitions