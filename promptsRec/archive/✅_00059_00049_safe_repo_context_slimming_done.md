Primary Executor: Claude Code
Task Type: Repository Maintenance
Stage: 049
Goal: Safely minimize Trae AI context by restructuring prompts and documentation visibility, updating `.trae/.ignore`, and preserving only the minimum high-value working set for default scanning.
Execution: RUNPROMPT

---

# Context

The repository weight analysis shows that the repository is not code-heavy but context-heavy.

Key findings:

- markdown files dominate repository weight
- docs and promptsRec together occupy a very large share of text lines
- logs and review reports add additional context noise
- backend business code is not the main context problem
- archived prompts and stable docs should not remain in default AI scanning scope

This task focuses on safe context slimming for Trae built-in model usage.

It must reduce default context aggressively while preserving safe development capability.

---

# Required References

Read before starting:

analysis/repo_weight_report.md or equivalent generated report
docs/ARCHITECTURE_INDEX.md
docs/API_CONTRACT_SNAPSHOT.md
docs/PRD.md

Inspect the current repository structure, including:

docs/
promptsRec/
review-reports/
logs/
backend/
frontend/src/
.skills/ or skills/

---

# Core Task

Minimize default AI context safely.

The task must:

1. keep only a minimal working set visible to Trae
2. move historical prompts out of active prompt scope
3. convert docs visibility to whitelist mode
4. update `.trae/.ignore`
5. preserve all files physically in the repository
6. avoid breaking development workflows

This task is about context exposure, not deleting project history.

---

# Required Work

## A. Restructure Prompt Visibility

Create or ensure the following structure exists:

promptsRec/active/
promptsRec/archive/

Move historical, completed, or no-longer-active prompts into:

promptsRec/archive/

Keep only currently actionable prompts in:

promptsRec/active/

Do not delete prompts.

---

## B. Convert Docs to Whitelist Visibility

Update `.trae/.ignore` so that docs are ignored by default.

Then explicitly allow only the smallest necessary document set, such as:

docs/ARCHITECTURE_INDEX.md
docs/API_CONTRACT_SNAPSHOT.md
docs/PRD.md

Optionally keep a very small number of additional documents only if clearly necessary.

Do not leave the full docs directory exposed by default.

---

## C. Ignore Historical and Generated Context

Ensure `.trae/.ignore` excludes at minimum:

review-reports/
logs/
run_records/
promptsRec/archive/
node_modules/
dist/
build/
frontend/dist/
frontend/build/
__pycache__/
.venv/
.git/
.idea/
.vscode/

Also exclude prompt archive noise such as:

promptsRec/✅_*
promptsRec/*.lock

---

## D. Preserve Safe Development Visibility

Ensure the following remain visible by default:

backend/
frontend/src/
tests/
promptsRec/active/
docs/ARCHITECTURE_INDEX.md
docs/API_CONTRACT_SNAPSHOT.md
docs/PRD.md
.skills/ or skills/ currently in use

Do not hide active source code.

---

## E. Generate a Context Slimming Report

Create:

docs/SAFE_REPO_CONTEXT_SLIMMING.md

The report must include:

1. what was moved to archive
2. which docs remain visible
3. which directories are ignored
4. why the configuration is safe
5. recommended next split candidates for future optimization

---

# Constraints

1. Do not delete repository history.
2. Do not refactor business code in this task.
3. Do not change API behavior.
4. Do not hide active source code.
5. Prefer hiding stable or historical files over changing working code.
6. Keep the result safe for continued AI-assisted development.

---

# Completion Criteria

The task is complete when:

1. promptsRec is split into active and archive scopes
2. docs visibility is whitelist-based
3. `.trae/.ignore` aggressively excludes historical and generated noise
4. active source code remains visible
5. docs/SAFE_REPO_CONTEXT_SLIMMING.md exists
6. Trae default context is significantly reduced without deleting project history