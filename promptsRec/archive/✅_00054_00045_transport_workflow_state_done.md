Primary Executor: Codex
Task Type: Feature Implementation
Stage: 041
Goal: Implement the transport workflow state in the tool IO order lifecycle so physical movement of tooling can be tracked between keeper confirmation and final confirmation.
Execution: RUNPROMPT

---

# Context

The Tooling IO Management System workflow currently includes:

Team Leader → create / submit order  
Keeper → confirm tool availability  
Transport Operator → move the tool  
Initiator / Keeper → final confirmation

At the moment, the workflow jumps directly from keeper confirmation to final confirmation.

However in real production environments there is an intermediate state where the tool is physically being transported.

The system must explicitly represent this step.

This task introduces the **transport state** into the order lifecycle.

---

# Required References

Read before implementing:

docs/ARCHITECTURE_INDEX.md  
docs/PRD.md  
docs/API_CONTRACT_SNAPSHOT.md  
docs/NOTIFICATION_SERVICE_FRAMEWORK.md  
docs/FEISHU_NOTIFICATION_ADAPTER.md  
docs/OPERATION_AUDIT_LOG_SYSTEM.md  

Also inspect:

- current order state model
- order services
- audit logging integration
- notification service integration

---

# Core Task

Extend the tool IO order workflow to support transport operations.

The workflow must include a transport stage between keeper confirmation and final confirmation.

This state must allow the system to track when the tool is being moved and who is responsible for the movement.

---

# Part 1 — Order State Model Extension

Add a new state to the order lifecycle.

Example conceptual sequence:

DRAFT  
SUBMITTED  
KEEPER_CONFIRMED  
TRANSPORT_IN_PROGRESS  
TRANSPORT_COMPLETED  
FINAL_CONFIRMED  

Do not break existing states already used in the system.

Update the state transition logic accordingly.

---

# Part 2 — Transport Assignment

Allow the system to capture which transport operator is responsible.

This may include:

transport_operator_user_id

or equivalent reference depending on the current schema.

If the schema already supports responsible operator assignment, reuse it.

If not, extend the model in a minimal and compatible way.

---

# Part 3 — Transport Start Action

Implement an action representing the start of transport.

Example API behavior:

transport operator acknowledges task  
→ order state becomes TRANSPORT_IN_PROGRESS

This action should:

write an audit log  
create notification updates if relevant

---

# Part 4 — Transport Completion Action

Implement a transport completion action.

Example:

transport operator confirms movement completed  
→ order state becomes TRANSPORT_COMPLETED

After this step, the order can proceed to final confirmation.

This action must:

write an audit log  
trigger any required notifications

---

# Part 5 — Notification Integration

When keeper confirms order:

→ transport notification must be generated

Transport operators must be notified that a movement task is pending.

When transport starts or completes:

→ system should optionally notify relevant stakeholders such as:

initiator  
keeper  

Use the existing notification service.

---

# Part 6 — Audit Logging

All transport actions must be recorded through the audit log system.

Actions that must generate audit entries:

transport assigned  
transport started  
transport completed  

Each entry must include:

operator  
timestamp  
order id  
previous status  
new status  

---

# Part 7 — API Exposure

Expose APIs supporting the transport workflow.

Examples may include:

assign transport operator  
start transport  
complete transport  

Ensure these APIs respect RBAC permission checks.

Do not introduce permissions inconsistent with the existing RBAC model.

---

# Part 8 — Frontend Compatibility

Ensure frontend order detail pages can read the new state.

At minimum the frontend must be able to display:

transport pending  
transport in progress  
transport completed  

Do not redesign the full UI in this task unless minimal adjustments are required to reflect the new state.

---

# Part 9 — Validation

Verify that the workflow behaves correctly:

create order  
submit order  
keeper confirm  
transport start  
transport complete  
final confirm  

Verify that:

notifications are generated  
audit logs are written  
RBAC permission checks are respected  

---

# Part 10 — Documentation

Create:

docs/TRANSPORT_WORKFLOW_STATE.md

The document must include:

1. updated order state machine
2. transport responsibilities
3. transport APIs
4. notification integration
5. audit logging behavior
6. workflow examples

---

# Constraints

1. Do not redesign the order schema unnecessarily.
2. Preserve existing workflow logic where possible.
3. Maintain compatibility with notification and audit systems.
4. Keep RBAC permission checks consistent.
5. Keep code and comments in English.

---

# Completion Criteria

The task is complete when:

order lifecycle includes transport state

transport start and completion actions exist

notifications are generated for transport tasks

audit logs are written for transport events

order workflow behaves correctly end to end

docs/TRANSPORT_WORKFLOW_STATE.md exists and is up to date with the latest transport state model, responsibilities, APIs, notification integration, audit logging behavior, and workflow examples