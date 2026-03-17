Primary Executor: Claude Code

Goal:
Initialize the AI-driven development pipeline for this project.

Do NOT implement business features.
Only prepare project infrastructure and documentation for the prompt-driven workflow.

---

# Required Directory Structure

Ensure the following directories exist:

rules/
skills/
promptsRec/
docs/
backend/
frontend/
logs/
logs/prompt_task_runs/

Create them if missing.

Do NOT delete existing files.

---

# Documentation

Create the document:

docs/AI_PIPELINE.md

This document must describe:

1. The prompt-driven development workflow
2. The role of each AI agent
3. The prompt task lifecycle
4. The standard pipeline stages

---

# AI Agent Responsibilities

Claude Code:
architecture design
technical design
architecture review
pipeline coordination

Codex:
backend implementation
database fixes
API implementation
frontend implementation

Gemini:
frontend design
interaction design
component structure planning

---

# Prompt Task Lifecycle

Document the workflow:

001_task.md
↓
create lock
↓
001.lock
↓
execute task
↓
delete lock
↓
archive prompt
↓
✅_00001_001_task_summary.md

---

# Pipeline Stages

Document the stages used by this project:

Architecture Design
Technical Design
Database Revision
Database Alignment
Backend Implementation
Architecture Review
Frontend Design
Frontend Implementation
Release Precheck

---

# Completion Criteria

The task is complete when:

docs/AI_PIPELINE.md exists
and explains the AI development workflow.