# AI Prompt Pipeline Architecture

## Overview

The project uses a prompt-based task execution system for managing AI-driven development tasks. This document describes the current pipeline architecture.

**注意**: 本文档描述的是当前系统的架构。更新的规则定义请参考 `.claude/rules/05_task_convention.md`。

## Directory Structure

```
promptsRec/
├── active/           # 待处理任务 (<类型编号>_<描述>.md)
├── archive/          # 已完成任务 (✅_<执行顺序号>_<类型编号>_<描述>_done.md)
└── .sequence        # 计数器文件
```

## Prompt Naming Convention

### Active Prompts

- Format: `<5-digit-type-number>_<description>.md`
- Example: `00017_order_list_ui_migration.md`
- Example: `10101_bug_tool_search_routing.md`

### Type Number Ranges

| Range | Type | Description |
|-------|------|-------------|
| 00001-09999 | Feature | 功能开发、UI迁移等 |
| 10101-19999 | Bug Fix | Bug修复任务 |
| 20101-29999 | Refactor | 代码重构 |
| 30101-39999 | Test | 自动化测试 |

### Archived Prompts

- Format: `✅_<exec-sequence>_<type-number>_<description>_done.md`
- Example: `✅_00182_00017_order_list_ui_migration_done.md`

## Counter File

The system uses `promptsRec/.sequence` to track the next available numbers:

```
# 功能开发 (00001-09999)
feature_next=00019

# Bug修复 (10101-19999)
bugfix_next=10178

# 重构 (20101-29999)
refactor_next=20101

# 测试 (30101-39999)
test_next=30101

# 执行顺序号（归档用）
exec_next=00182
```

## Execution Flow

1. Scan `promptsRec/active/` for prompts without locks
2. Create lock file `<prompt>.lock`
3. Execute prompt task
4. Write execution report to `logs/prompt_task_runs/`
5. Archive prompt to `promptsRec/archive/` with `✅` prefix
6. Remove lock file

## Run Reports

Location: `logs/prompt_task_runs/`

Format: `run_YYYYMMDD_<序号>_<任务名>.md`

## Skills Integration

The following skills automate rule execution:

| Rule | Skill | Purpose |
|------|-------|---------|
| `01_workflow.md` | `prompt-task-runner` | 四阶段流程执行 |
| `02_debug.md` | `self-healing-dev-loop` | 8D 问题解决 |
| `03_hotfix.md` | `self-healing-dev-loop` | 热修复流程 |
| `05_task_convention.md` | `auto-task-generator` | 任务生成与编号 |

## Task Executor Assignment

| Task Type | Executor | Exception |
|-----------|----------|-----------|
| Feature (00001-09999) | Claude Code | Frontend design major changes → human |
| Bug Fix (10101-19999) | Claude Code | P0/P1 malignant bugs |
| Refactor (20101-29999) | Claude Code | Always |
| Test (30101-39999) | Claude Code | Always |

## Simple Task Criteria

Tasks meeting these criteria are executed directly by Claude Code without spawning agents:

1. **Parameter issues**: Type mismatch, parameter passing errors
2. **Call errors**: Incorrect parameter extraction in function/method calls
3. **Signature corrections**: Function signature vs implementation mismatch
4. **Documentation updates**: docstring, comment sync
5. **Single-point fixes**: Single file/function modifications without architecture changes

## Malignant Bug Definition

- **P0**: System unusable, data corruption risk
- **P1**: Core functionality broken, API unavailable, workflow blocked

## Prohibited

1. **No duplicate exec numbers**: Each archived file must have a unique execution sequence number
2. **No missing suffix**: All archived files must include `_done.md` suffix
3. **No 3-digit numbers**: Both active and archive use 5-digit type numbers
4. **No archive scanning**: Never determine numbers by scanning archive directories
