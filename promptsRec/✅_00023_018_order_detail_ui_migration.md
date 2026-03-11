Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 018
Goal: Migrate the order detail page to the new Tailwind CSS + shadcn/ui + Tailark Mist visual system while preserving existing business logic, workflow visibility, and API integration.
Execution: RUNPROMPT

---

# Context

The project has already completed:

- frontend UI foundation migration
- order list UI migration
- real database-backed order workflow foundation

The next step is to migrate the order detail page into the new UI system.

This page is critical because it must clearly show:

- order basic information
- tool item details
- workflow status
- operation logs
- notification record placeholder
- available actions

Important:

Do NOT redesign business workflow.
Do NOT change backend APIs.
Do NOT invent unsupported data fields.

---

# Required References

Read before implementing:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md
docs/FRONTEND_UI_COMPONENT_MAP.md
docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md
docs/ORDER_LIST_UI_MIGRATION.md
docs/PRD.md
docs/ARCHITECTURE.md
docs/API_SPEC.md

Also inspect the current order detail page implementation if it exists, together with related route files, API wrappers, and shared components.

---

# Core Task

Migrate the order detail page to the new Tailwind + shadcn/ui + Mist-style visual system.

The page must keep working with the current backend order detail data and must present workflow-heavy information in a clearer, more structured way.

---

# Required Work

## A. Rebuild the Page Layout

Refactor the order detail page into the new layout system.

The page should use:

- the existing global layout shell
- Mist-style spacing and section rhythm
- strong content hierarchy
- calm internal-tool visual tone

The page should not feel like a dense admin table page.

---

## B. Basic Order Information Section

Create a clean detail header area for core order information.

This section should clearly present data such as:

- order identifier
- order type
- initiator
- keeper
- project or usage context
- created time
- current workflow status

Use the actual available response fields instead of assumptions.

Use cards, definition-style blocks, or structured detail groups consistent with the Mist direction.

---

## C. Workflow Tracking Section

Create a workflow progress section.

Recommended direction:

- Mist-style steps
- lightweight progress tracker
- calm status line or timeline

The section must make the business flow clearly understandable.

It should visually express progression such as:

draft  
submitted  
keeper confirmed  
transport / processing  
completed  

Only use workflow states that actually exist in the current system.

Do NOT invent unsupported statuses.

---

## D. Tool Item Detail Section

Redesign the tool item list area.

This section must present the selected tools belonging to the order in a readable way.

Possible approaches:

- structured table
- grouped detail rows
- Mist-style operational list

The section should support fields such as:

- tool identifier or serial
- tool code
- tool name
- drawing number
- model/spec
- location
- item-level status if available

Use the actual data structure from the current API.

---

## E. Audit / Operation Log Section

Create a dedicated operation log display area.

Recommended direction:

- changelog-like list
- vertical timeline
- Mist-inspired audit trail

Each log entry should clearly show:

- operator
- action
- timestamp
- remarks if available

This section is important for workflow traceability.

---

## F. Notification Record Placeholder

Create a notification record area placeholder in the detail page.

This area does not need full external messaging integration yet, but the page should reserve a clean section for notification-related records if the API already returns them.

If notification data is not yet available, display a proper empty state.

---

## G. Action Area

Refactor the action area.

Possible actions may include:

- process
- confirm
- cancel
- continue
- view next step

Only use actions already supported by the current workflow and backend.

Do NOT invent unsupported actions.

The visual treatment should be clean and structured.

---

## H. Empty / Error / Loading States

Implement improved states for:

- detail data loading
- request failure
- missing order detail
- empty sub-sections such as logs or notifications

Use Mist-style calm explanatory design.

---

## I. Compatibility

Preserve:

- current route behavior
- current detail API integration
- current business logic
- current data structure

Do NOT redesign the backend response format.

---

# Required Files

Update the appropriate files related to the order detail page.

Typical targets may include:

src/pages/tool-io/OrderDetail.vue
src/components/mist/*
src/components/ui/*
src/layout/*
src/api/toolIO.js

Follow the actual project structure if it differs.

---

# Required Documentation

Create:

docs/ORDER_DETAIL_UI_MIGRATION.md

This document must include:

1. layout redesign summary
2. order info section design
3. workflow tracker design
4. tool item section design
5. audit log presentation strategy
6. notification placeholder strategy
7. action area design
8. compatibility notes with current API

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

1. the order detail page uses the new UI system
2. order basic information is clearly presented
3. workflow progress is visually improved
4. tool item details render correctly
5. operation logs are clearly shown
6. empty/error/loading states are improved
7. docs/ORDER_DETAIL_UI_MIGRATION.md exists