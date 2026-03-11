Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 020
Goal: Migrate the order creation page to the new Tailwind CSS + shadcn/ui + Tailark Mist visual system while preserving the existing order submission workflow and tool selection integration.
Execution: RUNPROMPT

---

# Context

The project has already completed:

- frontend UI foundation migration
- order list UI migration
- order detail UI migration
- keeper processing UI migration
- tool search dialog with real backend integration
- order submission workflow at the business logic level

The next step is to migrate the order creation page into the new UI system.

This page is one of the most important workflow pages because it is where users:

- create outbound or inbound orders
- search and select tools
- review selected tools
- enter usage information
- submit the order

Important:

Do NOT redesign the business workflow.
Do NOT change backend APIs.
Do NOT invent unsupported fields.

---

# Required References

Read before implementing:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md
docs/FRONTEND_UI_COMPONENT_MAP.md
docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md
docs/TOOL_MASTER_FIELD_MAPPING.md
docs/TOOL_SEARCH_DB_INTEGRATION.md
docs/ORDER_SUBMISSION_IMPLEMENTATION.md
docs/PRD.md
docs/ARCHITECTURE.md
docs/API_SPEC.md

Also inspect the current order creation page, tool search dialog, selected tool table, API wrappers, and shared layout/components.

---

# Core Task

Migrate the order creation page to the new Tailwind + shadcn/ui + Mist-style visual system.

The page must continue to support the real business workflow:

1. choose order type
2. enter order form data
3. search tools
4. select multiple tools
5. review selected tools
6. submit the order

The result should feel clean, structured, and efficient for internal operations.

---

# Required Work

## A. Rebuild the Page Layout

Refactor the order creation page into the new layout system.

Recommended direction:

- Mist-style form page
- calm two-column or sectioned layout
- strong hierarchy between form area, selected tool area, and action area
- practical operational spacing

The page must not feel like a dense raw admin form.

---

## B. Order Form Area

Redesign the order form area.

The form must clearly support the existing fields already used by the current workflow, such as:

- order type
- project or usage context
- target location
- planned usage time
- planned return time
- remarks

Use the actual current form fields from the codebase and API workflow.

Do NOT invent new business fields without support.

The form should feel structured and easy to scan.

---

## C. Tool Search Entry

Redesign the tool search entry area.

The page must continue to support the current tool search dialog integration.

Requirements:

- clear "search tool" entry point
- clean visual relationship between order form and tool selection
- new visual style consistent with Mist language

Do NOT break the existing dialog open behavior.

---

## D. Selected Tool Area

Redesign the selected tool area.

This area must clearly show the tools already selected for the order.

It should support the current selected-tool data structure and operations such as:

- display selected tools
- remove selected tool
- show core tool information
- reflect selection count if already supported

Use the actual available fields rather than assumptions.

The presentation should be clean and readable.

---

## E. Submission Area

Refactor the order submission area.

The page must support:

- submit order
- show loading during submission
- show success feedback
- show error feedback

If the current workflow returns an order number after submission, display it clearly using the new UI style.

---

## F. Visual Hierarchy

The page should emphasize these three layers clearly:

1. order basic information
2. selected tools
3. final submission action

The user should never feel lost about what step they are currently performing.

Use spacing, section cards, subtle separators, and Mist-style visual rhythm to make this clear.

---

## G. Empty / Error / Loading States

Implement improved states for:

- no selected tools
- tool search not started
- submission in progress
- submission failure
- validation errors

Use Mist-style calm empty states and feedback blocks.

Do not leave raw empty areas.

---

## H. Compatibility

Preserve:

- current route behavior
- current order submission API integration
- current tool search dialog integration
- current selected tool return behavior
- current backend request format

Do NOT redesign backend behavior.

---

# Required Files

Update the appropriate files related to order creation.

Typical targets may include:

src/pages/tool-io/OrderCreate.vue
src/components/tool-io/ToolSearchDialog.vue
src/components/tool-io/ToolSelectionTable.vue
src/components/mist/*
src/components/ui/*
src/layout/*
src/api/toolIO.js

Follow the actual project structure if it differs.

---

# Required Documentation

Create:

docs/ORDER_CREATE_UI_MIGRATION.md

This document must include:

1. layout redesign summary
2. order form redesign
3. tool search entry redesign
4. selected tool area redesign
5. submission area strategy
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

1. the order creation page uses the new UI system
2. existing form fields remain functional
3. tool search dialog integration remains functional
4. selected tools render correctly
5. order submission remains functional
6. empty/error/loading states are improved
7. docs/ORDER_CREATE_UI_MIGRATION.md exists and is up-to-date