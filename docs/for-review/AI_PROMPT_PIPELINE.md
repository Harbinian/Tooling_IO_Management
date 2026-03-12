# AI Review: Prompt Pipeline Architecture

## Overview

The project uses a prompt-based task execution system (DocOps) for managing AI-driven development tasks.

## Directory Structure

```
promptsRec/
├── active/           # Active prompts (waiting to execute)
├── archive/          # Completed prompts
├── archive/
│   ├── 🔶_XXX_*     # Pending confirmation bugs
│   └── ✅_XXX_*     # Completed tasks
└── promptsRec/
    └── active/      # Current active prompt
```

## Prompt Naming Convention

### Active Prompts
- Format: `<3-digit_number>_<description>.md`
- Example: `054_generate_ai_auditable_codebase_documentation.md`

### Archived Prompts
- Format: `<icon>_<5-digit-sequence>_<original_name>_<status>.md`
- Example: `✅_00054_054_generate_ai_auditable_codebase_documentation_done.md`

### Icons
| Icon | Meaning |
|------|---------|
| ✅ | Completed |
| 🔶 | Pending confirmation (bugs only) |

## Prompt Metadata

Each prompt contains:

```markdown
Primary Executor: Claude Code
Fallback Executor: Codex
Gemini Usage: Forbidden Unless Explicitly Requested

TASK TYPE
<type>

STAGE
<number>

GOAL
<description>

---

# Context
# Required Work
# Output Files
# Repository Scanning
# Documentation Requirements
# Output Style
# Constraints
# Completion Criteria
```

## Task Types

- Repository Documentation Generation
- Backend Implementation
- Frontend Implementation
- Bug Fix
- Feature Development

## Task Numbers

| Range | Purpose |
|-------|---------|
| 000-099 | Feature/development tasks |
| 100-199 | Bug fixes |

## Lock Mechanism

- Lock files: `<prompt>.lock`
- Prevents parallel execution
- Content: executor, start_time, status

## Execution Flow

1. Scan `promptsRec/active/` for prompts without locks
2. Create lock file
3. Execute prompt task
4. Write execution report to `logs/prompt_task_runs/`
5. Archive prompt to `promptsRec/archive/`
6. Remove lock file

## Run Reports

Location: `logs/prompt_task_runs/`

Format: `run_[timestamp]_[prompt_name].md`

Contents:
- Prompt file
- Executor
- Start/end time
- Files created/updated
- Execution status

## Archive Numbering

- Scan existing archives for max sequence
- New sequence = max + 1
- 5-digit format: 00001, 00002, etc.

## Follow-up Tasks

- Detect by task number in filename
- Merge into existing archive's "## Follow-up Work" section
- Preserve original sequence number
