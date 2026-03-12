Primary Executor: Codex
Task Type: Bug Fix
Stage: 108
Goal: Add organization ownership field to order schema to satisfy the documented RBAC data-scope model
Execution: RUNPROMPT

---

# Context

The RBAC design in `docs/RBAC_DESIGN.md` and `docs/RBAC_DATABASE_SCHEMA.md` defines organization and data scope as first-class RBAC concepts.

The current order schema does not support this model.

---

# Problem

**File**: `database.py:1535, 1554`
**File**: `backend/services/tool_io_service.py:40`

**Current Behavior**:
- The `tool_io_orders` schema stores user references (initiator, keeper, transport assignee)
- No `org_id` or organization snapshot exists
- Order creation does not stamp the current organization into the record

**Impact**:
- For users who belong to multiple organizations, a created order cannot later be attributed to the organization context in which it was created
- `ORG` and `ORG_AND_CHILDREN` access control remains inference-based and unstable
- Cannot reliably filter orders by organization

---

# References

- `docs/RBAC_DESIGN.md` - RBAC design specification
- `docs/RBAC_DATABASE_SCHEMA.md` - Database schema for RBAC
- `docs/DB_SCHEMA.md` - Order schema definition

---

# Requirements

1. Add `org_id` field to the `tool_io_orders` table
2. Update order creation to populate `org_id` from the authenticated organization context
3. Migrate historical data with a reasonable default (e.g., user's default org)
4. Update data scope queries to use the new `org_id` field

---

# Verification

After fix:
- New orders should have explicit organization ownership
- Historical orders should have org_id populated
- ORG data scope queries should use org_id for reliable filtering
