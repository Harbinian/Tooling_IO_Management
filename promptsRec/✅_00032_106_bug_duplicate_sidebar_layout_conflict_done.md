Primary Executor: Gemini
Task Type: Bug Fix
Category: Frontend Layout / UI Consistency
Goal: Diagnose and fix the duplicate sidebar layout conflict so the old left navigation block is removed or fully merged into the new Mist-style navigation system.
Execution: RUNPROMPT

---

# Context

The frontend has already started migrating to the new UI foundation:

- Tailwind CSS
- shadcn/ui
- Tailark Mist-inspired layout
- new dashboard and layout shell

However, the current page shows a layout inconsistency:

There are effectively two navigation systems visible at the same time.

Observed issue:

1. an old narrow left sidebar block still exists
2. a new Mist-style sidebar also exists
3. the main content is visually pushed to the right
4. the page feels structurally inconsistent and visually unbalanced

This is not a new feature request.
It is a UI regression / layout bug caused by incomplete migration.

---

# Required References

Read before making changes:

docs/FRONTEND_STYLE_MIGRATION_PLAN.md
docs/FRONTEND_UI_COMPONENT_MAP.md
docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md
docs/ORDER_LIST_UI_MIGRATION.md if it exists
docs/ORDER_DETAIL_UI_MIGRATION.md if it exists
docs/KEEPER_PROCESS_UI_MIGRATION.md if it exists
docs/ORDER_CREATE_UI_MIGRATION.md if it exists

Also inspect the current frontend layout files and page shell, including but not limited to:

- App.vue
- main layout files
- sidebar-related components
- dashboard page
- route container structure
- any legacy Element Plus navigation container

---

# Core Task

Diagnose and fix the duplicate sidebar layout conflict.

The final result must ensure:

1. there is only one active primary navigation system
2. the old left navigation block is removed or fully merged
3. the new Mist-style sidebar becomes the single source of navigation
4. the main content area aligns correctly with the final layout
5. visual consistency is restored across the page shell

Do NOT redesign the entire frontend again.
This is a layout correction task.

---

# Required Work

## A. Diagnose the Duplicate Navigation Source

Inspect the current layout structure and determine:

1. which component or layout still renders the old narrow left sidebar
2. which component renders the new Mist-style sidebar
3. whether both are mounted at the same time through:
   - App.vue
   - router view wrappers
   - nested layouts
   - legacy page containers
4. whether the old sidebar is globally mounted or page-specific

Do not guess.
Identify the real rendering source from the codebase.

---

## B. Determine the Correct Navigation Owner

Confirm which navigation system should remain as the primary navigation.

Expected direction:

- the new Mist-style sidebar should remain
- the legacy narrow left block should be removed or retired

If there are cases where the old block still provides needed functions, merge those functions into the new navigation instead of keeping two sidebars.

---

## C. Fix the Layout Conflict

Apply the minimum safe fix so that:

1. only one sidebar remains visible
2. spacing and container widths are recalculated correctly
3. the content area is no longer visually squeezed
4. dashboard and other migrated pages remain functional

Possible fix areas include:

- global layout wrapper
- sidebar component composition
- legacy container removal
- width / margin / padding cleanup
- page shell structure cleanup

Do NOT apply temporary CSS hacks without understanding the rendering structure.

---

## D. Verify Page Consistency

After the fix, verify that:

1. dashboard page uses a single sidebar layout
2. top header still works correctly
3. navigation links still work
4. content area aligns naturally
5. no duplicated menu remains
6. migrated pages still render inside the layout correctly

---

## E. Prepare for Future Page Migration

Make sure the fixed layout can be reused by:

- order list page
- order detail page
- keeper processing page
- order creation page

The final layout should become the stable shell for future page migrations.

---

## F. Documentation

Create:

docs/BUG_DUPLICATE_SIDEBAR_LAYOUT_CONFLICT.md

This document must include:

1. observed symptom
2. root cause
3. which layout/component caused the old sidebar to remain
4. what was removed or merged
5. final layout ownership decision
6. verification result
7. remaining limitations if any

---

# Constraints

1. Do not redesign unrelated UI modules.
2. Do not remove the new Mist-style navigation.
3. Do not keep two navigation systems visible.
4. Apply the smallest structural fix necessary.
5. Preserve existing routing behavior.
6. Keep code and comments in English.
7. Keep the result compatible with the ongoing UI migration strategy.

---

# Completion Criteria

The task is complete when:

1. only one sidebar navigation remains visible
2. the old left block is removed or merged
3. the page layout becomes visually coherent
4. dashboard still functions correctly
5. docs/BUG_DUPLICATE_SIDEBAR_LAYOUT_CONFLICT.md exists
6. the bug fix is archived properly in the code repository