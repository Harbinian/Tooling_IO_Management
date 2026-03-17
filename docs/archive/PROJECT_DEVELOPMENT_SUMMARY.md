# Tooling IO Management System
Project Development Summary

## 1. Project Overview

The Tooling IO Management System is an internal manufacturing management module used to manage tooling inventory movement and workflow.

The system manages the lifecycle of tooling movement including:

- tooling outbound
- tooling inbound
- keeper confirmation
- transport coordination
- final confirmation
- audit logging
- notification tracking

The system integrates:

- SQL Server database
- RBAC permission model
- internal tooling identity database
- Feishu notification integration (planned)
- internal logistics coordination

---

# 2. Current Technology Stack

## Backend

Language
Python

Framework
Flask

Database
SQL Server

Core modules

backend/database  
backend/services  
web_server.py

Key responsibilities

database layer  
business service layer  
API layer  

---

## Frontend

Framework

Vue 3

UI stack

Tailwind CSS  
shadcn/ui  
Mist design style

Structure

frontend/src/pages  
frontend/src/components  
frontend/src/api  

Main pages

Dashboard  
OrderList  
OrderCreate  
OrderDetail  
KeeperWorkspace  

---

## AI Development Infrastructure

The project uses AI-assisted development with multiple models.

Claude Code  
Codex  
Gemini (design related tasks only)

Development orchestration is done through a prompt pipeline.

promptsRec/active  
promptsRec/archive  

Skills are used to coordinate development tasks.

---

# 3. Core System Modules

## Tool Identity System

Based on the existing tooling master database.

Important attributes include:

tool name  
tool drawing number  
tool model  
revision version  
location  
availability status  
validity status  
inbound/outbound status  

---

## Tool IO Order System

Core entity

Tool IO Order

Includes

order header  
order detail  
workflow status  
audit logs  
notification records  

---

## Workflow State

Current workflow concept

Draft  
Submitted  
Keeper Confirmed  
Transport In Progress  
Arrived  
Final Confirmation  
Closed  

Actual state definitions will be finalized during business truth alignment.

---

## Role Model

The system is based on RBAC.

Main roles

System Administrator  
Team Leader  
Keeper  
Planner  
Transport Operator  
Auditor  

Roles determine

page visibility  
operation permissions  
data access scope  

---

# 4. Database Layer

Key tables currently exist

工装出入库单_主表  
工装出入库单_明细  
工装出入库单_操作日志  
工装出入库单_通知记录
工装出入库单_位置  
tool_io_order_no_sequence  

RBAC tables

sys_user  
sys_role  
sys_permission  
sys_user_role_rel  
sys_role_permission_rel  
sys_org  

---

# 5. Frontend Architecture

Pages

Dashboard  
OrderList  
OrderCreate  
OrderDetail  
KeeperWorkspace  
Login  

Dialogs

ToolSearchDialog  

Shared components

tables  
forms  
buttons  
filters  

---

# 6. Debug Infrastructure

A Debug ID Overlay system was implemented.

Purpose

allow precise UI element identification during debugging.

Example DebugIDs

C-FIELD-014  
C-BTN-002  
D-CARD-003  

Features

admin-only visibility  
hover labels  
debug mode toggle  

Future enhancement

DebugID → component locator

---

# 7. Current Development Status

Completed

database connection  
tool search integration  
tool master field alignment  
frontend tool search dialog  
debug ID overlay  
SQL Server schema creation  
basic RBAC schema  

In progress

RBAC role assignment  
admin account management page  

Pending

multi-role workflow validation  
transport operator workflow  
notification integration (Feishu)  
automated E2E tests  

---

# 8. Known Technical Debt

database.py is large and will require modular refactoring.

service layer needs domain separation.

frontend pages require component-level decomposition.

RBAC assignment UI is still under development.

---

# 9. Testing Strategy

Testing will follow three phases.

Phase 1

Administrator full-flow testing

Phase 2

Multi-role workflow validation

Phase 3

Scripted automated E2E tests

Playwright-based regression testing is planned.

---

# 10. AI Development Rules

Default executor

Claude Code

Backend implementation

Codex

UI design tasks

Gemini

Prompt workflow

promptsRec/active

Archived prompts

promptsRec/archive

---

# 11. Next Major Milestones

Complete RBAC account management

Assign test accounts for each role

Perform multi-role workflow testing

Introduce E2E test suite

Integrate Feishu notification workflow

Refactor database layer