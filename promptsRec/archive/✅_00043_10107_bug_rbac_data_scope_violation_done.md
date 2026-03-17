Primary Executor: Codex
Task Type: Bug Fix
Stage: 107
Goal: Fix RBAC data scope violation where role-to-org bindings are not preserved during scope resolution
Execution: RUNPROMPT

---

# Context

The repository has a documented RBAC model in `docs/RBAC_DESIGN.md` that defines:
- Users may have multiple roles in different organizations
- Data scope should be constrained by specific role assignments

However, the current implementation in `backend/services/rbac_data_scope_service.py` violates this model.

---

# Problem

## Issue 1: Role-to-Org Binding Not Preserved

**File**: `backend/services/rbac_data_scope_service.py:80, 97`

**Current Behavior**:
- `_resolve_scope_context()` loads all role scopes for the user
- Then merges every discovered scope type into one set
- Once `ORG` or `ORG_AND_CHILDREN` appears, the code builds `direct_org_ids` from `current_org`, `default_org`, and every entry in `role_orgs`
- There is no preservation of the role-to-org binding

**Impact**:
- A user with one org-limited role and another role in a different organization receives the union of both organizations
- This is an authorization expansion, not just a UI inconsistency

**Expected Behavior**:
- Carry role-to-org bindings through scope resolution
- Evaluate scope per role assignment, then union only the data actually granted by each assignment

---

## Issue 2: Order Visibility Based on Participants

**File**: `backend/services/rbac_data_scope_service.py:136, 148, 171, 177`

**Current Behavior**:
- For `ORG` and `ORG_AND_CHILDREN`, the SQL filter and in-memory matcher allow an order when `initiator_id`, `keeper_id`, or `transport_assignee_id` belongs to the allowed org user set
- An order created for another organization becomes visible to org A users as soon as a keeper or transporter from org A touches it

**Impact**:
- Data isolation becomes participant-based instead of organization-owned
- Visibility can grow over time because workflow participants change

---

# References

- `docs/RBAC_DESIGN.md` - RBAC design specification
- `docs/RBAC_DATABASE_SCHEMA.md` - Database schema for RBAC
- `docs/ORG_SCOPED_ORDER_DATA_ACCESS.md` - Order data access documentation

---

# Requirements

1. Fix `_resolve_scope_context()` to preserve role-to-org bindings
2. Evaluate scope per role assignment, not globally
3. Fix order visibility to be based on organization ownership, not participants
4. Ensure multi-organization users only see data from their specific role assignments

---

# Verification

After fix:
- Multi-org users should only see data from the organization context of their specific role
- Order visibility should be based on order's organization ownership, not workflow participants
- No unauthorized data exposure should occur
