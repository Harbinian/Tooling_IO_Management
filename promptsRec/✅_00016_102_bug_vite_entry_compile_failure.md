Primary Executor: Codex
Task Type: Bug Fix
Category: Frontend Build / Runtime Compile
Goal: Diagnose and fix the Vite frontend compile failure causing App.vue and router/index.js to return 500 in development.
Execution: RUNPROMPT

---

# Context

The frontend development server starts successfully and Vite connects, but the browser fails to load core source files.

Observed behavior includes:

- Vite client connects successfully
- GET /src/router/index.js returns 500
- GET /src/App.vue returns 500

This indicates a frontend source compilation or module resolution failure.

This task must be solved by investigation first, then correction.

Do NOT guess blindly.
Trace the actual compile failure from Vite logs and frontend source dependencies.

---

# Required References

Read before making changes:

docs/PRD.md
docs/ARCHITECTURE.md
docs/FRONTEND_DESIGN.md
docs/README_AI_SYSTEM.md
docs/AI_DEVOPS_ARCHITECTURE.md

Inspect relevant frontend files, including but not limited to:

- src/main.js
- src/App.vue
- src/router/index.js
- recently modified Vue components
- recently modified API files
- Vite config
- package.json

---

# Core Task

Diagnose and fix the frontend compile failure so that:

1. App.vue can load successfully
2. router/index.js can load successfully
3. the Vite dev server serves the app normally
4. no related source file returns 500 in development

---

# Investigation Requirements

Before applying any fix, inspect the actual error source.

You must:

1. read Vite terminal output
2. run a frontend build check
3. identify the first real compile or import error
4. trace whether the failure comes from:
   - syntax error
   - invalid Vue SFC structure
   - broken import path
   - missing file
   - incorrect export/import usage
   - recently introduced regression

Do not stop at the browser 500 symptom.
Find the true root cause.

---

# Diagnosis Tasks

Determine:

1. whether src/App.vue itself is invalid
2. whether src/router/index.js itself is invalid
3. whether either file imports another broken module
4. whether any recently added component breaks the dependency chain
5. whether Vite config or alias config contributes to the failure
6. whether case-sensitive path mismatch exists in imports

Document the exact root cause.

---

# Fix Requirements

After identifying the root cause, apply the minimum safe fix.

The fix must ensure:

1. Vite dev server can compile the frontend
2. App.vue loads normally
3. router/index.js loads normally
4. recently implemented features remain intact where possible
5. no unrelated modules are redesigned

Possible fix areas include:

- Vue SFC syntax correction
- import path correction
- missing export/default export correction
- router config correction
- component reference correction
- build config correction

Avoid broad rewrites.

---

# Verification

After applying the fix, verify all of the following:

1. npm run build succeeds
2. npm run dev serves the app without 500 on App.vue
3. npm run dev serves the app without 500 on router/index.js
4. the application shell loads in browser
5. no regression is introduced in existing tool search flow

---

# Documentation

Create:

docs/BUG_VITE_ENTRY_COMPILE_FAILURE.md

Document:

1. observed symptom
2. root cause
3. files changed
4. fix applied
5. verification results
6. remaining risks if any

---

# Constraints

1. Investigate before changing code.
2. Do not redesign unrelated frontend modules.
3. Apply the smallest safe fix.
4. Preserve current working features where possible.
5. Keep code and comments in English.
6. Use the real Vite/build error output as the source of truth.

---

# Completion Criteria

The task is complete when:

1. App.vue no longer returns 500 in dev
2. router/index.js no longer returns 500 in dev
3. frontend can compile and load normally
4. docs/BUG_VITE_ENTRY_COMPILE_FAILURE.md exists
5. the bug fix is archived properly