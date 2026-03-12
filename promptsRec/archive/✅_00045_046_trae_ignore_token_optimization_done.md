Primary Executor: Claude Code
Task Type: Repository Maintenance
Stage: 046
Goal: Create or update `.trae/.ignore` using the token-optimized template to reduce Trae built-in model token usage.
Execution: RUNPROMPT

Context

The repository has grown and now includes:

backend services  
frontend UI  
AI prompts  
review reports  
build artifacts  
logs  
large documentation sets  

Trae built-in models scan repository files to construct their working context.

If unnecessary files are scanned (logs, build artifacts, reports, archives), token usage increases dramatically.

This task introduces or updates `.trae/.ignore` so the Trae environment avoids loading irrelevant files.

The goal is to reduce token consumption while preserving access to active development files.

---

Core Task

1. Ensure the `.trae` directory exists.
2. Create or update `.trae/.ignore`.
3. Merge the optimized ignore template below.
4. Avoid duplicate entries.
5. Preserve visibility of core development directories.

---

Ignore Rules

node_modules/
venv/
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/

dist/
build/
frontend/dist/
frontend/build/

*.log
*.tmp
*.temp
*.cache
*.map
*.pyc
*.pyo
.DS_Store
Thumbs.db

review-reports/
run_records/
logs/

.git/
.idea/
.vscode/

promptsRec/✅_*
promptsRec/*.lock

docs/*
!docs/ARCHITECTURE_INDEX.md
!docs/ARCHITECTURE.md
!docs/PRD.md
!docs/API_CONTRACT_SNAPSHOT.md
!docs/RBAC_DESIGN.md
!docs/RBAC_DATABASE_SCHEMA.md
!docs/RBAC_INIT_DATA.md
!docs/AI_DEVOPS_ARCHITECTURE.md

---

Important Visibility Rules

Never ignore:

backend/
frontend/src/
promptsRec/
.skills/

These directories must remain visible for AI-assisted development.

---

Validation

Verify after execution:

backend source files remain visible

frontend/src remains visible

promptsRec active prompts remain visible

.skills remains visible

review-reports and build directories are ignored

---

Expected Result

`.trae/.ignore` exists

large irrelevant directories are excluded

Trae token consumption decreases

AI context stays focused on active development files