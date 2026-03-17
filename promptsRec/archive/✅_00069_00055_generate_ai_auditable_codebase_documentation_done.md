Primary Executor: Claude Code
Fallback Executor: Codex
Gemini Usage: Forbidden Unless Explicitly Requested

TASK TYPE
Repository Documentation Generation

STAGE
054

GOAL
Generate a complete AI-auditable documentation package for the entire repository.

The output must allow other AI models to review the codebase without reading the entire project.

This document will serve as a compressed but comprehensive representation of the codebase.

---

# Context

The project has grown large enough that direct code inspection is expensive for AI models.

We want to create a structured documentation layer that allows:

Claude Code  
Codex  
Gemini  
or other external AI reviewers

to understand the system architecture quickly.

The documentation must summarize:

system architecture  
modules  
API contracts  
data models  
RBAC model  
frontend structure  
workflow state machine  

without exposing unnecessary noise.

This documentation must be readable by both humans and AI.

---

# Required Work

Analyze the entire repository and generate a documentation bundle.

The documentation must include:

System architecture overview

Backend module structure

Database schema summary

API endpoints summary

RBAC model explanation

Workflow state machine

Frontend page structure

Key UI components

Debug infrastructure

Prompt pipeline architecture

AI development workflow

---

# Output Files

Create the following documents.

docs/AI_REVIEW_CODEBASE_OVERVIEW.md

docs/AI_BACKEND_STRUCTURE.md

docs/AI_FRONTEND_STRUCTURE.md

docs/AI_DATABASE_MODEL.md

docs/AI_API_CONTRACT_SUMMARY.md

docs/AI_RBAC_MODEL.md

docs/AI_WORKFLOW_STATE_MACHINE.md

docs/AI_DEBUG_INFRASTRUCTURE.md

docs/AI_PROMPT_PIPELINE.md

docs/AI_TESTING_STRATEGY.md

Each document must be concise but complete.

Avoid large narrative sections.

Prefer structured sections and bullet points.

---

# Repository Scanning

The analysis must inspect

backend  
frontend  
database modules  
service layer  
API routes  
RBAC logic  
debug system  
prompt pipeline  

Use the real code as source of truth.

Do not invent architecture.

---

# Documentation Requirements

Each document must include:

purpose of the module

main components

key files

key responsibilities

dependencies

important design decisions

---

# Output Style

Use clean markdown.

Avoid code duplication.

Prefer tables and bullet lists.

Avoid long paragraphs.

Ensure each document is under 1000 lines.

---

# Constraints

Do not modify any existing code.

Do not refactor modules.

Do not change APIs.

Only generate documentation.

---

# Completion Criteria

The task is complete when

all documentation files are generated

documents reflect the real codebase

documents allow AI reviewers to understand the system without scanning the entire repository