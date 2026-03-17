Primary Executor: Gemini
Task Type: Frontend Design
Stage: 015
Goal: Redesign the frontend UI from Element Plus style to Tailwind CSS + shadcn/ui + Tailark Mist design language, while preserving the current business workflow and information architecture.
Execution: RUNPROMPT

---

# Context

The project is a Tooling IO Management System.

The current frontend has already implemented core business pages and flows, but the visual style is still based on the existing Element Plus-oriented UI.

The new target is:

- Tailwind CSS
- shadcn/ui
- Tailark Mist design language

The goal is to significantly improve UI/UX while preserving business clarity and operational efficiency.

Important:

This task is currently focused on frontend design and structure planning, not full backend redesign.

Do NOT change the business workflow.
Do NOT change database assumptions.
Do NOT invent unsupported backend capabilities.

---

# Required References

Read before designing:

docs/PRD.md
docs/ARCHITECTURE.md
docs/FRONTEND_DESIGN.md
docs/README_AI_SYSTEM.md
docs/AI_DEVOPS_ARCHITECTURE.md
docs/ORDER_SUBMISSION_IMPLEMENTATION.md
docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md if it exists

Also inspect the current frontend pages and layout structure.

---

# Core Goal

Redesign the frontend visual system and page structure using:

- Tailwind CSS
- shadcn/ui
- Tailark Mist-style components and layout language

The redesign must preserve:

- order creation workflow
- order list workflow
- keeper processing workflow
- order detail / workflow tracking
- login / permission entry
- empty / error states

---

# Design Principles

Use the following principles consistently:

1. Minimal visual noise
2. Thin borders and light structure
3. Large whitespace and calm layout rhythm
4. Strong readability for internal operational use
5. Better perceived quality without sacrificing efficiency
6. Clear hierarchy for workflow-heavy screens

Do NOT create flashy marketing-style pages.
This remains an internal operations system.

---

# Target Design System

The new frontend style must be based on:

- Tailwind CSS for layout, spacing, typography, and utility styling
- shadcn/ui for core reusable UI primitives
- Tailark Mist design language for page composition and visual tone

If Tailark Mist blocks are not directly available in code, reproduce their layout and visual logic using Tailwind + shadcn/ui.

---

# Required Scope

## 1 Dashboard Overview

Design a dashboard overview page.

Recommended direction:

- mist-stats style blocks
- mist-features style feature entry grid

Required content:

- today outbound orders
- pending keeper confirmations
- in-transport count
- completed orders
- quick entry points for:
  - outbound order
  - inbound order
  - order list
  - inventory / tool search

The layout should feel spacious, structured, and immediately readable.

---

## 2 Order Management Page

Redesign the order list and filtering page.

Recommended direction:

- documentation-style layout
- clean sidebar filtering
- list as structured operational content, not dense admin table only

Required support:

- keyword search
- order type filter
- order status filter
- initiator filter
- keeper filter
- date range filter if already supported

The page should feel like a high-quality internal operations console.

---

## 3 Order Detail and Workflow Tracking

Redesign the order detail page and workflow tracking section.

Recommended direction:

- Mist-style workflow or step layout
- timeline / changelog-style audit trail
- structured detail sections with strong readability

Required sections:

- order basic information
- tool item list
- workflow progress
- audit / operation log
- notification record area placeholder
- action area

The workflow progress visualization must make the business status very clear.

---

## 4 Authentication Page

Redesign the login / permission entry page.

Recommended direction:

- mist-auth style
- minimal form
- calm enterprise internal-tool tone
- no heavy branding

The page should support role-based internal login scenarios.

---

## 5 Empty States and Error States

Design a consistent system for:

- empty search result
- no pending orders
- no selected tools
- request failure
- permission denied
- backend error state

Recommended direction:

- mist-cta style empty states
- simple explanatory text
- one clear next action

Examples:

- contact admin
- retry
- create new order
- go back to list

---

# Required Deliverables

Create:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md

This document must include:

1. design goals
2. visual system principles
3. page-by-page redesign plan
4. Mist-inspired block mapping
5. Tailwind usage guidelines
6. shadcn/ui component recommendations
7. layout recommendations
8. typography and spacing recommendations
9. empty/error state design rules
10. migration priorities

Also create:

docs/FRONTEND_UI_COMPONENT_MAP.md

This document must map:

current page / component
→ new Tailwind + shadcn/ui + Mist-style replacement strategy

Example categories:

- stats cards
- filter sidebar
- order list container
- workflow tracker
- audit timeline
- auth form
- empty state block

---

# Implementation Planning Requirement

The design output must also include an implementation sequence.

Define which parts should be migrated first.

Recommended priority order should consider:

1. global layout and shell
2. dashboard overview
3. order list page
4. order detail page
5. keeper processing page
6. order creation page
7. auth page
8. empty/error states

If the current project structure suggests a better migration order, document it.

---

# Constraints

1. Do not change business workflow definitions.
2. Do not invent new backend APIs.
3. Do not assume data fields that are not already part of the project.
4. Keep the design practical for internal enterprise use.
5. Keep code-facing naming and planning in English.
6. Preserve operational efficiency while improving quality.
7. Use Mist as a style direction, not as an excuse for visual ambiguity.

---

# Completion Criteria

The task is complete when:

1. docs/FRONTEND_STYLE_MIGRATION_PLAN.md exists
2. docs/FRONTEND_UI_COMPONENT_MAP.md exists
3. all five requested page categories are covered
4. Tailwind + shadcn/ui + Mist-style migration strategy is clearly defined
5. the plan is implementable without changing the core backend workflow