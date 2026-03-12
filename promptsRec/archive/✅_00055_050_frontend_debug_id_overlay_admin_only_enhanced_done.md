Primary Executor: Gemini
Task Type: Frontend Debug Tooling
Stage: 050
Goal: Implement an enhanced admin-only UI debug identification system with structured IDs, hover labels, optional pin mode, and click-to-copy debug information for precise issue reporting.
Execution: RUNPROMPT

---

# Context

The frontend system has grown large enough that describing UI problems precisely has become difficult.

When manually reviewing pages, it is often unclear which exact field, button, section, or panel is being referenced.

To solve this, we need a **structured debug identification overlay** that allows administrators to:

- hover over UI elements and see a debug identifier
- optionally display identifiers persistently
- click an element to copy structured debug information

This system will significantly improve communication when reporting UI issues to Claude Code, Codex, or other models.

Example issue reports after implementation:

Dashboard D-CARD-003 metric incorrect  
OrderCreate C-FIELD-014 label mismatch  
KeeperWorkspace K-BTN-022 should be disabled  

---

# Critical Constraints

This task must NOT:

- refactor backend logic
- change API contracts
- change business workflow
- change RBAC logic
- redesign page layout

This system is purely a **debug overlay layer**.

---

# Admin-only Visibility Requirement

The debug system must only be visible when BOTH conditions are satisfied:

1. logged-in user role = Administrator
2. debug UI mode explicitly enabled

Other roles must NEVER see debug identifiers.

Roles that must not see debug IDs:

- Team Leader
- Keeper
- Transport Operator
- Planner
- Auditor

If the role cannot be determined, debug mode must remain disabled.

---

# Debug Mode Activation

Debug UI should activate when:

Administrator user AND debug mode flag enabled.

Possible activation methods:

Query parameter example:

?debugUI=1

Alternative options may include:

local storage flag  
development environment variable  

Normal users must never see debug overlays.

---

# Structured Debug ID Naming Scheme

The system must use **structured identifiers**, not just numbers.

Format:

PAGE-TYPE-NUMBER

Examples:

Dashboard
D-CARD-003
D-METRIC-002

Order List
L-FILTER-001
L-TABLE-001
L-BTN-003

Order Detail
OD-PANEL-002
OD-AUDIT-001
OD-BTN-005

Order Create
C-FIELD-014
C-FORM-001
C-BTN-002

Keeper Workspace
K-LIST-001
K-PANEL-002
K-BTN-022

Login
A-FIELD-001
A-BTN-002

The TYPE portion should reflect the element category.

---

# Element Categories

Suggested categories:

CARD  
METRIC  
FIELD  
BTN  
FORM  
TABLE  
COL  
FILTER  
PANEL  
TAB  
SECTION  
ACTION  
DIALOG  

Do not create IDs for purely decorative elements.

Focus on elements that humans will reference when reporting problems.

---

# Hover Display Behavior

When hovering over a debug-enabled element:

- display a small badge containing the debug ID
- ensure the badge is visible but unobtrusive
- avoid layout shifts

Recommended style:

top-right corner label  
small tooltip-like badge  

---

# Persistent Pin Mode

The debug system should support two display modes:

Hover Mode (default)

- debug ID appears only when hovering over elements

Pin Mode

- debug IDs are always visible on labeled elements

Pin mode may be enabled via:

query parameter  
debug toggle  

Example:

?debugUI=pin

This mode helps when capturing screenshots.

---

# Click-to-Copy Debug Information

When an administrator clicks a labeled element in debug mode:

Copy structured debug information to clipboard.

Example copied content:

Page: OrderCreate  
Route: /tool-io/create  
Role: Administrator  
DebugID: C-FIELD-014  
Element: Planned Return Time  

This allows precise bug reports.

---

# Central Debug ID Registry

To avoid scattered definitions, debug IDs must be defined in a central registry.

Example location:

frontend/src/debug/debugIds.ts

The registry should:

- group IDs by page
- prevent duplicates
- allow easy maintenance
- allow future documentation generation

Example structure concept:

Dashboard IDs  
OrderList IDs  
OrderCreate IDs  
OrderDetail IDs  
KeeperWorkspace IDs  
Login IDs  

---

# Implementation Approach

Use a reusable mechanism such as:

Vue directive  
wrapper component  
composable utility  

Avoid duplicating debug logic across components.

Developers should be able to easily attach debug IDs to elements.

---

# Page Coverage Priority

Apply debug IDs to these pages first:

Dashboard  
Order List  
Order Create  
Order Detail  
Keeper Workspace  
Login  

Also cover major dialogs such as:

tool search dialog  
confirmation dialogs  
notification panels  

---

# Preserve Existing Behavior

Do NOT change:

routing  
RBAC permissions  
API behavior  
business workflow  
existing UI structure  

This system must function as a non-invasive debug overlay.

---

# Documentation

Create:

docs/FRONTEND_DEBUG_ID_SYSTEM.md

Document must include:

debug ID naming scheme  
page prefixes  
element categories  
admin-only visibility rule  
debug mode activation  
pin mode usage  
click-to-copy behavior  
guidelines for reporting issues  

Also include a **standard issue reporting format**.

Example:

Page  
Debug ID  
Role  
Expected behavior  
Actual behavior  
Steps to reproduce  

---

# Completion Criteria

Task is complete when:

1. debug ID overlay exists
2. identifiers follow structured naming
3. hover displays IDs
4. pin mode displays IDs persistently
5. click copies structured debug information
6. debug overlay visible ONLY to administrators with debug mode enabled
7. Dashboard, Order List, Order Create, Order Detail, Keeper Workspace, Login pages are covered
8. debug ID registry exists
9. docs/FRONTEND_DEBUG_ID_SYSTEM.md exists