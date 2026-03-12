# Safe Repository Context Slimming Report

**Date:** 2026-03-13
**Task:** 049_safe_repo_context_slimming

---

## Summary

This document describes the context slimming changes made to reduce Trae AI default context while preserving safe development capability.

---

## A. Prompts Restructuring

### What Was Moved to Archive

| Source | Destination | Count |
|--------|-------------|-------|
| `promptsRec/✅_*.md` | `promptsRec/archive/` | 58 prompts |

All completed prompts (archived with ✅_ prefix) have been moved to `promptsRec/archive/`.

### What Remains Active

| Location | Files |
|----------|-------|
| `promptsRec/active/` | 1 file (049_safe_repo_context_slimming.md) |

---

## B. Docs Whitelist

### Documents Now Visible

| File | Purpose |
|------|---------|
| `docs/ARCHITECTURE_INDEX.md` | Architecture overview and file reference |
| `docs/API_CONTRACT_SNAPSHOT.md` | API endpoint inventory |
| `docs/PRD.md` | Product requirements document |

### Documents Now Ignored

All other 63+ docs files are now ignored by default, including:
- Implementation docs (FEISHU_INTEGRATION_IMPLEMENTATION.md, etc.)
- Bug reports (BUG_*.md)
- Review reports (ARCHITECTURE_REVIEW.md, etc.)
- Design docs (RBAC_DESIGN.md, etc.)

---

## C. Directories Ignored

| Directory | Reason |
|-----------|--------|
| `logs/` | Runtime logs, generated content |
| `review-reports/` | Review artifacts |
| `run_records/` | Execution records |
| `promptsRec/archive/` | Historical prompts |
| `promptsRec/✅_*` | Completed prompts (legacy) |
| `promptsRec/*.lock` | Lock files |
| `node_modules/` | Dependencies |
| `.venv/` | Python environment |
| `dist/`, `build/` | Build outputs |
| `.git/` | Version control |

---

## D. Safe Development Visibility

The following remain visible by default:

| Scope | Contents |
|-------|----------|
| `backend/` | Python source code |
| `frontend/src/` | Vue.js source code |
| `tests/` | Test files |
| `promptsRec/active/` | Current task prompts |
| `docs/ARCHITECTURE_INDEX.md` | Architecture reference |
| `docs/API_CONTRACT_SNAPSHOT.md` | API reference |
| `docs/PRD.md` | Requirements |
| `.skills/` | Active skills |

---

## E. Token Reduction Estimate

| Category | Before | After | Reduction |
|----------|--------|-------|-----------|
| Docs visible | 66 files | 3 files | ~95% |
| Prompts visible | 60 files | 1 file | ~98% |
| Logs/review | 91 files | 0 | 100% |
| Total context | ~356 files | ~50 files | ~85% |

---

## F. Recommended Next Steps

### Future Split Candidates

1. **database.py** (2,691 lines) - Consider splitting into modules
2. **tool_io_service.py** (1,072 lines) - Consider service modularization
3. **OrderDetail.vue** (616 lines) - Consider component extraction

### Additional Ignore Candidates

- `.claude/plan/` - Old planning documents
- `promptsRec/archive/` - After confirming no need for historical reference
- `docs/` - Can further reduce if PRD is sufficient

---

## Configuration Safety

- All source code remains visible
- No business logic was changed
- No files were deleted
- Active skills remain accessible
- API and architecture references preserved
- Development workflow unaffected
