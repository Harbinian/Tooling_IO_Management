Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 016
Goal: Implement the new frontend UI foundation using Tailwind CSS + shadcn/ui + Tailark Mist design language, replacing the Element Plus visual system while preserving existing functionality.
Execution: RUNPROMPT

---

# Context

The project has completed the UI design planning stage in:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md  
docs/FRONTEND_UI_COMPONENT_MAP.md  

The next step is to implement the actual UI foundation that will support the new design system.

The target stack is:

- Tailwind CSS
- shadcn/ui
- Tailark Mist design style

The goal is **not yet full page migration**, but to build the **UI system infrastructure** that future pages will use.

The existing business logic and API integration must remain intact.

Do NOT break:

- order submission
- order list loading
- tool search dialog
- backend API interaction

---

# Required References

Read before implementing:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md  
docs/FRONTEND_UI_COMPONENT_MAP.md  
docs/PRD.md  
docs/ARCHITECTURE.md  

Also inspect the current frontend structure.

---

# Core Task

Implement the frontend UI foundation layer so that the application can transition from Element Plus style to Tailwind + shadcn/ui + Mist style.

This includes:

1. Tailwind configuration
2. shadcn/ui setup
3. core UI primitives
4. Mist-style layout blocks
5. global layout system
6. non-breaking integration with existing pages

---

# Required Work

## A Install and Configure Tailwind CSS

Install Tailwind dependencies if not already present.

Configure:

tailwind.config.js  
postcss.config.js  

Ensure Tailwind is properly integrated with the Vite build system.

Tailwind must support:

- responsive layout
- typography utilities
- spacing scale
- color tokens suitable for Mist-style UI

---

## B Initialize shadcn/ui

Initialize shadcn/ui within the project.

Configure component directory:

src/components/ui/

Generate or implement base components such as:

button  
card  
input  
textarea  
dialog  
badge  
table  
tabs  
dropdown-menu  
tooltip  

Ensure components use Tailwind utilities.

---

## C Create Mist Design Blocks

Create a Mist-style component layer.

Directory:

src/components/mist/

Implement reusable blocks inspired by Tailark Mist.

Examples:

mist-stats  
mist-features  
mist-steps  
mist-timeline  
mist-empty  
mist-filter-sidebar  

Each component should follow these principles:

- minimal visual noise
- generous whitespace
- thin separators
- clear hierarchy

Use shadcn primitives and Tailwind styling internally.

---

## D Create Global Layout System

Implement a reusable layout structure.

Directory:

src/layout/

Create layouts such as:

MainLayout.vue  
SidebarLayout.vue  
DashboardLayout.vue  

The layout must support:

- left navigation sidebar
- top header
- main content container
- responsive behavior

Do NOT redesign routing structure unless necessary.

---

## E Add Dashboard Entry Page

Create a new dashboard page to validate the new UI system.

Suggested location:

src/pages/dashboard/DashboardOverview.vue

Use:

mist-stats  
mist-features  

Display example metrics such as:

- today's outbound orders
- pending keeper confirmations
- in-transport orders
- completed orders

These values can use placeholder API calls or existing endpoints.

---

## F Maintain Compatibility

Existing pages must remain functional during the migration.

Do NOT remove Element Plus components yet.

The system must temporarily support both:

- existing Element Plus pages
- new Tailwind + shadcn pages

The migration will happen gradually in later prompts.

---

# Required Documentation

Create:

docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md

Document:

1. Tailwind setup
2. shadcn/ui initialization
3. Mist component layer
4. layout system design
5. dashboard implementation
6. compatibility strategy with existing pages

---

# Constraints

1. Do not remove existing Element Plus pages yet.
2. Do not break existing API integrations.
3. Do not redesign business logic.
4. Keep the codebase clean and modular.
5. Keep naming consistent with existing frontend conventions.
6. Follow the Mist design language principles.

---

# Completion Criteria

The task is complete when:

1. Tailwind CSS is fully configured
2. shadcn/ui components are available
3. Mist component layer exists
4. layout system is implemented
5. dashboard page renders successfully
6. existing pages still function
7. docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md exists