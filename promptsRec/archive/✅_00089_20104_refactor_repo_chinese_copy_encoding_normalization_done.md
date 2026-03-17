Primary Executor: Claude Code
Task Type: Refactoring
Priority: P0
Stage: 203
Goal: Normalize Chinese copy encoding repository-wide and eliminate mojibake from source/docs/scripts with zero functional change
Dependencies: None
Execution: RUNPROMPT

---

## Context / 背景

The repository currently contains mixed-encoding Chinese copy in multiple areas (frontend views, docs, and workflow assets), with mojibake risk observed during recent changes. This creates high risk for:

- wrong UI text rendering
- unreadable technical docs
- accidental corruption in database-interaction scripts
- future patch instability due repeated encode/decode cycles

This task is a **repository-wide encoding normalization refactor** and must preserve behavior.

## Required References / 必需参考

- `AGENTS.md`
- `.claude/rules/50_hotfix_sop.md`
- `docs/PROMPT_TASK_CONVENTION.md`
- `docs/AI_PIPELINE.md`
- `docs/README_AI_SYSTEM.md`
- Backend (high priority safety set):
  - `database.py`
  - `backend/services/auth_service.py`
  - `backend/services/rbac_service.py`
  - `backend/routes/auth_routes.py`
- Frontend and docs roots:
  - `frontend/src/`
  - `templates/`
  - `docs/`
  - `promptsRec/`

## Core Task / 核心任务

Perform repository-wide Chinese copy encoding normalization to UTF-8 (without BOM), remove mojibake text, and ensure no functional regression. Prioritize database interaction scripts and runtime code safety.

## Required Work / 必需工作

1. Build file inventory and classify text files
- Include code/docs/templates/prompt assets
- Exclude generated/binary/runtime artifacts (`frontend/dist/`, `node_modules/`, `__pycache__/`, logs output files)

2. Run encoding diagnostics
- Detect non-UTF8 or suspicious mojibake patterns
- Produce a candidate-fix list with file risk levels:
  - `critical`: DB scripts, backend runtime modules
  - `high`: API routes/services/frontend API
  - `medium`: Vue pages/components/templates
  - `low`: docs/prompt assets

3. Apply normalization in controlled batches
- Batch A: critical + high (backend/db/api)
- Batch B: frontend pages/components/templates
- Batch C: docs and prompt assets
- For each batch:
  - patch only confirmed mojibake text
  - keep logic and identifiers unchanged
  - avoid schema/SQL behavior changes

4. Protect database interaction scripts
- Confirm Chinese literals/comments in DB-related Python files are readable UTF-8
- Ensure SQL strings remain executable and unchanged semantically
- Do not introduce BOM or mixed newline corruption

5. Verification per batch
- Backend syntax:
  - `python -m py_compile web_server.py database.py backend/services/auth_service.py backend/services/rbac_service.py backend/routes/auth_routes.py`
- Targeted tests:
  - `python -m pytest tests/test_auth_system.py -q`
- Frontend build:
  - `cd frontend && npm run build`
- UTF-8 decode check script over normalized files

6. Reporting and traceability
- Summarize normalized files and risk class
- Record any files intentionally skipped with reason
- Include before/after examples for representative mojibake fixes

## Constraints / 约束条件

- Refactor-only: no business behavior change
- Keep API contracts and DB schema behavior unchanged
- Must preserve all SQL execution semantics
- Must use UTF-8 without BOM for normalized text files
- Do not edit generated artifacts unless explicitly required
- Do not use destructive git commands
- Follow minimal-blast-radius hotfix discipline from `50_hotfix_sop.md`

## Completion Criteria / 完成标准

1. All targeted repository text files are UTF-8 readable and no confirmed mojibake remains
2. Database interaction scripts are verified clean and executable
3. Backend compile check passes
4. Auth regression tests pass
5. Frontend build passes
6. RUNPROMPT lifecycle artifacts are completed:
- prompt archive rename (`✅_<seq>_203_refactor_repo_chinese_copy_encoding_normalization.md`)
- run report in `logs/prompt_task_runs/`
- codex rectification log in `logs/codex_rectification/` if real code/doc corrections occurred

### Acceptance Tests

| Test | Expected Result |
|------|-----------------|
| UTF-8 decode sweep on normalized files | 100% pass, no decode errors |
| Mojibake pattern scan (post-fix) | No confirmed mojibake in changed files |
| `python -m py_compile ...` | Pass |
| `python -m pytest tests/test_auth_system.py -q` | Pass |
| `frontend/npm run build` | Pass |
| Manual spot check: settings/auth/admin pages Chinese copy | Readable correct Chinese text |
| Manual spot check: DB script comments/strings | Readable UTF-8, SQL semantics unchanged |
