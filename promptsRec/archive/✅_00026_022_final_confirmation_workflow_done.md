Primary Executor: Codex
Task Type: Backend + Frontend Integration
Stage: 022
Goal: Implement the final confirmation workflow for outbound and inbound orders using the real database schema and existing workflow states.
Execution: RUNPROMPT

---

# Context

The project has already completed or planned:

- tool master search integration
- order submission workflow
- order list loading
- keeper confirmation workflow
- frontend UI migration for major pages
- structured message preview UI

The next business step is to implement the final confirmation workflow.

This workflow must close the core order lifecycle.

Business rules:

- outbound completion is confirmed by the initiator
- inbound completion is confirmed by the keeper

Important constraint:

Do NOT assume fixed database field names.
Inspect the actual schema and current workflow implementation before making changes.

---

# Required References

Read before implementing:

docs/PRD.md
docs/ARCHITECTURE.md
docs/DB_SCHEMA.md
docs/SQLSERVER_SCHEMA_REVISION.md
docs/ORDER_SUBMISSION_IMPLEMENTATION.md
docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md
docs/ORDER_DETAIL_UI_MIGRATION.md
docs/STRUCTURED_MESSAGE_PREVIEW_UI.md
docs/API_SPEC.md
docs/AI_DEVOPS_ARCHITECTURE.md

Also inspect relevant backend and frontend files, including but not limited to:

- web_server.py
- database.py
- backend/services/tool_io_service.py
- order detail page
- keeper processing page
- frontend API wrappers

---

# Core Task

Implement the final confirmation workflow so that:

1. eligible outbound orders can be finally confirmed by the initiator
2. eligible inbound orders can be finally confirmed by the keeper
3. order workflow state is updated to the correct terminal or next state
4. operation logs are written
5. the frontend can trigger and display final confirmation results

This workflow must use the real database schema and current workflow logic.

---

# Required Work

## A. Inspect Existing Workflow State Storage

Using the real schema and current implementation, determine:

1. how order workflow state is stored
2. how order type is stored
3. how current keeper-confirmed state is represented
4. whether item-level completion state exists
5. what fields can store final confirmation metadata

Do not assume exact field names.
Use real schema inspection.

---

## B. Determine Final Confirmation Eligibility

From the current workflow logic, determine the exact conditions under which an order is eligible for final confirmation.

Rules to implement:

- outbound orders must be confirmed by the initiator
- inbound orders must be confirmed by the keeper

Use real current status values and current role logic.
Do not invent a separate parallel workflow.

---

## C. Backend API Implementation

Implement or complete APIs required for final confirmation.

At minimum support:

1. query whether final confirmation is available for a given order
2. submit final confirmation
3. return updated order state

The backend final confirmation logic must:

- validate order existence
- validate role eligibility
- validate workflow state eligibility
- update final confirmation fields
- update order workflow state
- update item-level state if required by current schema
- insert operation logs
- return confirmation result

Follow the existing DatabaseManager style.
Do NOT redesign backend architecture.

---

## D. Frontend Integration

Update the relevant frontend pages so that final confirmation can be performed from the correct context.

Possible pages may include:

- order detail page
- keeper processing page
- order list row actions

Use the actual current UI and workflow placement.

The UI must:

1. show final confirmation action only when valid
2. show different behavior for outbound vs inbound roles
3. display loading, success, and failure feedback
4. refresh workflow status after confirmation

Do NOT expose invalid actions for the wrong role or wrong state.

---

## E. State Transition Handling

Implement the final confirmation state transition using the current real workflow model.

Ensure:

1. outbound confirmation moves to the correct final state
2. inbound confirmation moves to the correct final state
3. no invalid transition is allowed
4. operation logs record previous and next state

Do not invent arbitrary terminal states if current workflow already defines them.

---

## F. Operation Logging

Insert final confirmation logs into the operation log table.

At minimum record:

- order identifier
- operator identifier
- operator role if supported
- action type
- previous state
- next state
- timestamp
- remarks if available

Use the real schema.

---

## G. Documentation

Create:

docs/FINAL_CONFIRMATION_IMPLEMENTATION.md

This document must include:

1. schema inspection summary
2. eligibility rules
3. outbound confirmation rule
4. inbound confirmation rule
5. APIs implemented or updated
6. frontend page integration
7. state transition behavior
8. operation logging behavior
9. any schema limitations or assumptions

---

# Constraints

1. Do not hardcode field names.
2. Always inspect the real schema first.
3. Do not redesign the database architecture.
4. Preserve current submission and keeper-confirmation logic.
5. Keep SQL Server compatibility.
6. Keep code and comments in English.
7. Keep frontend behavior consistent with the current UI migration direction.
8. Keep changes minimal, safe, and production-oriented.

---

# Completion Criteria

The task is complete when:

1. eligible outbound orders can be finally confirmed by initiator
2. eligible inbound orders can be finally confirmed by keeper
3. order workflow state updates correctly
4. operation logs are written
5. frontend action is available only in valid cases
6. docs/FINAL_CONFIRMATION_IMPLEMENTATION.md exists