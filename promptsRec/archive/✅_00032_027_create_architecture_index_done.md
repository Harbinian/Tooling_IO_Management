Primary Executor: Claude Code
Task Type: Architecture Documentation & Dev Workflow Enforcement
Category: AI DevOps Infrastructure
Goal: Create an architecture index document and enforce document loading rules so that all models (Claude Code, Codex, Gemini) reliably read core architecture documents before implementing features.
Execution: RUNPROMPT

---

# Context

The project already contains several important architecture documents, including but not limited to:

docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/RBAC_INIT_DATA.md  

These documents define the system's authorization model, database schema, and initialization data.

However, in multi-model development workflows, models sometimes ignore existing documentation and implement logic inconsistently.

This task introduces a **central architecture index** and updates the development workflow so that models must load architecture documentation before implementing related features.

---

# Core Task

Create a centralized architecture index document and update project development rules so that all models must reference architecture documentation before implementing features.

This ensures:

- architecture consistency
- RBAC correctness
- database schema alignment
- stable AI-assisted development

---

# Part 1 — Create Architecture Index

Create a new document:

docs/ARCHITECTURE_INDEX.md

The document must serve as the **central reference map for system architecture documentation**.

It should include sections such as:

System Architecture Documents  
Security & RBAC  
Database Design  
Workflow & Business Logic  
Frontend Architecture  
AI Development Workflow

Each section must list the corresponding documents.

Example sections to include:

System Architecture  
- docs/ARCHITECTURE.md

RBAC and Security  
- docs/RBAC_DESIGN.md  
- docs/RBAC_DATABASE_SCHEMA.md  
- docs/RBAC_INIT_DATA.md  

Database Design  
- docs/RBAC_DATABASE_SCHEMA.md  

AI DevOps Architecture  
- docs/AI_DEVOPS_ARCHITECTURE.md  

The document should clearly state that:

All feature implementations must reference the architecture index.

---

# Part 2 — Define Document Usage Rules

Inside ARCHITECTURE_INDEX.md add a section called:

Architecture Usage Rules

Define rules such as:

1. Any change related to RBAC must read RBAC_DESIGN.md.
2. Any database change must read RBAC_DATABASE_SCHEMA.md.
3. Any permission initialization must reference RBAC_INIT_DATA.md.
4. No model should redefine RBAC logic without checking these documents.

These rules are meant for both humans and AI models.

---

# Part 3 — Update AI Development Workflow

Update or create a short section explaining how AI models should load architecture documentation.

For example:

Before implementing any backend logic related to:

- authentication
- authorization
- database schema
- workflow state machine

Models must first read:

docs/ARCHITECTURE_INDEX.md

Then load the referenced architecture documents.

---

# Part 4 — Integrate With Existing AI Workflow

If the project already has:

docs/AI_DEVOPS_ARCHITECTURE.md

Then update that document to reference:

docs/ARCHITECTURE_INDEX.md

Explain that the architecture index is the **entry point for architecture knowledge**.

---

# Part 5 — Ensure Compatibility With RUNPROMPT

Add a section describing how prompts should reference the architecture index.

Example rule:

Before implementing a task, the model should load:

docs/ARCHITECTURE_INDEX.md

Then identify relevant documents.

---

# Constraints

Do NOT change RBAC logic.

Do NOT modify database schema.

This task is documentation and workflow enforcement only.

---

# Completion Criteria

The task is complete when:

1. docs/ARCHITECTURE_INDEX.md exists
2. The document maps all major architecture documents
3. RBAC documents are included
4. Usage rules are clearly defined
5. AI workflow instructions are present
6. The development process now explicitly references the architecture index before implementing features