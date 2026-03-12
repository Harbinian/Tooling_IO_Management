Primary Executor: Gemini
Task Type: Bug Fix
Category: Frontend Debug Overlay / Dialog Coverage
Goal: Fix the debug ID overlay system so inner elements inside the tool search dialog are correctly labeled, not just the dialog title/header container.
Execution: RUNPROMPT

---

# Context

The admin-only debug ID overlay system has been implemented, and debug mode is active.

A major bug has been found in the tool search dialog page:

- the dialog title/header area is labeled
- but the inner UI elements are NOT labeled

Missing labels include:

- form fields
- table areas
- action buttons
- selection controls
- footer buttons

This makes the debug overlay system incomplete and reduces its usefulness for issue reporting.

This is a bug in the debug overlay coverage, not a business logic problem.

---

# Required References

Read before making changes:

docs/ARCHITECTURE_INDEX.md
docs/FRONTEND_DEBUG_ID_SYSTEM.md
docs/LOGIN_PAGE_AND_AUTH_FLOW_UI.md
docs/FRONTEND_PERMISSION_VISIBILITY.md

Also inspect the current frontend implementation related to:

- debug ID registry
- debug overlay directive / wrapper / composable
- tool search dialog component
- shared input components
- shared button components
- shared table components
- dialog / modal container components

Use the actual current codebase as source of truth.

---

# Core Task

Fix the debug overlay system so the inner elements inside the tool search dialog receive and display debug IDs correctly.

The final result must ensure:

1. dialog header remains labeled
2. inner form fields are labeled
3. table container is labeled
4. major table-related controls are labeled
5. footer action buttons are labeled
6. admin-only behavior remains intact
7. normal non-debug UI behavior remains unchanged

---

# Required Work

## A. Reproduce and Inspect the Coverage Gap

Inspect the tool search dialog in debug mode.

Determine why only the dialog header receives a debug label while inner elements do not.

Possible causes include:

- debug wrapper only applied to outer dialog container
- inner elements missing debug ID bindings
- directive not working through component boundaries
- shared components not forwarding debug metadata
- slot content losing debug props
- hover layer blocked by container structure
- z-index / pointer-events issues inside modal body

Do not guess.
Confirm the actual cause in the real implementation.

---

## B. Inspect Debug ID Registry Coverage

Check whether the tool search dialog inner elements already have defined debug IDs in the registry.

At minimum verify coverage for:

- dialog root
- dialog title/header
- tool code field
- tool name field
- drawing number field
- spec field
- location field
- reset button
- search button
- result table
- row selection area if supported
- cancel button
- confirm/add button

If IDs are missing, add them using the established naming scheme.

Suggested page/dialog prefix style should remain consistent with the current system.

---

## C. Fix Component Propagation

If the bug comes from shared components not exposing debug overlay support, fix that propagation path.

Typical problem areas may include:

- custom input wrapper components
- button components
- table wrapper components
- dialog slot rendering
- field block wrappers

Ensure debug metadata can reach the actual rendered DOM node or the intended visible wrapper.

---

## D. Ensure Dialog-Specific Coverage

Apply debug coverage to the major human-reportable UI units inside the tool search dialog.

Focus on meaningful elements, not every tiny nested DOM node.

Required coverage should include at least:

1. search criteria section
2. key input fields
3. search/reset actions
4. result table block
5. footer action area
6. confirm/cancel buttons

---

## E. Preserve Existing Rules

Preserve all existing debug system rules:

- visible only for administrators
- visible only when debug mode is enabled
- hover behavior remains correct
- optional pin mode behavior remains correct if already implemented
- click-to-copy behavior remains correct if already implemented

Do not weaken these constraints.

---

## F. Validate Other Dialogs if Needed

If the root cause is generic to dialog internals, inspect whether the same issue may affect other dialogs or modal panels.

Only apply safe, minimal fixes where justified.

Do not start a broad redesign.

---

## G. Documentation

Update:

docs/FRONTEND_DEBUG_ID_SYSTEM.md

Include:

1. dialog coverage behavior
2. shared component propagation rules
3. how dialog inner elements should be labeled
4. any implementation caveats discovered

---

# Constraints

1. Do not redesign the full debug ID system.
2. Do not redesign the dialog UI layout.
3. Do not change business logic or API behavior.
4. Keep the fix minimal and targeted.
5. Keep code and comments in English.
6. Preserve admin-only and debug-mode-only visibility.

---

# Completion Criteria

The task is complete when:

1. tool search dialog inner elements display debug IDs
2. form fields are labeled
3. action buttons are labeled
4. result table area is labeled
5. header and body coverage both work
6. admin-only debug visibility still works
7. docs/FRONTEND_DEBUG_ID_SYSTEM.md is updated with dialog-specific coverage details