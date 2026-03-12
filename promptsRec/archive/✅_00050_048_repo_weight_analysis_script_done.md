Primary Executor: Claude Code
Task Type: Repository Analysis Tooling
Stage: 048
Goal: Create a script that measures repository weight and AI context burden, then generate a structured report showing which files and directories are most likely causing token bloat and development slowdown.
Execution: RUNPROMPT

---

# Context

The repository has grown significantly.

There are now many:

- backend source files
- frontend source files
- docs
- skills
- prompts
- review reports
- generated records

The project is now feeling heavy, and we need objective measurements instead of guesswork.

This task is not for feature development.

It is for creating a repository analysis script that can measure:

1. file size distribution
2. line-count distribution
3. likely AI context hotspots
4. documentation / skill / prompt expansion
5. directories that should be ignored or split
6. files that are too large for efficient AI-assisted development

The output of this task will later be reviewed manually.

---

# Core Task

Create a script that analyzes the repository and outputs a structured weight report.

The script must help answer questions such as:

- which files are the largest
- which files have the most lines
- which directories contain the most total weight
- which files are likely expensive for AI context
- which file types dominate the repository
- which files are good candidates for splitting
- which directories are likely safe to ignore in `.trae/.ignore`

---

# Required Output Metrics

The script must collect at least the following metrics.

## A. File Size Metrics

For all files in the repository, calculate:

- file path
- file size in bytes
- file extension
- top N largest files

---

## B. Line Count Metrics

For text/code files, calculate:

- file path
- line count
- top N files by line count

This helps identify context-heavy source files.

---

## C. Directory Weight Metrics

Aggregate by directory:

- total number of files
- total size
- total line count where possible

At minimum summarize these areas if they exist:

- backend/
- frontend/
- docs/
- promptsRec/
- .skills/ or skills/
- review-reports/
- logs/
- run_records/

---

## D. File Type Distribution

Show distribution by extension, such as:

- .py
- .vue
- .ts
- .js
- .md
- .json
- others

For each file type, show:

- file count
- total size

---

## E. AI Context Hotspot Detection

Mark files as likely AI context hotspots if they match conditions such as:

- line count > 400
- size > 50 KB
- markdown > 20 KB
- generated reports / logs / archived prompts
- route or query files that are too large

This does not need to be perfect.
Use a practical heuristic.

---

## F. Suggested Optimization Candidates

The script should output simple candidates for:

- split candidates
- ignore candidates
- archive candidates

Examples:

split candidates:
- large backend source files
- oversized route modules
- oversized database/query files

ignore candidates:
- logs
- review reports
- build outputs
- archived prompts

---

# Implementation Requirements

Create the script in a practical location, for example:

scripts/repo_weight_analysis.py

Use Python unless there is a clearly better reason to use another language already standard in the repo.

The script should:

- run locally
- not require external services
- be readable and maintainable
- output results in a structured text or markdown report

---

# Report Output

The script must generate a report file, for example:

analysis/repo_weight_report.md

The report must include:

1. summary
2. top largest files
3. top files by line count
4. heaviest directories
5. file type distribution
6. context hotspot candidates
7. suggested split/ignore candidates

Make the report concise and readable.

---

# Validation

After writing the script, run it once and ensure:

- the report is generated successfully
- results are sorted and readable
- no critical repository areas are skipped accidentally
- the report can be reviewed manually afterward

---

# Constraints

1. Do not modify business logic.
2. Do not change `.trae/.ignore` in this task.
3. Do not refactor source files in this task.
4. Focus only on analysis and reporting.
5. Keep code and comments in English.
6. Keep the script lightweight and reusable.

---

# Completion Criteria

The task is complete when:

1. a repository weight analysis script exists
2. it runs successfully
3. it generates a structured report
4. the report includes file, directory, and hotspot analysis
5. the output is suitable for manual review and follow-up optimization decisions