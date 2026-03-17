Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 019
Goal: Migrate the keeper processing page to the new Tailwind CSS + shadcn/ui + Tailark Mist visual system while preserving the existing keeper workflow and API integration.
Execution: RUNPROMPT

---

# Context

The project has already completed:

- frontend UI foundation migration
- order list UI migration
- order detail UI migration planning or implementation
- keeper confirmation workflow at the business logic level

The next step is to migrate the keeper processing page into the new UI system.

This page is operationally critical because it is used by the keeper to process pending orders and confirm item-level information.

Important:

Do NOT redesign the keeper business workflow.
Do NOT change backend APIs.
Do NOT invent unsupported fields or actions.

---

# Required References

Read before implementing:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md
docs/FRONTEND_UI_COMPONENT_MAP.md
docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md
docs/ORDER_LIST_UI_MIGRATION.md
docs/ORDER_DETAIL_UI_MIGRATION.md
docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md
docs/PRD.md
docs/ARCHITECTURE.md
docs/API_SPEC.md

Also inspect the current keeper processing page, related routes, API wrappers, and shared components.

---

# Core Task

Migrate the keeper processing page to the new Tailwind + shadcn/ui + Mist-style visual system.

The page must continue to support the real keeper workflow:

1. load pending orders
2. open one order
3. inspect tool items
4. confirm keeper-side values
5. submit keeper confirmation

The result should feel structured, calm, and highly usable for internal operations.

---

# Required Work

## A. Rebuild the Page Layout

Refactor the keeper processing page into the new layout system.

Recommended direction:

- split operational workspace
- clean master-detail structure
- Mist-style spacing and hierarchy
- practical internal-tool layout

A suggested structure is:

- left side: pending order list
- right side: selected order processing detail

If the existing layout already follows this pattern, preserve the logic but migrate the visual system.

---

## B. Pending Order List Area

Redesign the pending order list area.

This section should make it easy to scan and select orders waiting for keeper action.

Each list entry should clearly show available fields such as:

- order identifier
- order type
- initiator
- project or usage context
- current status
- created time

Use the actual available response structure instead of assumptions.

The list must feel readable and operationally efficient.

---

## C. Keeper Processing Detail Area

Redesign the selected order detail area.

This section should clearly display:

- order basic information
- selected tool items
- item-level keeper confirmation fields
- remarks area if supported
- confirmation actions

The page must not feel like a raw admin form.
It should feel like a focused operational processing workspace.

---

## D. Tool Item Confirmation UI

Redesign the item-level confirmation experience.

For each item, the UI should support keeper-side review and editable confirmation values where the current workflow allows.

Potential categories include:

- current location
- confirmed location
- current status
- confirmed status
- keeper remarks
- availability result

Use the actual fields already supported by the current backend and schema.

Do NOT invent unsupported item fields.

---

## E. Status and Workflow Visibility

Make the current processing state visually clear.

Requirements:

- order-level status is clearly visible
- item-level processing state is readable if supported
- the keeper understands what still requires confirmation

Use Mist-style status badges, section headers, or step indicators as appropriate.

---

## F. Action Area

Refactor the action area for keeper operations.

Possible actions may include:

- confirm
- reject
- save draft state if already supported
- return to list

Only implement actions already supported by the backend workflow.

The action area must be visually clear and easy to use.

---

## G. Empty / Error / Loading States

Implement improved states for:

- no pending orders
- no selected order
- order detail loading
- keeper confirmation request failure
- no item data

Use calm Mist-style operational empty states.

---

## H. Compatibility

Preserve:

- current route behavior
- current keeper API integration
- current business logic
- current response structure

Do NOT redesign backend behavior.

---

# Required Files

Update the appropriate files related to keeper processing.

Typical targets may include:

src/pages/tool-io/KeeperProcess.vue
src/components/mist/*
src/components/ui/*
src/layout/*
src/api/toolIO.js

Follow the actual project structure if it differs.

---

# Required Documentation

Create:

docs/KEEPER_PROCESS_UI_MIGRATION.md

This document must include:

1. layout redesign summary
2. pending order list design
3. processing detail area design
4. item-level confirmation UI strategy
5. action area design
6. empty/error/loading state handling
7. compatibility notes with current APIs

---

# Constraints

1. Do not change backend APIs.
2. Do not invent unsupported fields.
3. Do not change workflow semantics.
4. Keep the UI practical for internal enterprise use.
5. Use Tailwind + shadcn/ui + Mist-style structure consistently.
6. Preserve current page functionality while improving presentation.

---

# Completion Criteria

The task is complete when:

1. the keeper processing page uses the new UI system
2. pending orders remain functional
3. keeper detail processing remains functional
4. item-level confirmation UI is improved
5. empty/error/loading states are improved
6. docs/KEEPER_PROCESS_UI_MIGRATION.md exists   