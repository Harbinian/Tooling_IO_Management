Primary Executor: Codex
Task Type: Code Refactoring
Stage: 036
Goal: Refactor oversized backend core files (database.py and web_server.py) into modular components to reduce AI context usage, improve maintainability, and preserve current behavior.
Execution: RUNPROMPT

---

# Context

The repository analysis shows that two files consume a large portion of the development context:

database.py  
web_server.py  

These files are large and frequently loaded during debugging and development, which significantly increases token usage and slows AI-assisted workflows.

Current observations:

- database.py exceeds ~1000 lines
- web_server.py contains most API route definitions and middleware logic
- both files are frequently scanned by models when analyzing bugs or API behavior

The goal of this task is to **reduce context size and improve modularity** without changing the functional behavior of the system.

This is a **refactoring task**, not a feature implementation task.

---

# Required References

Before refactoring, read:

docs/ARCHITECTURE_INDEX.md  
docs/ARCHITECTURE.md  
docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/ORG_STRUCTURE_IMPLEMENTATION.md  

Also inspect current backend structure and service usage patterns.

---

# Core Task

Refactor oversized backend files into modular components.

The refactor must:

1. split database logic into domain-specific modules
2. split API routing logic into route modules
3. keep behavior identical
4. reduce file size for each module
5. maintain compatibility with existing imports

Avoid breaking existing business logic.

---

# Part 1 — Refactor database.py

Create a database module structure.

Suggested directory:

backend/database/

Target structure example:

backend/database/core.py  
backend/database/order_queries.py  
backend/database/tool_queries.py  
backend/database/dashboard_queries.py  
backend/database/rbac_queries.py  

Responsibilities:

core.py  
- database connection logic
- connection pool
- basic query execution helpers

order_queries.py  
- order-related queries
- tool IO order logic
- order status queries

tool_queries.py  
- tool search queries
- tool master lookup
- tool location queries

dashboard_queries.py  
- dashboard statistics
- aggregate counts

rbac_queries.py  
- user queries
- role queries
- permission queries
- organization queries

Migration rules:

- move SQL blocks into correct modules
- move helper functions with the SQL they belong to
- avoid circular imports
- preserve existing method signatures where possible

After refactoring:

database.py should become a lightweight compatibility wrapper or be removed.

---

# Part 2 — Refactor web_server.py

Create route modules.

Suggested directory:

backend/routes/

Target structure example:

backend/routes/auth_routes.py  
backend/routes/order_routes.py  
backend/routes/tool_routes.py  
backend/routes/dashboard_routes.py  
backend/routes/rbac_routes.py  

Responsibilities:

auth_routes.py  
- login API
- current user API
- logout API if present

order_routes.py  
- order list
- order detail
- order creation
- keeper confirmation
- final confirmation

tool_routes.py  
- tool search
- tool lookup

dashboard_routes.py  
- dashboard statistics APIs

rbac_routes.py  
- user management
- role management
- permission queries

The main web_server.py should then only:

- create the app
- register middleware
- register route modules

---

# Part 3 — Preserve Middleware and Guards

Ensure that:

- authentication middleware
- permission guard
- RBAC loading
- request context setup

continue to work exactly as before.

Middleware should remain centralized in the main server initialization.

Do not duplicate permission checks across route files.

---

# Part 4 — Import Compatibility

Ensure existing imports continue to work where possible.

If refactoring changes import paths, update:

- service modules
- route modules
- middleware modules

The system must still run without manual import fixes after the refactor.

---

# Part 5 — File Size Target

After refactoring:

No backend file should exceed approximately:

400 lines

Recommended ranges:

core modules  
100–250 lines

route modules  
100–300 lines

query modules  
100–350 lines

This reduces the likelihood that AI models must read very large files during debugging.

---

# Part 6 — Regression Safety

Before finishing the refactor, verify that:

- API routes still respond
- database queries still execute
- authentication still works
- RBAC permission checks still work
- order workflows remain functional

No business logic must be altered.

---

# Part 7 — Documentation

Create:

docs/BACKEND_REFACTOR_CONTEXT_OPTIMIZATION.md

The document must include:

1. original large files
2. new module structure
3. database module design
4. route module design
5. compatibility considerations
6. expected reduction in context size
7. future recommendations for keeping files small

---

# Constraints

1. Do not change database schema.
2. Do not change API contracts.
3. Do not redesign RBAC.
4. Preserve existing functionality.
5. Keep code and comments in English.
6. Focus on modularization and context reduction only.

---

# Completion Criteria

The task is complete when:

1. database.py is split into modular query files
2. web_server.py is reduced to a thin server entry file
3. route logic is separated into domain modules
4. no backend file exceeds approximately 400 lines
5. the system still runs and APIs behave identically
6. docs/BACKEND_REFACTOR_CONTEXT_OPTIMIZATION.md exists
