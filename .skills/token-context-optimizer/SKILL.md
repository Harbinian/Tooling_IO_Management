name: token-context-optimizer
executor: Claude Code
description: Maintain .trae/.ignore to reduce token usage by excluding large or irrelevant files from AI context scanning.

PURPOSE

This skill reduces token consumption during AI-assisted development.

It maintains the file:

.trae/.ignore

This file tells the AI environment which directories and files should NOT be scanned when loading repository context.

The goal is to keep AI context focused on:

backend source code
frontend source code
active prompts
essential architecture documents

and ignore everything else.

WHEN TO USE

Use this skill when:

repository grows large
AI responses become slower
review reports accumulate
large logs appear
build artifacts increase
token usage spikes

This skill should be executed occasionally to keep the repository AI-friendly.

STEP 1 — ENSURE .trae DIRECTORY

Check whether the repository contains:

.trae/

If it does not exist:

create directory ".trae"

STEP 2 — CREATE OR UPDATE IGNORE FILE

Ensure the file exists:

.trae/.ignore

If it already exists:

append missing rules
do not duplicate existing entries

STEP 3 — IGNORE DEPENDENCY DIRECTORIES

Add rules for dependency folders:

node_modules/
venv/
.venv/
__pycache__/

These folders should never be scanned by AI.

STEP 4 — IGNORE BUILD ARTIFACTS

Add rules for compiled outputs:

dist/
build/
frontend/dist/
frontend/build/

These directories contain generated files.

STEP 5 — IGNORE LOG AND TEMP FILES

Add rules for temporary files:

*.log
*.tmp
*.map
*.cache

These files do not help AI reasoning.

STEP 6 — IGNORE GENERATED REPORTS

Generated reports often consume large tokens.

Ignore directories such as:

review-reports/
run_records/
logs/

These files remain available for manual reading but should not be scanned automatically.

STEP 7 — PRESERVE IMPORTANT DIRECTORIES

Never ignore these directories:

backend/
frontend/src/
promptsRec/active/
promptsRec/archive/
docs/
.skills/

These contain active development logic.

STEP 8 — VALIDATE CONFIGURATION

After updating .trae/.ignore verify:

backend code remains visible
frontend src remains visible
promptsRec/active/ remains visible
promptsRec/archive/ remains visible
skills remain visible

Confirm ignored directories are no longer scanned.

EXPECTED RESULT

After execution:

.trae/.ignore exists
large directories are ignored
token consumption decreases
AI context stays focused on active code and essential docs