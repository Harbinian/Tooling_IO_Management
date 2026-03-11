Primary Executor: Gemini

Task Type: Frontend Page Design / Interaction Design / Field Mapping

Goal:
Design the frontend pages and interaction flows for the Tool Inventory Inbound/Outbound Management System.

---

# Context

The project already has the following documents:

docs/PRD.md
docs/ARCHITECTURE.md
docs/DB_SCHEMA.md
docs/API_SPEC.md
docs/TASKS.md

The backend APIs and state machines are defined by those documents.

Your task is to design the frontend based strictly on those documents.

Do NOT invent backend fields, states, or APIs that are not defined in the project docs.

---

# Technology Context

Frontend:
Vue3 + Element Plus

Backend:
FastAPI

Database:
SQL Server

Persistence details are backend concerns and should not affect page design.

---

# Design Scope

Design the following pages:

1. Order Creation Page
2. Keeper Processing Page
3. Order List Page
4. Order Detail Page

The design should focus on:

- information architecture
- interaction flow
- component structure
- status display
- field mapping
- button visibility rules

Do NOT implement backend logic.

---

# Business Context

The system manages manufacturing tool inbound/outbound operations.

Key roles:

- Team Leader
- Tool Keeper
- Transport Operator

Important workflow rules:

Outbound flow:
1. Team leader creates outbound request
2. Keeper confirms tools
3. System generates transport notification
4. Initiator confirms outbound completion

Inbound flow:
1. Team leader creates inbound request
2. Keeper confirms inbound completion

Important completion rules:

Outbound completion → confirmed by initiator  
Inbound completion → confirmed by keeper  

---

# Required Pages

## 1. Order Creation Page

Design a page for team leaders to create inbound/outbound orders.

Must include:

- order type selector
- tool search area
- batch selection area
- selected tool list
- usage purpose / project / time / target location inputs
- structured text preview area
- submit action

Tool search must support:

- tool code
- tool name
- specification / model
- location
- status

Batch selection must be clear and efficient.

---

## 2. Keeper Processing Page

Design a page for tool keepers to process pending orders.

Must include:

- pending order summary
- order item confirmation area
- location confirmation
- tool status confirmation
- remarks input
- transport type selection
- transport notification preview
- Feishu send action
- WeChat copy action
- approve / reject / confirm actions

The page should make it easy to process multiple tool items in one order.

---

## 3. Order List Page

Design a list page for viewing orders.

Must include:

- filters
- keyword search
- order type filter
- order status filter
- initiator / keeper related filters if needed
- list columns
- status tags
- quick actions

The list should help users quickly identify:

- pending orders
- rejected orders
- completed orders
- orders waiting for final confirmation

---

## 4. Order Detail Page

Design a detailed view page.

Must include:

- basic order information
- tool item list
- status timeline
- audit log section
- notification record section
- structured text display
- action buttons based on current state and current role

---

# Required Design Outputs

Generate a frontend design document:

docs/FRONTEND_DESIGN.md

The document must include:

1. Page overview
2. Page-by-page design
3. Component structure suggestions
4. Interaction flow
5. Status display rules
6. Button visibility rules
7. Field mapping table
8. Notes for frontend implementation

---

# Field Mapping Requirement

You MUST provide a clear mapping table:

UI Field -> API Field

Examples:

Order Number -> order_no
Order Type -> order_type
Tool Code -> tool_code
Tool Name -> tool_name
Order Status -> order_status

Do not invent fields not defined in API_SPEC.md.

---

# Status Display Rules

Define how the UI should display order states.

Expected states include values such as:

draft
submitted
keeper_confirmed
partially_confirmed
transport_notified
final_confirmation_pending
completed
rejected
cancelled

For each visible status, explain:

- label text
- where it appears
- whether it affects button visibility

---

# Button Visibility Rules

For each page, define which buttons are visible under which conditions.

Examples:

- Submit button visible only when draft can be submitted
- Keeper confirm button visible only to keeper when order is submitted
- Notify transport button visible only after keeper confirmation
- Final confirm button visible only to initiator for outbound, or keeper for inbound
- Reject button review stage
- Cancel button visible only when allowed by business rules

---

# Structured Text UX

The design must include UX handling for:

1. Keeper request text preview
2. Transport notification preview
3. WeChat copy text

Users should be able to:

- preview text
- copy text
- clearly distinguish different text types

---

# Constraints

1. Do not define new APIs.
2. Do not define new database fields.
3. Do not change state names.
4. Follow project docs as the single source of truth.
5. Focus on clean enterprise internal-tool UX.
6. Keep the design practical, not flashy.

---

# Completion Criteria

The task is complete when:

docs/FRONTEND_DESIGN.md exists

and includes:

- four page designs
- interaction descriptions
- field mapping table
- status display rules
- button visibility rules
- structured text preview/copy UX
