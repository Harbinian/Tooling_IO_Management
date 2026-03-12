Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 115
Goal: Add missing confirmation tracking fields to order detail table
Dependencies: None
Execution: RUNPROMPT

---

## Context

Code review found that the order detail table (工装出入库单_明细) lacks fields for tracking keeper confirmation at the line-item level. When a keeper confirms or partially confirms items, there is no record of WHO confirmed WHICH item and WHEN, or WHY an item was rejected.

## Required References

- `backend/database/tool_io_queries.py` — table creation and queries
- `backend/database/core.py` — database manager
- `backend/services/tool_io_service.py` — keeper_confirm function
- `AI_DATABASE_MODEL.md` — current schema documentation

## Core Task

Add confirmation tracking fields to the order detail table and update the keeper confirmation logic to populate them.

## Required Work

1. Inspect `tool_io_queries.py` to find the exact table creation SQL for 工装出入库单_明细
2. Inspect `tool_io_service.py` keeper_confirm() to understand current confirmation logic
3. Add new columns to 工装出入库单_明细 (use ALTER TABLE if table exists, include in CREATE for new installs):
   - 确认人 (NVARCHAR) — user ID of confirmer
   - 确认时间 (DATETIME) — confirmation timestamp
   - 驳回原因 (NVARCHAR) — rejection reason (nullable)
4. Update keeper_confirm() in service layer to populate these fields
5. Update get_order_detail() to return the new fields
6. Update `AI_DATABASE_MODEL.md`

## Constraints

- Do NOT drop or recreate existing tables (use ALTER TABLE for migration)
- Do NOT change the order master table
- Do NOT change API response structure (add new fields, don't remove existing ones)
- New columns must be nullable (backward compatible with existing data)

## Acceptance Tests

- Existing orders without new fields still load correctly (null values)
- After keeper confirmation, 确认人 and 确认时间 are populated
- After item rejection, 驳回原因 is populated
- Order detail API returns new fields
- No errors on application startup with existing database

## Completion Criteria

- [ ] ALTER TABLE migration added for existing databases
- [ ] CREATE TABLE updated for fresh installs
- [ ] keeper_confirm() populates new fields
- [ ] get_order_detail() returns new fields
- [ ] Backward compatible with existing data
- [ ] AI_DATABASE_MODEL.md updated with new fields
