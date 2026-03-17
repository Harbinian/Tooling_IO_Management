Primary Executor: Codex
Task Type: Frontend Implementation
Stage: 010
Goal: Implement the tool search dialog component for batch tool selection in the Tool IO frontend.
Execution: RUNPROMPT

---

# Context

The project is already using the AI development workflow and existing project rules.

You must follow the existing project development rules and architecture documents.

Required references:

docs/PRD.md  
docs/ARCHITECTURE.md  
docs/API_SPEC.md  
docs/FRONTEND_DESIGN.md  
docs/README_AI_SYSTEM.md  
docs/AI_DEVOPS_ARCHITECTURE.md  

Frontend stack:

Vue3  
Element Plus  

This task is part of the Tool Inventory Inbound/Outbound Management System.

The current UI already includes:

- order creation page
- selected tool table area
- structured message preview area

But the core tool selection capability is still incomplete.

This task focuses only on implementing the reusable tool search dialog and its integration with the order creation page.

---

# Task

Implement a reusable frontend component for tool search and batch selection.

The component must support:

1. searching tools
2. displaying tool list
3. multiple selection
4. returning selected tools to the parent page
5. preventing duplicate additions
6. integration with the current order creation page

Do NOT redesign the whole page.
Do NOT modify unrelated modules.

---

# Required Files

Implement or update files under the frontend project.

Recommended target files:

src/components/tool-io/ToolSearchDialog.vue  
src/api/toolIO.js  
src/pages/tool-io/OrderCreate.vue  

If the existing project structure differs, follow the current project structure but keep the component reusable.

---

# Functional Requirements

## 1. Dialog Component

Create a reusable dialog component:

ToolSearchDialog.vue

The dialog must include:

- keyword input
- optional filter fields if supported by existing API
- search button
- reset button
- tool result table
- multiple selection
- confirm button
- cancel button

The dialog should open from the order creation page.

---

## 2. Search Fields

The dialog must support search conditions aligned with the project docs and existing UI expectations.

At minimum include:

- tool code
- tool name
- specification or model
- location
- status

If the existing API only supports keyword search, use that API and keep the UI fields aligned with the actual API capability.

Do NOT invent unsupported backend fields.

---

## 3. Tool Result Table

The result table must display at least:

- tool code
- tool name
- drawing number
- specification/model
- location
- status

Use Element Plus table.

Support multi-select rows.

---

## 4. Batch Selection Return

When the user clicks confirm:

- return selected rows to the parent page
- append them into the selected tool list
- prevent duplicate tool entries
- keep data structure consistent with the selected tool table already shown on the order creation page

If the same tool is selected twice, do not insert a duplicate row.

---

## 5. Parent Page Integration

Update the order creation page so that:

- clicking the existing "搜索工装" button opens the dialog
- selected tools are inserted into the "已选工装" table
- the selected tool count updates correctly
- deleting a selected tool from the parent table works correctly

Do NOT break existing form fields.

---

## 6. API Integration

Use existing API wrapper style.

Implement or update frontend API methods in:

src/api/toolIO.js

Use the existing tool search API defined in docs/API_SPEC.md.

If needed, create a method such as:

searchTools(params)

Do NOT invent a new endpoint unless it already exists in API_SPEC.md.

---

## 7. UX Requirements

The component should be practical for internal enterprise use.

Requirements:

- clear table layout
- easy multi-selection
- search and reset actions visible
- confirm and cancel buttons obvious
- loading state supported during API requests
- empty state shown when no data is returned

Use Element Plus standard components.

Do NOT over-design the UI.

---

## 8. Error Handling

Handle API failures gracefully.

Use Element Plus message feedback for:

- search failure
- data load failure
- invalid selection state if relevant

Do NOT leave silent failures.

---

## 9. Reusability

The component must be reusable for future inbound/outbound order flows.

Avoid hardcoding page-specific assumptions into the dialog.

Use props and emits where appropriate.

Suggested interface idea:

Props:
- visible

Emits:
- update:visible
- confirm

Use the current project coding style if already established.

---

# Constraints

1. Follow existing project rules and architecture documents.
2. Use English for code, comments, variables, and component logic.
3. Do not add placeholder code.
4. Do not rewrite unrelated frontend pages.
5. Do not invent backend fields or endpoints.
6. Keep changes minimal, safe, and production-oriented.
7. Read existing files before modifying them.
8. Preserve current working UI behavior.

---

# Required Deliverable

Also create a short implementation note:

docs/TOOL_SEARCH_DIALOG_IMPLEMENTATION.md

It must include:

- files created or updated
- API method used
- selected tool return structure
- duplicate prevention logic
- any limitations or assumptions

---

# Completion Criteria

The task is complete when:

1. the tool search dialog component exists
2. it can search tools through the existing API
3. it supports multiple selection
4. selected tools can be inserted into the order creation page
5. duplicate additions are prevented
6. the order creation page still works
7. docs/TOOL_SEARCH_DIALOG_IMPLEMENTATION.md exists