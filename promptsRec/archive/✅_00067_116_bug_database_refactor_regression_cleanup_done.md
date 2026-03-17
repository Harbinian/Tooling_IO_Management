Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 116
Goal: Repair regressions and incomplete cleanup introduced by the database module split refactor
Dependencies: 201
Execution: RUNPROMPT

---

## Context / 上下文

Code review of the archived stage-201 refactor result found that the database split was not completed cleanly.

Observed issues:

1. `docs/ARCHITECTURE_INDEX.md` was rewritten into a corrupted/duplicated state, with broken markdown structure and mojibake content.
2. The refactor left two parallel `core` implementations in place:
   - `backend/database/core.py`
   - `backend/database/core/`
3. The stage-201 archive/report trail is now ambiguous because multiple stage-201 archive artifacts exist and the execution result is hard to trace cleanly.

This means the refactor currently introduces documentation regression and leaves the database-layer authority model unclear.

---

## Required References / 必需参考

- `database.py`
- `backend/database/__init__.py`
- `backend/database/core.py`
- `backend/database/core/connection_pool.py`
- `backend/database/core/database_manager.py`
- `backend/database/core/executor.py`
- `docs/ARCHITECTURE_INDEX.md`
- `docs/PROMPT_TASK_CONVENTION.md`
- `docs/AI_PIPELINE.md`
- `promptsRec/archive/✅_00064_201_refactor_split_tool_io_service_done.md`
- `promptsRec/archive/✅_00066_201_refactor_database_module_split_done.md`

---

## Core Task / 核心任务

Clean up the failed/incomplete database refactor result so that:

- architecture documentation is readable and structurally valid
- there is one clear authoritative database core implementation
- the facade and package exports are consistent
- prompt/archive traceability for the stage-201 refactor chain is corrected

---

## Required Work / 必需工作

1. Inspect the current split architecture and determine which `core` implementation is authoritative:
   - `backend/database/core.py`
   - `backend/database/core/`

2. Remove the duplicate-authority condition without breaking imports:
   - either consolidate everything onto the package form `backend/database/core/`
   - or consolidate onto a single module path
   - but do not leave both as active implementations

3. Verify `database.py` remains a thin compatibility facade:
   - preserve public API names
   - preserve external imports used by existing services
   - avoid reintroducing business logic into the facade

4. Repair `docs/ARCHITECTURE_INDEX.md`:
   - remove corrupted/duplicated content
   - restore readable UTF-8 content
   - ensure markdown section boundaries are valid
   - keep the document aligned with the current architecture inventory

5. Review stage-201 prompt execution traceability:
   - determine which archive/report files are canonical
   - correct archive naming/report linkage if current state is misleading
   - avoid deleting historical evidence without documenting the correction

6. Add or update tests as needed to prove the cleanup did not break behavior:
   - facade imports still work
   - key database public functions still import/call successfully under mocks

7. Run validation and record exact results.

---

## Constraints / 约束条件

- Do NOT change database schema semantics
- Do NOT change public function names exposed by `database.py`
- Do NOT introduce new dependencies
- Do NOT silently delete archive history; if cleanup is needed, document it
- Preserve existing runtime behavior for routes/services importing `database.py`
- Prefer the smallest corrective change set that restores a single clear architecture

---

## Acceptance Tests / 验收测试

- `docs/ARCHITECTURE_INDEX.md` is readable and structurally valid markdown
- Only one authoritative database core implementation remains
- `database.py` still imports successfully as a compatibility facade
- Existing imports from backend services using `from database import ...` still work
- Relevant tests/validation commands pass
- Archive/report trail for the refactor task is understandable and documented

---

## Completion Criteria / 完成标准

- [ ] Duplicate database core authority removed
- [ ] `docs/ARCHITECTURE_INDEX.md` repaired
- [ ] `database.py` facade compatibility preserved
- [ ] Validation commands executed and recorded
- [ ] Stage-201 archive/report traceability clarified
- [ ] RUNPROMPT lifecycle completed with archive + run report + rectification log
