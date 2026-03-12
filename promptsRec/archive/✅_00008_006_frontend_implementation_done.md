Primary Executor: Codex

Task Type: Frontend Implementation

Goal:
Implement the frontend pages for the Tool Inventory Inbound/Outbound Management System according to the frontend design document.

---

# Context

The project already contains:

docs/PRD.md
docs/ARCHITECTURE.md
docs/API_SPEC.md
docs/FRONTEND_DESIGN.md

The frontend design document is the authoritative specification for page structure and interaction behavior.

Do NOT redesign the UI.
Follow the design document strictly.

---

# Technology Stack

Frontend Framework:
Vue3

UI Library:
Element Plus

Build Tool:
Vite

Backend:
FastAPI

API style:
REST

---

# Implementation Scope

Implement the following frontend pages:

1. Order Creation Page
2. Keeper Processing Page
3. Order List Page
4. Order Detail Page

---

# Project Structure

Create a clean frontend structure.

Recommended layout:

frontend/
  src/
    api/
    components/
    pages/
    router/
    store/
    utils/

Pages should be stored under:

src/pages/tool-io/

Example:

src/pages/tool-io/
  OrderCreate.vue
  OrderList.vue
  OrderDetail.vue
  KeeperProcess.vue

---

# API Integration

Use API definitions from:

docs/API_SPEC.md

Implement API calls for:

POST /tool-io-orders
GET /tool-io-orders
GET /tool-io-orders/{id}

POST /tool-io-orders/{id}/submit
POST /tool-io-orders/{id}/keeper-confirm
POST /tool-io-orders/{id}/notify-transport
POST /tool-io-orders/{id}/final-confirm

POST /tool-io-orders/{id}/reject
POST /tool-io-orders/{id}/cancel

GET /tools/search
POST /tools/batch-query

Create API wrapper files inside:

src/api/

Example:

src/api/toolIO.js

---

# Page Requirements

## 1. Order Creation Page

File:

OrderCreate.vue

Functions:

- order type selector
- tool search
- batch selection
- selected tool list
- usage purpose input
- project input
- target location input
- structured text preview
- submit order

Tool search must support:

- tool code
- tool name
- specification
- location
- status

Batch selection must allow adding multiple tools into one order.

---

## 2. Keeper Processing Page

File:

KeeperProcess.vue

Functions:

- load order details
- confirm tool locations
- confirm tool status
- add keeper remarks
- preview transport notification
- send Feishu notification
- copy WeChat notification text
- approve order
- reject order

The page must support processing multiple tool items.

---

## 3. Order List Page

File:

OrderList.vue

Functions:

- search orders
- filter by order type
- filter by status
- filter by initiator
- filter by keeper
- pagination
- quick action buttons

Columns must include:

order number
order type
initiator
keeper
status
created time
actions

Status must use Element Plus tag components.

---

## 4. Order Detail Page

File:

OrderDetail.vue

Functions:

- show order information
- show tool items
- show order timeline
- show audit logs
- show notification records
- show structured text blocks
- show action buttons based on order state

---

# UI Behavior

## Status Display

Display order states clearly using tags.

Example states:

draft
submitted
keeper_confirmed
partially_confirmed
transport_notified
completed
rejected
cancelled

Each state should have a different color.

---

## Button Visibility

Buttons must appear based on:

current order state
current user role

Examples:

Submit → only for draft

Keeper Confirm → only for keeper when status=submitted

Notify Transport → after keeper confirmation

Final Confirm → initiator for outbound / keeper for inbound

Reject → keeper only during review

Cancel → initiator before confirmation

---

# Structured Text UX

The system must display structured message text for:

1. Keeper request message
2. Transport notification
3. WeChat copy message

Users must be able to:

preview text
copy text

Use copy-to-clipboard buttons.

---

# Component Suggestions

Reusable components should include:

ToolSearchDialog.vue
ToolSelectionTable.vue
OrderStatusTag.vue
NotificationPreview.vue

Place them in:

src/components/tool-io/

---

# Data Handling

Use Vue reactive state management.

Example:

ref
reactive
computed

Avoid unnecessary global state unless needed.

---

# Error Handling

Handle API errors gracefully.

Show error messages using Element Plus message component.

Example:

ElMessage.error("Operation failed")

---

# Completion Criteria

The task is complete when:

1. All four pages exist
2. API wrappers exist
3. components are reusable
4. pages compile without errors
5. basic interactions work with API calls
6. structured text preview and copy UX works
7. status tags display correctly
8. button visibility rules work as expected