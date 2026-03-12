Primary Executor: Gemini
Task Type: Refactoring
Priority: P2
Stage: 202
Goal: Resolve Element Plus vs shadcn/ui dual library conflict
Dependencies: 017 (API layer unification first)
Execution: RUNPROMPT

---

## Context

Code review found that the frontend references both Element Plus and shadcn/ui + Tailwind CSS. Running two UI component libraries increases bundle size and creates visual inconsistency. The project's design direction is Mist style with shadcn/ui.

## Required References

- `frontend/package.json` — current dependencies
- `frontend/src/components/ui/` — shadcn-style components
- `frontend/src/pages/` — all page files (check which use Element Plus)
- `frontend/src/main.js` — library registration
- `AI_FRONTEND_STRUCTURE.md` — frontend architecture

## Core Task

Audit Element Plus usage across the codebase and create a migration plan. Execute migration for pages that have minimal Element Plus dependency.

## Required Work

1. Scan all `.vue` files for Element Plus component usage (el-* tags, ElMessage, ElMessageBox, etc.)
2. Create an inventory table: file → Element Plus components used → shadcn/custom equivalent
3. For each Element Plus component found, determine if a shadcn/ui equivalent exists in `components/ui/`
4. Migrate pages with ≤3 Element Plus components to shadcn/ui equivalents
5. For pages with heavy Element Plus usage, add TODO comments with migration notes
6. If ALL Element Plus usage is removed, uninstall the package
7. Update `AI_FRONTEND_STRUCTURE.md`

## Constraints

- Do NOT break any existing page functionality
- Do NOT create new shadcn components unless necessary (use existing ones first)
- Migrate incrementally — do not attempt a full rewrite in one pass
- Maintain visual consistency with Mist design style

## Acceptance Tests

- All migrated pages render correctly with no visual regression
- Bundle size is reduced (or at minimum not increased)
- No unused Element Plus imports remain in migrated files
- Mist design style is maintained

## Completion Criteria

- [ ] Element Plus usage inventory created (as code comment or doc)
- [ ] At least 3 pages migrated away from Element Plus
- [ ] No visual regression on migrated pages
- [ ] AI_FRONTEND_STRUCTURE.md updated with migration status
