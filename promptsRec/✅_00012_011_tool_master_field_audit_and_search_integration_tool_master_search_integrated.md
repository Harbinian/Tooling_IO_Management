Primary Executor: Codex
Task Type: Backend and Frontend Integration
Stage: 011
Goal: Audit fields from 工装身份卡_主表, identify usable fields for this project, and integrate real database-backed tool search into the tool selection dialog.
Execution: RUNPROMPT

---

# Context

The project is implementing the Tool Inventory Inbound/Outbound Management System.

The current priority is NOT Feishu or WeChat integration.

The current priority is:

1. read real tool data from SQL Server
2. audit the actual fields in 工装身份卡_主表
3. identify which fields are suitable for this project
4. use those fields for tool search and selected-tool display
5. keep future business extension possible

The project already has:

- SQL Server
- pyodbc
- existing DatabaseManager / inherited CRUD style
- frontend tool search dialog UI
- order creation page with selected tool area

Important:
Do NOT invent a new data source.
Start from the real table:

工装身份卡_主表

---

# Required References

Read before implementation:

docs/PRD.md
docs/ARCHITECTURE.md
docs/API_SPEC.md
docs/DB_SCHEMA.md
docs/SQLSERVER_SCHEMA_REVISION.md
docs/FRONTEND_DESIGN.md
docs/README_AI_SYSTEM.md
docs/AI_DEVOPS_ARCHITECTURE.md

Also inspect the existing database module and current frontend files related to:

- tool search dialog
- order creation page
- tool search API

---

# Core Task

Use 工装身份卡_主表 as the source of truth for tool master data.

You must first inspect the actual fields of 工装身份卡_主表 and determine:

1. which fields are actually available
2. which fields are suitable for search
3. which fields are suitable for display in the tool search dialog
4. which fields are suitable for selected tool rows
5. which fields should be reserved for future workflow usage

Do NOT assume the final field set in advance.
Base the implementation on the real schema.

---

# Required Work

## A. Audit the Tool Master Table

Inspect 工装身份卡_主表 and produce a field audit.

Identify at least:

- primary key or unique identifier candidate
- tool code candidate
- tool name candidate
- drawing number candidate
- specification/model candidate
- location candidate
- status candidate
- department / owner candidate
- update time candidate

If there are multiple similar fields, choose the most appropriate one and document the decision.

---

## B. Create a Field Mapping Document

Create:

docs/TOOL_MASTER_FIELD_MAPPING.md

This document must include:

1. all relevant fields discovered from 工装身份卡_主表
2. recommended fields for tool search
3. recommended fields for dialog table display
4. recommended fields for selected-tool rows
5. future-reserved fields for later business use
6. logical English aliases for code usage

Example sections:

- Actual DB Field
- Recommended Business Meaning
- Used In Search
- Used In Dialog Display
- Used In Selected Tool Table
- Reserved For Future

---

## C. Backend Search Integration

Based on the real audited fields, update or complete the tool search backend logic.

Requirements:

1. keep SQL Server compatibility
2. keep existing DatabaseManager / inherited CRUD style
3. do NOT redesign a new persistence layer
4. search logic must use the audited fields from 工装身份卡_主表
5. support the frontend dialog with practical search capability

At minimum, make the backend support:

- keyword search
- location-related filtering if supported by real fields
- status-related filtering if supported by real fields

If the actual schema does not support all UI filters directly, use a practical fallback approach and document it.

---

## D. Frontend Dialog Integration

Integrate the current tool search dialog with real backend data.

Requirements:

1. dialog search must call the real backend search API
2. result table must display the audited usable fields
3. selected tools must be returned to the order creation page
4. duplicate tool selection must be prevented
5. selected tool rows must use the audited field mapping

Do NOT hardcode fake data.

---

## E. Selected Tool Table Alignment

Update the selected tool list in the order creation page so it uses fields that actually exist in 工装身份卡_主表.

Use the audited mapping to decide what should be shown.

Prefer a practical minimal set such as:

- tool code
- tool name
- drawing number
- specification/model
- location

But final selection must follow the real schema.

---

## F. Implementation Notes

Create:

docs/TOOL_SEARCH_DB_INTEGRATION.md

This document must include:

1. backend files updated
2. frontend files updated
3. actual fields used from 工装身份卡_主表
4. search strategy used
5. fallback logic if some UI fields are not directly supported
6. duplicate prevention logic
7. remaining limitations

---

# Constraints

1. Start from 工装身份卡_主表, not from assumptions.
2. Do not invent unsupported fields.
3. Do not redesign the persistence architecture.
4. Keep English for code, comments, variables, and helper names.
5. Keep Chinese physical database field names if already used in SQL.
6. Read existing files before modifying them.
7. Preserve current working UI where possible.
8. Focus on real data integration first, not Feishu or WeChat.
9. Keep changes minimal, safe, and production-oriented.

---

# Completion Criteria

The task is complete when:

1. 工装身份卡_主表 has been audited
2. docs/TOOL_MASTER_FIELD_MAPPING.md exists
3. tool search uses real database fields
4. the frontend dialog can search and display real tool data
5. selected tools can be added into the order creation page
6. duplicate additions are prevented
7. docs/TOOL_SEARCH_DB_INTEGRATION.md exists