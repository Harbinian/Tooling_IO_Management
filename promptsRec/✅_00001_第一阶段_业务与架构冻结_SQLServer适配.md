You are acting as the Chief Software Architect for this project.

Your task is to generate the architecture baseline for a module called:

Tool Inventory Inbound/Outbound Management System.

Important:
Do NOT generate implementation code.
This phase focuses only on business and architecture design.

---

# System Context

This is an internal manufacturing management module.

The system manages the inbound and outbound lifecycle of manufacturing tools.

Users include:

- Team Leaders (request initiators)
- Tool Keepers (warehouse managers)
- Transport Operators (forklift / crane workers)

---

# Technology Stack

Backend:
Python + FastAPI

Database:
SQL Server

Database Access Strategy:

This project inherits existing database CRUD scripts from other internal systems.

Important constraints:

1. Reuse existing database CRUD patterns whenever possible.
2. Do NOT redesign a new persistence layer from scratch.
3. Avoid ORM-first assumptions unless they match the inherited system.
4. Prefer incremental integration with existing DB utilities.

Frontend:
Vue3 + Element Plus

Notification:
Feishu Webhook

Architecture:
Single monolithic service.

---

# Project Scale

Internal enterprise tool.

Expected usage:

- <100 concurrent users
- <100k tool records
- single SQL Server instance

Avoid over-engineering.

Do NOT introduce:

- microservices
- message queues
- workflow engines
- distributed transactions

---

# V1 Scope

Focus on core workflow only.

Outbound flow:

1. Team leader creates outbound request
2. System generates structured request text
3. Keeper confirms tool location and availability
4. System generates transport notification
5. Notification sent via Feishu
6. Transport happens offline
7. Initiator confirms outbound completion

Inbound flow:

1. Team leader creates inbound request
2. Keeper confirms tool condition and location
3. Keeper confirms inbound completion

Important rule:

Outbound completion → confirmed by initiator  
Inbound completion → confirmed by keeper

---

# Modeling Requirements

The system MUST follow these modeling principles:

1. Order + Order Items structure

Example tables:

tool_io_order  
tool_io_order_item  

Each order may include multiple tools.

2. Separate state machines

order_status  
tool_status  
item_status  

3. All operations must be auditable.

Every action must record:

operator  
timestamp  
order_id  
previous_state  
next_state  

4. Notifications must be persistent.

Feishu notification results must be stored.

5. Structured text generation must exist for:

Keeper request text  
Transport notification text  
WeChat copy text  

---

# Deliverables

Generate exactly two documents:

docs/PRD.md  
docs/ARCHITECTURE.md  

Do not generate DB schema or APIs yet.

---

# docs/PRD.md must include

1. System overview  
2. Roles definition  
3. Business workflows  
4. Outbound workflow  
5. Inbound workflow  
6. Completion conditions  
7. Business rules  
8. Exception scenarios  
9. V1 scope  
10. Future extensions  

---

# docs/ARCHITECTURE.md must include

1. System architecture overview  
2. Module boundaries  
3. State machine design

Define:

order_status  
tool_status  
item_status  

4. Data flow

User → API → Service → DB CRUD layer → SQL Server → Notification → Logs

5. Audit logging design

6. Notification architecture

7. Concurrency handling

8. Error handling strategy

9. Inherited database access constraints

Add a section explaining how the module integrates with inherited SQL Server CRUD scripts.

---

# Output format

Use clean Markdown.

Output exactly two files:

docs/PRD.md  
docs/ARCHITECTURE.md  

Do not output extra commentary.