name: repo-context-firewall
executor: Claude Code
description: Detect oversized files and context-heavy repository areas, then recommend or apply context optimization rules to reduce Trae token usage and improve AI development speed.

PURPOSE

This skill protects the repository from context explosion.

Its primary goal is to reduce token consumption for Trae built-in models by preventing oversized or low-value files from being repeatedly loaded into AI context.

Its secondary goal is to improve Claude Code and Codex development speed by reducing unnecessary repository scanning.

This skill does NOT directly implement business features.

It focuses on repository context efficiency.

CORE VALUE

For Trae built-in models:
- reduce token cost
- reduce context pollution
- reduce loading of irrelevant files

For Claude Code and Codex:
- improve repo scan speed
- reduce large-file analysis overhead
- make bug fixing and feature implementation more focused

WHEN TO USE

Use this skill when:

- the repository becomes large
- AI responses become slower
- Trae token usage becomes expensive
- review reports accumulate
- logs and build artifacts increase
- backend core files become too large
- documentation volume grows significantly

This skill should be used periodically as repository maintenance.

STEP 1 — SCAN FOR CONTEXT HOTSPOTS

Inspect the repository and identify files or directories that are likely to waste AI context.

Typical hotspots include:

- files larger than 200 KB
- source files longer than 500 lines
- generated reports
- logs
- build artifacts
- duplicated documents
- archived prompt execution records
- temporary files

STEP 2 — CLASSIFY HOTSPOTS

Classify each hotspot into one of the following groups:

GROUP A — Safe to Ignore
Examples:
- build outputs
- dependency folders
- logs
- generated reports
- temp files

GROUP B — Keep but Avoid Frequent Loading
Examples:
- large stable documentation
- archived prompt history
- completed run summaries
- old review documents

GROUP C — Must Stay Visible but Should Be Split
Examples:
- oversized backend source files
- oversized frontend source files
- oversized route files
- oversized query modules

STEP 3 — UPDATE .trae/.ignore

For Group A and appropriate Group B items:

- create or update .trae/.ignore
- add ignore rules
- avoid duplicate rules
- preserve important source directories

Never ignore:
- backend/
- frontend/src/
- promptsRec/active/
- promptsRec/archive/
- .skills/
- essential architecture entry documents

STEP 4 — GENERATE SPLIT RECOMMENDATIONS

For Group C files:

do NOT automatically refactor them in this skill

Instead generate a structured recommendation list including:

- file path
- approximate size
- reason it is context-heavy
- suggested split strategy

Examples:

database.py
Suggested split:
- database/core.py
- database/order_queries.py
- database/tool_queries.py
- database/rbac_queries.py

web_server.py
Suggested split:
- routes/auth_routes.py
- routes/order_routes.py
- routes/tool_routes.py
- routes/dashboard_routes.py

STEP 5 — PRESERVE ACTIVE DEVELOPMENT CONTEXT

The skill must ensure the following remain visible for AI development:

- active backend source files
- frontend src files
- current prompts under promptsRec/active/
- architecture index
- current API contract snapshot
- currently edited skill definitions

The purpose is optimization, not blindness.

STEP 6 — OUTPUT A FIREWALL REPORT

Create or update a report:

docs/REPO_CONTEXT_FIREWALL.md

The report must include:

- largest files
- most token-expensive directories
- ignored directories
- files recommended for splitting
- safe optimization actions
- high-risk areas for Trae token waste

STEP 7 — OPTIONAL LIGHTWEIGHT ENFORCEMENT

If safe and obvious, the skill may update:

.trae/.ignore

But it must NOT:
- delete files
- move files
- refactor source code automatically
- hide essential architecture documents

EXPECTED RESULT

After execution:

- Trae built-in model token usage is reduced
- unnecessary repo areas are ignored
- oversized files are identified
- split candidates are documented
- Claude Code and Codex can navigate the repo faster
- repository maintenance becomes more efficient
- docs/REPO_CONTEXT_FIREWALL.md exists and is up to date with the latest hotspots, classifications, ignore rules, split recommendations, and safe actions
- .trae/.ignore is up to date with the latest safe-to-ignore and split recommendations
- active development context remains visible for AI development