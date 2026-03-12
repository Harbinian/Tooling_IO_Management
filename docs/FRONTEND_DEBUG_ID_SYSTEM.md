# Frontend Debug ID System

This document describes the enhanced debug identification system implemented in the Tooling IO Management System.

## Overview

The Debug ID system provides a structured way to identify UI elements for precise issue reporting. It is an overlay layer visible only to administrators.

## Debug ID Naming Scheme

Format: `PAGE-TYPE-NUMBER`

### Page Prefixes
- `A`: Login / Auth
- `D`: Dashboard
- `L`: Order List
- `C`: Order Create
- `OD`: Order Detail
- `K`: Keeper Workspace

### Element Categories
- `CARD`: Container cards
- `METRIC`: Statistical data displays
- `FIELD`: Input fields, selects, date pickers
- `BTN`: Buttons
- `FORM`: Form containers
- `TABLE`: Data tables
- `COL`: Table columns
- `FILTER`: Search/filter inputs
- `PANEL`: Specialized sections or panels
- `TAB`: Tab triggers or lists
- `SECTION`: Major page sections
- `ACTION`: Action triggers or button groups
- `DIALOG`: Modal dialogs or drawers

## Dialog Coverage

When labeling dialogs, follow these rules:

1.  **Dialog Root/Header**: Use a `DIALOG` or `PAGE` prefix for the overall dialog container or header.
2.  **Inner Sections**: Use `SECTION` for major blocks (e.g., search criteria, result area).
3.  **Inner Fields**: Use `FILTER` for search inputs and `FIELD` for data entry fields.
4.  **Inner Buttons**: Use `BTN` for action buttons (e.g., Search, Reset, Confirm, Cancel).
5.  **Inner Tables**: Use `TABLE` for result listings.

Example (Tool Search Dialog):
- Header: `C-DIALOG-001`
- Filter Section: `C-SECTION-002`
- Tool Code Filter: `C-FILTER-001`
- Search Button: `C-BTN-004`
- Result Table: `C-TABLE-002`
- Footer Action Area: `C-ACTION-002`
- Confirm Button: `C-BTN-006`

## Shared Component Propagation Rules

The `v-debug-id` directive should be applied to:

- **Native Elements**: Directly on `<div>`, `<section>`, etc.
- **Custom UI Components**: On the component tag if it has a single root element (e.g., `<Input v-debug-id="..." />`).
- **Complex Wrappers**: On the wrapper `div` if the inner element is a complex component (like `el-table`) or needs to include a label.

For `void` elements (like `<input>`), the directive automatically appends the badge to the parent element.

## Visibility & Activation

### Admin-only Visibility
The debug system is visible ONLY when:
1. The logged-in user has the `Administrator` role (or `sys_admin` role code).
2. Debug UI mode is explicitly enabled.

**Note**: If you are on the Login page and haven't logged in yet, debug identifiers will NOT be visible even if `?debugUI=1` is present. You must be logged in with an Administrator account.

### Activation Methods
Debug mode can be activated via URL query parameters:
- `?debugUI=1`: Enables **Hover Mode**. Debug IDs appear when hovering over elements.
- `?debugUI=pin`: Enables **Pin Mode**. Debug IDs are persistently visible.

## Features

### Hover Labels
In Hover Mode, a red badge with the Debug ID appears in the top-right corner of the element when the mouse hovers over it.

### Click-to-Copy
When debug mode is active:
- Clicking the red badge copies structured debug information to the clipboard.
- Alternatively, holding `Alt` and clicking the element itself also copies the information.

**Copied Information Example:**
```text
Page: Order Detail
Route: /inventory/IO-2024-001
Role: Administrator
DebugID: OD-BTN-004
Element: Final Confirm
```

## Issue Reporting Guidelines

When reporting a UI issue, please use the following standard format:

- **Page**: [Page Name]
- **Debug ID**: [e.g., C-FIELD-014]
- **Role**: [Your User Role]
- **Expected Behavior**: [What should happen]
- **Actual Behavior**: [What actually happened]
- **Steps to Reproduce**: [List of steps]

## Central Registry

All Debug IDs are defined in `frontend/src/debug/debugIds.js`. Developers should use this registry instead of hardcoding strings in components.

```javascript
import { DEBUG_IDS } from '@/debug/debugIds'

// Usage in template
// <div v-debug-id="DEBUG_IDS.PAGE.ELEMENT">...</div>
```
