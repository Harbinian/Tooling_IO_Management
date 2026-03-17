Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 017
Goal: Migrate the order list page to the new Tailwind CSS + shadcn/ui + Tailark Mist visual system while preserving existing business logic and API integration.
Execution: RUNPROMPT

---

# Context

The project has already completed the frontend UI foundation migration:

- Tailwind CSS
- shadcn/ui
- Tailark Mist-inspired component layer
- global layout system
- dashboard overview foundation

The next step is to migrate the order list page into the new UI system.

The order list page is a high-frequency operational page and must become the first major business page using the new design system.

Important:

Do NOT redesign the order list business workflow.
Do NOT change backend APIs.
Do NOT break existing order list data loading logic.

---

# Required References

Read before implementing:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md
docs/FRONTEND_UI_COMPONENT_MAP.md
docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md
docs/PRD.md
docs/ARCHITECTURE.md
docs/API_SPEC.md

Also inspect the current order list page and related frontend files.

---

# Core Task

Migrate the current order list page from the old Element Plus-oriented UI to the new Tailwind + shadcn/ui + Mist-style layout and components.

The page must keep working with the existing order list API.

---

# Required Work

## A. Rebuild Page Layout

Refactor the order list page into the new layout system.

The page should use:

- MainLayout or the current global layout shell
- Mist-style page spacing
- clean content hierarchy
- lightweight operational styling

Do not keep the old dense admin-panel visual style.

---

## B. Filtering Experience

Redesign the filtering area using the new UI system.

Recommended direction:

- documentation-style filter area
- sidebar filter panel or structured top filter bar
- calm visual hierarchy
- compact but readable arrangement

The page must support the existing filter capabilities already present in the project, such as:

- keyword search
- order type
- order status
- initiator
- keeper
- date-related filters if already supported

Do NOT invent backend filters that do not exist.

---

## C. Order List Presentation

Redesign the list/table area using the new UI stack.

Possible implementation options:

- shadcn-style table
- Mist-inspired structured list container
- hybrid documentation-style operational list

The list must still clearly show core fields such as:

- order number
- order type
- initiator
- keeper
- order status
- created time
- actions

Use the actual current data structure instead of assumptions.

---

## D. Status Display

Improve status visualization.

Requirements:

- use badges, chips, or lightweight Mist-style status markers
- ensure workflow states are clearly distinguishable
- keep internal-tool readability high

Do not use loud or excessive colors.
Use calm and structured visual semantics.

---

## E. Actions Area

Redesign action buttons for each order row.

Possible actions may include:

- view detail
- process
- continue
- confirm
- cancel

Use the actual existing actions already supported by the current workflow.

Do not invent actions without backend support.

---

## F. Empty State and Error State

Implement improved empty and error states.

Support at least:

- no orders found
- filter returns no results
- order list request failed

Use Mist-style empty state principles:

- minimal explanation
- one clear next action
- no clutter

---

## G. Loading State

Improve loading behavior for the order list page.

Use a cleaner loading experience consistent with the new design system.

Possible approaches:

- skeleton blocks
- lightweight shimmer rows
- subtle loading placeholders

Do not leave raw blank tables during loading.

---

## H. Compatibility

Preserve the current order list API integration.

The migrated page must continue to work with:

- the current order list request
- current response structure
- existing route structure

Do NOT redesign backend response format.

---

# Required Files

Update the appropriate files for the order list page.

Typical targets may include:

src/pages/tool-io/OrderList.vue
src/components/mist/*
src/components/ui/*
src/layout/*

Follow the actual project structure if it differs.

---

# Required Documentation

Create:

docs/ORDER_LIST_UI_MIGRATION.md

This document must include:

1. page structure changes
2. filter area redesign
3. list presentation strategy
4. status display strategy
5. empty/error/loading state handling
6. reused UI components
7. compatibility notes with current API

---

# Constraints

1. Do not change backend logic.
2. Do not change order list API contract.
3. Do not remove core filter capabilities.
4. Keep the UI practical for internal enterprise use.
5. Use Tailwind + shadcn/ui + Mist-style structure consistently.
6. Preserve current page functionality while improving presentation.

---

# Completion Criteria

The task is complete when:

1. the order list page uses the new UI system
2. filters remain functional
3. order data renders correctly
4. status display is improved
5. empty/error/loading states are improved
6. docs/ORDER_LIST_UI_MIGRATION.md exists and is up-to-date