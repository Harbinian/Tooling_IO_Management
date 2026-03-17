Primary Executor: Codex
Task Type: Feature Implementation
Stage: 042
Goal: Implement tool location management so tool positions can be maintained consistently across storage, transport, outbound, and inbound workflow stages.
Execution: RUNPROMPT

---

# Context

The Tooling IO Management System already includes:

- tool master search
- order workflow
- keeper confirmation
- notification framework
- Feishu adapter
- transport workflow state

The database also already includes a location-related table:

工装位置表

At this stage, the system still needs a clear and consistent location management mechanism.

Without explicit location management:

- current location may drift from physical reality
- transport state cannot reliably update tool position
- inbound/outbound completion cannot guarantee final position consistency
- keeper visibility becomes unreliable

This task introduces a unified tool location management capability.

---

# Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md  
docs/PRD.md  
docs/API_CONTRACT_SNAPSHOT.md  
docs/TRANSPORT_WORKFLOW_STATE.md  
docs/OPERATION_AUDIT_LOG_SYSTEM.md  
docs/RBAC_DESIGN.md  

Also inspect:

- tool master related schema
- 工装位置表 structure
- current order workflow services
- current transport state logic
- current tool search fields related to location

---

# Core Task

Implement tool location management so the system can:

1. resolve the current tool location
2. update location during workflow transitions
3. preserve location history through logs or related records
4. keep tool search and order processing aligned with real storage positions

The implementation must use the existing schema where possible.

---

# Part 1 — Inspect Existing Location Model

Inspect the current database schema and determine:

1. what the authoritative current-location field is
2. how 工装位置表 is structured
3. whether tool master data already stores current location directly
4. how location should be updated during workflow transitions
5. what minimal location history is already available from logs

Do not assume fixed field names.
Use the actual schema and current implementation.

---

# Part 2 — Define Location Lifecycle

Define how location changes across the order lifecycle.

At minimum consider these phases:

- storage location before order
- keeper-confirmed pickup location
- transport in progress
- target use location after outbound completion
- return staging location if inbound
- final storage location after inbound completion

Use the current business workflow and existing state machine.

Do not invent unnecessary extra states if the current model already supports the needed transitions.

---

# Part 3 — Current Location Resolution

Implement a reliable way to resolve the current location of a tool.

Possible sources may include:

- tool master current location field
- 工装位置表
- current open workflow state
- transport stage

The system must clearly define which source is authoritative at each stage.

Document the decision.

---

# Part 4 — Location Update Logic

Implement location update logic during relevant workflow transitions.

Examples:

- keeper confirmation may lock the pickup location
- transport completion may update location to target site
- final inbound confirmation may restore or set final storage location

The implementation must ensure location updates are consistent and idempotent where possible.

Do not scatter location writes across unrelated modules without a clear utility or service boundary.

---

# Part 5 — Location Service Module

Create or extend a dedicated location service.

Suggested location:

backend/services/tool_location_service.py

Responsibilities:

- resolve current tool location
- validate location transitions
- update tool location
- support future location history and tracking extensions

Keep the module small and aligned with current backend structure.

---

# Part 6 — Workflow Integration

Integrate location updates into the existing workflow at the correct points.

At minimum review:

- order creation
- keeper confirmation
- transport start
- transport completion
- final confirmation
- inbound completion if present

Only update location at business-valid milestones.

---

# Part 7 — Audit Logging

All important location changes must be recorded through the audit log system.

At minimum record:

- tool identifier
- order identifier if applicable
- operator
- previous location
- new location
- timestamp
- action type

Audit logging must not break the main workflow if logging fails.

---

# Part 8 — Tool Search Consistency

Ensure the tool search and related UI-facing APIs continue to return accurate location information.

This means:

- current tool search results should reflect updated location
- order detail pages should show consistent location values
- keeper and transport steps should not expose contradictory locations

Do not redesign existing search APIs unless required for consistency.

---

# Part 9 — Validation

Validate at least the following scenarios:

1. tool in storage location before order
2. keeper confirms tool from expected pickup location
3. transport moves tool to target location
4. final confirmation reflects correct new location
5. inbound or return flow restores or changes location correctly if already supported

Verify that:

- current location remains consistent
- audit logs are written
- APIs return the expected location values

---

# Part 10 — Documentation

Create:

docs/TOOL_LOCATION_MANAGEMENT.md

The document must include:

1. inspected schema summary
2. authoritative location source rules
3. location lifecycle across workflow states
4. location service design
5. workflow integration points
6. audit logging behavior
7. validation scenarios
8. limitations or assumptions

---

# Constraints

1. Do not redesign the full database model unless clearly necessary.
2. Prefer existing schema and existing location table usage.
3. Do not assume fixed field names without inspection.
4. Preserve existing workflow logic.
5. Keep RBAC and permission behavior consistent.
6. Keep code and comments in English.
7. Keep implementation modular and production-oriented.

---

# Completion Criteria

The task is complete when:

1. tool location can be resolved consistently
2. relevant workflow transitions update location correctly
3. tool search reflects updated location
4. location changes are audit-logged
5. docs/TOOL_LOCATION_MANAGEMENT.md exists and is up to date with the latest location management schema, authoritative source rules, lifecycle, service design, workflow integration points, audit logging behavior, validation scenarios, and limitations or assumptions