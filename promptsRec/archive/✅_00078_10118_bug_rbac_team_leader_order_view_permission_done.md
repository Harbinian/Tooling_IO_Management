Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 118
Goal: Add order:view permission to team_leader role
Dependencies: None
Execution: RUNPROMPT

---

## Context

During the E2E test (2026-03-18, Test Sequence: T000001), the RBAC permission test revealed that team_leader role lacks the `order:view` permission, which prevents team leaders from viewing order details.

**Test Error:**
```
missing required permission: order:view
```

**Affected Workflow:**
- Team Leader attempts to view order details éˆ«?Permission denied

## Required References

1. `docs/RBAC_DESIGN.md` - RBAC design documentation
2. `docs/DB_SCHEMA.md` - Database schema documentation
3. `docs/API_SPEC.md` - API specification
4. Existing RBAC configuration in the codebase (search for role definitions)

## Core Task

Add `order:view` permission to the team_leader role configuration so that team leaders can view order details.

## Required Work

1. **Investigate RBAC Configuration:**
   - Find where role-permission mappings are defined in the codebase
   - Identify the current permissions assigned to team_leader role
   - Understand how permissions are stored (database table or config file)

2. **Add Missing Permission:**
   - Add `order:view` permission to team_leader role
   - Ensure the permission is properly persisted in the database or configuration

3. **Verify the Fix:**
   - Test that team_leader can now view order details via API
   - Ensure no other roles are affected

## Constraints

- Must follow the existing RBAC schema and patterns in the codebase
- Do not modify other role permissions without justification
- Must preserve all existing permissions for team_leader
- Use the exact permission name `order:view` as shown in the error message

## Completion Criteria

- [ ] Team Leader role has `order:view` permission in the configuration
- [ ] Team Leader can successfully view order details via API
- [ ] No regression in other role permissions
