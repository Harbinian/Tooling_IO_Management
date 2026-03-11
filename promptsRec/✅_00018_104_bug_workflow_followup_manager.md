Primary Executor: Claude Code
Task Type: Architecture / DevOps Workflow
Goal: Implement a bug follow-up management rule to prevent prompt explosion during debugging.
Execution: RUNPROMPT

---

# Context

The project now uses prompt-driven development and bug fixing.

Bug prompts are stored in promptsRec/.

Example:

101_bug_tool_search_request_routing.md
102_bug_vite_entry_compile_failure.md
103_bug_order_list_api_500.md

During debugging, new issues may appear that are actually sub-issues of the same root cause.

Creating a new bug prompt for every sub-issue leads to uncontrolled prompt growth.

This task implements a bug workflow rule that ensures a single bug prompt manages the full debugging chain.

---

# Core Task

Implement a bug follow-up workflow rule in the project documentation and pipeline logic.

The rule must ensure:

1 one bug → one primary prompt
2 sub-issues recorded in bug documentation
3 new prompts created only when escalation conditions are met

---

# Required Work

## A Validate Existing Bug Prompts

Inspect promptsRec/.

Identify all bug prompts:

files matching pattern:

*_bug_*.md

Ensure they follow the numbering scheme:

100–199 range.

If inconsistencies exist, document them but do not rename files automatically.

---

## B Implement Bug Follow-Up Rule

Ensure the debugging process follows these rules:

Sub-issues discovered during debugging must be recorded in:

docs/BUG_<NAME>.md

instead of creating new prompts.

The rule must explicitly forbid automatic creation of additional bug prompts unless escalation conditions are met.

---

## C Escalation Logic

Define escalation conditions:

A new bug prompt is allowed only if:

1 root cause is unrelated to original bug
2 issue belongs to a different subsystem
3 fixing it inside the original bug would cause architectural side effects

Otherwise the issue remains part of the original bug.

---

## D Pipeline Integration

Update pipeline logic so that:

pipeline-dashboard
bug-triage

both recognize the bug workflow rules.

When a bug prompt already exists:

the system must recommend updating the existing bug documentation instead of creating a new prompt.

---

## E Documentation

Ensure the following document exists and is referenced:

docs/BUG_WORKFLOW_RULES.md

The pipeline must treat this document as the source of truth for bug lifecycle rules.

---

# Constraints

1 Do not modify working bug prompts.
2 Do not rename archived prompts.
3 Avoid automatic file renaming.
4 Keep the change limited to workflow rules and documentation.

---

# Completion Criteria

The task is complete when:

1 BUG_WORKFLOW_RULES.md is validated
2 bug follow-up rules are documented
3 pipeline logic respects the one-bug-one-prompt principle
4 escalation conditions are clearly defined in BUG_WORKFLOW_RULES.md