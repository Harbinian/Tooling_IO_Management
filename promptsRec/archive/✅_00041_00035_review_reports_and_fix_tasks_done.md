Primary Executor: Claude Code
Task Type: Review Analysis
Stage: 035
Goal: Analyze repository review reports stored in the review-reports folder, consolidate findings, classify issues, and generate structured bug-fix prompts for the pipeline.
Execution: RUNPROMPT

---

# Context

The repository has already been reviewed by both Claude Code and Codex.

The generated review reports are stored under:

review-reports/

This task must use those reports as the source of truth.

The purpose of this task is NOT to fix code directly.

The purpose is to:

1. read all review reports in review-reports/
2. consolidate findings
3. classify issues
4. generate structured follow-up bug prompts where necessary
5. prepare the pipeline for controlled remediation

This task should avoid unnecessary expansion of the skill/doc system.
Reuse the existing project workflow and prompt rules.

---

# Required References

Read before processing:

docs/ARCHITECTURE_INDEX.md
docs/AI_DEVOPS_ARCHITECTURE.md
docs/BUG_WORKFLOW_RULES.md
docs/END_TO_END_RBAC_WORKFLOW_VALIDATION.md if it exists

Also inspect:

- all files under review-reports/
- existing prompts in promptsRec/
- existing bug documentation in docs/BUG_*.md

---

# Core Task

Process the repository review reports stored in review-reports/ and convert the findings into a controlled remediation plan.

The task must:

1. identify all reported issues
2. deduplicate overlapping findings between Claude Code and Codex reports
3. classify issues by category and severity
4. decide which issues should become bug prompts
5. avoid unnecessary prompt explosion
6. reuse existing bug chains where appropriate

Do NOT directly implement fixes in this task.

---

# Required Work

## A. Load Review Reports

Read all review reports stored in:

review-reports/

Identify:

- report source
- report scope
- reported findings
- repeated findings
- unresolved findings

Do not ignore overlap between reports.

---

## B. Consolidate Findings

Merge overlapping findings from different reports into unified issue items.

For each consolidated issue, determine:

- issue summary
- affected module
- probable layer
- severity
- whether it is already covered by an existing bug prompt
- whether it belongs to an existing bug chain

Avoid creating duplicate tasks for the same root cause.

---

## C. Issue Classification

Classify each issue into one of these categories:

- Architecture
- Security
- RBAC
- Authentication
- Data Scope
- API Contract
- Frontend Integration
- Performance
- Code Quality
- Documentation

Also classify severity:

- Critical
- High
- Medium
- Low

---

## D. Bug Workflow Decision

For each issue, decide one of the following:

1. Already covered by existing bug chain
2. Should be appended as a sub-issue to an existing bug document
3. Requires a new bug prompt
4. Should be handled later as a low-priority improvement
5. Documentation-only issue

This decision must follow:

docs/BUG_WORKFLOW_RULES.md

Do NOT create a new bug prompt if the issue is only a sub-issue of an existing root cause.

---

## E. Generate Follow-up Bug Prompts

Only generate new bug prompts for issues that truly require separate remediation.

Naming format:

promptsRec/10X_bug_<short_description>.md

Executor assignment rules:

- Claude Code → architecture / system consistency issues
- Codex → backend / API / database issues
- Gemini → frontend UI / interaction issues

Each generated bug prompt must follow the existing project prompt format.

Do not generate unnecessary prompts.

---

## F. Produce Consolidation Report

Create:

docs/REVIEW_REPORT_CONSOLIDATION.md

This report must include:

1. reports processed
2. total findings
3. deduplicated issue list
4. issues by category
5. issues by severity
6. mapping to existing bug chains if any
7. newly generated bug prompts if any
8. issues deferred or documented only

The report should be concise and action-oriented.

---

# Constraints

1. Do not fix code in this task.
2. Do not create duplicate bug prompts.
3. Follow one-bug-one-prompt rules.
4. Reuse existing bug chains whenever possible.
5. Do not add new skills.
6. Do not create unnecessary new documents beyond the required consolidation report and truly necessary bug prompts.
7. Keep the remediation plan lightweight and token-efficient.

---

# Completion Criteria

The task is complete when:

1. all review reports in review-reports/ have been processed
2. duplicate findings are consolidated
3. issues are classified by category and severity
4. only necessary bug prompts are generated
5. docs/REVIEW_REPORT_CONSOLIDATION.md exists
6. the output is ready for pipeline-dashboard and RUNPROMPT without creating unnecessary task bloat
7. the output is ready for END_TO_END_RBAC_WORKFLOW_VALIDATION.md if it exists