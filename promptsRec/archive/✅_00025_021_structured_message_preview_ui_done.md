Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 021
Goal: Implement the structured message preview UI using the new Tailwind CSS + shadcn/ui + Tailark Mist visual system while preserving the current business workflow and preparing for future notification integration.
Execution: RUNPROMPT

---

# Context

The project has already completed:

- frontend UI foundation migration
- order list UI migration
- order detail UI migration
- keeper processing UI migration
- order creation UI migration

The next step is to implement the structured message preview UI.

This feature is important because the business workflow requires automatically generated structured text for operational use, even before Feishu or WeChat integration is enabled.

At this stage, the system should support:

- keeper request message preview
- transport notification preview
- copy-friendly structured text display

Important:

Do NOT implement Feishu integration yet.
Do NOT implement WeChat integration yet.
Do NOT change backend workflow logic.

This task focuses only on UI presentation and preview interaction.

---

# Required References

Read before implementing:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md
docs/FRONTEND_UI_COMPONENT_MAP.md
docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md
docs/ORDER_CREATE_UI_MIGRATION.md
docs/KEEPER_PROCESS_UI_MIGRATION.md
docs/PRD.md
docs/ARCHITECTURE.md
docs/API_SPEC.md

Also inspect current frontend pages related to:

- order creation
- keeper processing
- order detail
- current structured text preview area if it already exists

---

# Core Task

Implement a structured message preview UI using the new Tailwind + shadcn/ui + Mist-style system.

The UI must support operational preview and copy interaction for structured business text.

The result should be readable, calm, and practical for internal enterprise use.

---

# Required Work

## A. Define Preview Areas

Implement structured preview sections for at least the following categories:

1. keeper request message
2. transport notification message
3. copy-ready business message block

These preview blocks may appear in one or more workflow pages depending on the existing project structure.

Do not invent pages that do not exist.
Integrate into the most suitable existing pages.

---

## B. Message Preview Presentation

Design the preview area using the new UI system.

Recommended direction:

- Mist-style content panel
- monospaced or highly readable formatted text area
- subtle border and whitespace structure
- clear section title and message type label

The preview should feel like a professional internal communication block, not a raw textarea dump.

---

## C. Copy Interaction

Provide a copy-to-clipboard interaction for each structured message block.

Requirements:

- clear copy button
- visible feedback after copy
- no visual clutter
- consistent with the current UI system

Do not implement external send actions yet.

---

## D. Placement Strategy

Place the message preview UI where it best matches the current workflow.

Possible pages include:

- order creation page
- keeper processing page
- order detail page

Use the real business flow and current UI structure to decide placement.

The preview should appear where users naturally need to review and copy the message.

---

## E. Empty / Loading / Error States

Handle the following states:

- no structured message available yet
- generation pending
- preview data missing
- preview load failure

Use Mist-style calm empty and feedback states.

---

## F. Typography and Readability

The structured message content must be easy to copy and easy to scan.

Use spacing, line grouping, and typography rules that support:

- operation-oriented reading
- quick copy
- minimal ambiguity

The preview must not feel cramped.

---

## G. Compatibility

Preserve:

- current backend API contract
- current workflow semantics
- current page routing
- current data loading logic

If structured message data is not yet fully provided by backend, implement a UI structure that can receive current available data and remain ready for future integration.

Do NOT invent unsupported backend APIs.

---

# Required Files

Update the appropriate frontend files.

Typical targets may include:

src/pages/tool-io/OrderCreate.vue
src/pages/tool-io/KeeperProcess.vue
src/pages/tool-io/OrderDetail.vue
src/components/mist/*
src/components/ui/*

Follow the actual project structure if it differs.

---

# Required Documentation

Create:

docs/STRUCTURED_MESSAGE_PREVIEW_UI.md

This document must include:

1. preview area placement
2. message block presentation strategy
3. copy interaction design
4. empty/error/loading state handling
5. compatibility notes for future Feishu / WeChat integration

---

# Constraints

1. Do not implement Feishu integration yet.
2. Do not implement WeChat integration yet.
3. Do not change backend APIs.
4. Do not invent unsupported workflow states.
5. Keep the UI practical for internal enterprise use.
6. Use Tailwind + shadcn/ui + Mist-style structure consistently.
7. Preserve current page functionality while improving presentation.

---

# Completion Criteria

The task is complete when:

1. structured message preview UI exists
2. preview blocks are clearly presented
3. copy interaction works
4. empty/error/loading states are handled
5. docs/STRUCTURED_MESSAGE_PREVIEW_UI.md exists and is up-to-date