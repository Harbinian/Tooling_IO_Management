Primary Executor: Codex
Task Type: Backend + Frontend Integration
Stage: 013
Goal: Implement the order submission workflow using real database schema without assuming fixed field names.
Execution: RUNPROMPT

---

# Context

The project is implementing a Tool Inventory IO Management System.

The previous stages already completed:

- tool master search integration using 工装身份卡_主表
- tool search dialog with real SQL Server data
- selected tool table in the order creation page

The system can now search tools and select them.

The next step is to implement the first real business workflow:

Create and submit a tool IO order.

Important constraint:

DO NOT assume specific database field names.
All field usage must be derived from actual database schema inspection.

---

# Required References

docs/PRD.md  
docs/ARCHITECTURE.md  
docs/AI_DEVOPS_ARCHITECTURE.md  
docs/TOOL_MASTER_FIELD_MAPPING.md  
docs/TOOL_SEARCH_DB_INTEGRATION.md  

Inspect the current database through the backend connection.

---

# Core Task

Implement the order submission workflow that allows the user to:

1. create an order
2. attach selected tools
3. submit the order
4. store the order in the database

The implementation must be based on the actual database schema.

---

# Required Work

## A Inspect Database Schema

Using the existing database connection:

1. identify tables related to tool IO or workflow
2. inspect table structures
3. determine which tables can store order data
4. determine which tables can store tool-order relationships

If such tables do not exist, propose a minimal extension that fits the current schema style.

Document the findings.

---

## B Determine Logical Entities

From the schema, derive logical entities such as:

- order header
- order item (tool list)
- order status
- audit log

Do not assume specific column names.
Use schema inspection to determine how they should be mapped.

---

## C Backend Implementation

Implement order submission backend logic.

Requirements:

1. receive order data from frontend
2. validate selected tools
3. insert order header
4. insert tool list records
5. return order identifier

Use the existing DatabaseManager style.

Do NOT redesign the database layer.

---

## D Frontend Integration

Update the order creation page so that:

1. selected tools are included in submission payload
2. the form can submit an order
3. success response shows the generated order number
4. error states are handled properly

Keep the UI consistent with current Element Plus usage.

---

## E Status Initialization

When an order is first submitted, initialize a workflow status.

The exact status values must be derived from:

- database schema
- PRD workflow definition

Do not invent arbitrary status fields if the schema already defines them.

---

## F Documentation

Create:

docs/ORDER_SUBMISSION_IMPLEMENTATION.md

Include:

- tables used
- schema inspection summary
- logical entity mapping
- API endpoint description
- request payload structure
- response structure

---

# Constraints

1. Do not hardcode field names.
2. Always derive fields from database schema.
3. Do not modify 工装身份卡_主表 logic.
4. Keep SQL Server compatibility.
5. Preserve existing backend architecture.
6. Keep code and comments in English.

---

# Completion Criteria

The task is complete when:

1. the order creation page can submit an order
2. the backend stores order data in the database
3. selected tools are linked to the order
4. an order identifier is returned
5. docs/ORDER_SUBMISSION_IMPLEMENTATION.md exists