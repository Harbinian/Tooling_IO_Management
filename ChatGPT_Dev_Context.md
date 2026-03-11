# Tooling IO Management System — Project Overview

## 1. Project Purpose

The Tooling IO Management System is an internal manufacturing tool management module used to manage the lifecycle of tool usage in production.

The system manages:

- tool outbound requests
- tool inbound returns
- tool location confirmation
- keeper validation
- workflow tracking
- structured notification generation

The immediate development priority is to complete the **core operational workflow**, not external messaging integrations.

---

# 2. Core Business Workflow

## 2.1 Roles

### Team Leader
Responsibilities:

- create outbound or inbound tool orders
- search and select tools
- describe usage scenario
- submit order request
- confirm outbound completion

### Tool Keeper
Responsibilities:

- view pending orders
- confirm tool location
- confirm tool availability
- confirm tool condition
- update order workflow status
- confirm inbound completion

### Transport Operator
Not yet integrated in the system.

Future role:

- receive structured transport instructions
- move tools between locations

---

# 3. Main Business Processes

## 3.1 Outbound Process

```
Team Leader creates order
        ↓
Select tools
        ↓
Submit outbound order
        ↓
Tool Keeper confirmation
        ↓
Transport operation
        ↓
Initiator confirms outbound completion
```

---

## 3.2 Inbound Process

```
Team Leader creates return order
        ↓
Tool Keeper confirms returned tool condition
        ↓
Tool Keeper confirms inbound completion
```

---

# 4. Technology Stack

## Backend

Language:
- Python

Framework:
- Flask-style API server

Database Access:
- pyodbc

Database:
- SQL Server

Architecture:
- DatabaseManager abstraction
- service-layer query logic
- defensive configuration loading

---

## Frontend

Framework:
- Vue 3

UI Library:
- Element Plus

Build System:
- Vite

HTTP Client:
- Axios

---

# 5. AI Development Environment

Development is performed using multiple AI agents:

| Agent | Responsibility |
|------|---------------|
Claude Code | architecture planning |
Codex | backend implementation |
Gemini | frontend design |

Prompt-driven development pipeline is used to coordinate tasks.

---

# 6. Database Architecture

## 6.1 Tool Master Data Source

The system uses the real production table:

```
工装身份卡_主表
```

This table is treated as the **source of truth for tool master data**.

Confirmed tool instance identifier:

```
序列号
```

This field is unique and non-null in the dataset.

---

## 6.2 Business Tables

The following tables are confirmed to exist:

```
工装出入库单_主表
工装出入库单_明细
工装出入库单_操作日志
工装出入库单_通知记录
工装位置表
tool_io_order_no_sequence
```

These tables support the core tool IO workflow.

---

# 7. Backend Structure

Typical backend structure:

```
backend/
│
├─ database.py
├─ web_server.py
│
├─ services/
│   └─ tool_io_service.py
│
└─ config/
    └─ settings.py
```

### database.py
Responsible for:

- SQL Server connection
- configuration loading
- DatabaseManager initialization

### web_server.py
Responsible for:

- API route registration
- request handling
- response serialization

### tool_io_service.py
Responsible for:

- business logic
- order creation
- tool search
- order list queries
- workflow updates

---

# 8. Frontend Structure

Typical structure:

```
frontend/src
│
├─ main.js
├─ App.vue
│
├─ router/
│   └─ index.js
│
├─ api/
│   ├─ http.js
│   └─ toolIO.js
│
├─ pages/tool-io/
│   ├─ OrderCreate.vue
│   ├─ OrderList.vue
│   └─ KeeperProcess.vue
│
└─ components/tool-io/
    ├─ ToolSearchDialog.vue
    └─ ToolSelectionTable.vue
```

---

# 9. Core Implemented Features

## 9.1 Tool Search

The system supports searching real tools from SQL Server.

Frontend:

```
ToolSearchDialog.vue
```

Capabilities:

- keyword search
- tool result table
- multi-selection
- return selected tools to parent page

Backend endpoint:

```
/api/tools/search
```

---

## 9.2 Tool Selection

Users can:

- search tools
- select multiple tools
- append selected tools to order form
- prevent duplicate tool entries

---

## 9.3 Order Submission

Order submission has been implemented.

Capabilities:

- create tool IO order
- attach selected tools
- insert records into database
- generate order identifier

---

# 10. Development Workflow

## Prompt Numbering

Feature prompts:

```
000 – 099
```

Bug fix prompts:

```
100 – 199
```

---

## Bug Workflow Principle

One bug chain must have only one primary bug prompt.

Sub-issues must be documented within the same bug documentation instead of creating additional prompts.

Example:

```
103_bug_order_list_api_500.md
```

---

# 11. AI DevOps Skills

The system includes multiple operational skills.

### RUNPROMPT
Executes development prompts.

### pipeline-dashboard
Shows pipeline state and next task.

### release-precheck
Validates system readiness.

### incident-monitor
Detects runtime anomalies.

### incident-capture
Records incidents.

### bug-triage
Converts incidents into bug prompts.

---

# 12. Current Active Bug

```
103_bug_order_list_api_500
```

Observed issue:

```
GET /api/tool-io-orders
→ 500 Internal Server Error
```

Impact:

- order list page cannot load
- keeper processing workflow blocked

The root cause is currently being investigated in backend logic.

---

# 13. Current System Status

Working:

- SQL Server connection
- tool master search
- backend startup
- order submission
- Vite proxy routing
- frontend tool selection

Incomplete:

- order list API stability
- keeper confirmation workflow
- order detail page
- structured message generation
- final confirmation flow
- notification integration

---

# 14. Next Development Steps

## Step 1
Fix bug:

```
103_bug_order_list_api_500
```

---

## Step 2
Implement keeper confirmation workflow.

Features:

- keeper fetches pending orders
- confirm tool location
- confirm tool status
- update order status
- record operation logs

---

## Step 3
Implement order detail page.

Display:

- order header
- tool list
- workflow status
- operation logs

---

## Step 4
Implement structured message generation.

Generate:

- keeper confirmation message
- transport instruction message

No external integration yet.

---

## Step 5
Implement final workflow confirmation.

Outbound completion:
- confirmed by initiator

Inbound completion:
- confirmed by keeper

---

## Step 6
Integrate notification records.

Use table:

```
工装出入库单_通知记录
```

---

## Step 7
Integrate Feishu notifications.

This will be implemented only after the core workflow is stable.

---

# 15. Development Priority

Current priority order:

```
Fix order list API
        ↓
Implement keeper workflow
        ↓
Order detail page
        ↓
Structured message generation
        ↓
Final confirmation
        ↓
Notification integration
```

---

# 16. Current Development Focus

The project has moved beyond prototype stage and is now operating as a real database-backed workflow system.

Immediate focus:

```
Stabilize order list API
Complete keeper confirmation workflow
Finish full tool IO lifecycle
```

After that, the system will be ready for external notification integration.