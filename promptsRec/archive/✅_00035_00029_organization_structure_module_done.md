Primary Executor: Codex
Task Type: Feature Implementation
Category: Platform Infrastructure
Goal: Implement the organization structure module so the system can manage organizational hierarchy and bind users, roles, and data scope to real organizations.
Execution: RUNPROMPT

---

# Context

The system has already completed or is completing:

- RBAC design
- RBAC database schema
- RBAC initial data
- architecture index
- user authentication system

Relevant documents:

docs/ARCHITECTURE_INDEX.md  
docs/RBAC_DESIGN.md  
docs/RBAC_DATABASE_SCHEMA.md  
docs/RBAC_INIT_DATA.md  

Before implementation, load these documents to ensure:

- organization model consistency
- RBAC compatibility
- correct data scope design
- correct user-role-organization relationship

The project now needs a real organization structure module.

Without organization structure:

- data scope control is incomplete
- user roles cannot be attached to business units properly
- order visibility cannot be restricted by organization
- future enterprise integration will be unstable

This task implements the first version of the organization structure module.

---

# Objectives

Implement a minimal but extensible organization structure system.

The system must support:

- organization creation and storage
- hierarchical parent-child structure
- organization query
- organization tree retrieval
- user association with organizations
- role assignment with organization context
- future support for RBAC data scope enforcement

---

# Required Components

Implement the following components.

---

# 1 Organization Service

Create a backend organization service.

Possible location:

backend/services/org_service.py

Responsibilities:

- create organization
- update organization
- query organization list
- query organization detail
- build organization tree
- validate parent-child structure
- support organization lookup by org_id

---

# 2 Organization APIs

Implement APIs such as:

GET /api/orgs  
GET /api/orgs/tree  
GET /api/orgs/{org_id}  
POST /api/orgs  
PUT /api/orgs/{org_id}

Use the existing backend style and route structure.

Requirements:

- return organization list
- return organization tree
- support parent-child hierarchy
- validate invalid parent references
- prevent obvious structural conflicts

Do not redesign the backend API framework.

---

# 3 Organization Tree Logic

Implement organization tree building using the real schema.

The system must support hierarchy such as:

company  
factory  
workshop  
team  
warehouse  
project_group

Use the real schema defined in:

docs/RBAC_DATABASE_SCHEMA.md

Do not invent a separate org model.

---

# 4 User-Organization Integration

Ensure users can be associated with organizations.

At minimum support:

- sys_user.default_org_id usage
- organization lookup for current user
- ability to resolve current user organization context

If additional relation handling is needed, keep it consistent with the current RBAC schema and avoid overengineering.

---

# 5 Role-Organization Context

Ensure role assignment can use organization context correctly.

The system already has:

sys_user_role_rel

Use the org-related fields in that relation to support:

- same user having different roles in different organizations
- data scope enforcement later
- business workflow role identity by organization

Implement the necessary query utilities.

---

# 6 Data Scope Preparation

This task does not need to fully implement data scope filtering across all business APIs yet.

However, it must prepare the system to support later logic such as:

- current user can only see orders in own org
- keeper can only see assigned org or warehouse orders
- planner can see org and children

At minimum:

- expose organization information in user context
- make organization resolution utilities available
- document how RBAC data scope will use organization data

---

# 7 Initial Organization Bootstrap

Provide a documented way to create initial organization data.

Example hierarchy should include at least:

- company
- factory
- workshop
- team
- warehouse

This may be done via:

- SQL initialization examples
- API usage example
- seed script if that matches the project style

Do not hardcode one fixed enterprise structure into the core logic.

---

# 8 Frontend Organization Support

Provide the minimum frontend support needed for future integration.

At minimum:

- organization tree API should be callable by frontend
- organization list should be usable in forms or admin pages later

Do not build a full organization management UI yet unless the existing project structure already expects it.

This task is primarily backend/platform focused.

---

# 9 Validation Rules

Implement at least these validations:

- org_id uniqueness
- no missing parent if parent_org_id is provided
- no self-parenting
- no obvious hierarchy corruption in simple update cases
- disabled organizations should remain queryable where needed but clearly marked

---

# 10 Documentation

Create:

docs/ORG_STRUCTURE_IMPLEMENTATION.md

This document must include:

1. organization schema usage
2. API list
3. organization tree logic
4. user-organization relationship handling
5. role-organization context handling
6. future data scope usage notes
7. initialization guidance

---

# Constraints

Do not redesign RBAC.

Use the existing organization-related schema from:

docs/RBAC_DATABASE_SCHEMA.md

Do not invent a second organization table.

Keep the implementation consistent with:

docs/RBAC_DESIGN.md

Keep the code and comments in English.

Keep the changes minimal, modular, and production-oriented.

---

# Completion Criteria

The task is complete when:

1. organization APIs work
2. organization tree retrieval works
3. user organization context can be resolved
4. role assignments can be interpreted with organization context
5. future data scope logic is technically supported
6. docs/ORG_STRUCTURE_IMPLEMENTATION.md exists
