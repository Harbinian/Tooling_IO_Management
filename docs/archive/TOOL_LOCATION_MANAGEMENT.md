# Tool Location Management

## Inspected Schema Summary

The existing repository and schema references show:

- tool master current location is stored in `工装身份卡_主表.[库位]`
- tool master history/context is available in `工装身份卡_主表.[应用历史]`
- order header stores `target_location_text`
- order item records store keeper-confirmed location fields
- location dictionary data exists in `工装位置表`

This implementation treats `工装身份卡_主表.[库位]` as the long-term authoritative current location field for tool search and general lookup.

## Authoritative Source Rules

Current authoritative location source by stage:

| Stage | Authoritative Source |
|---|---|
| normal inventory state | tool master `库位` |
| keeper confirmation | keeper-confirmed location on order item acts as the locked pickup/storage reference |
| transport in progress | workflow item location is treated as the temporary authoritative source |
| transport completed outbound | order target location becomes the resolved current location |
| transport completed inbound | keeper-confirmed storage location becomes the resolved current location |
| final confirmed | tool master `库位` should already match the workflow target, and final confirm re-applies it idempotently |

## Location Lifecycle

Minimum lifecycle covered by the current implementation:

1. tool starts at stored master location
2. keeper confirmation records the actual pickup/storage location per item
3. transport start keeps workflow ownership in the transport stage
4. transport completion writes the target or confirmed storage location back to tool master
5. final confirmation re-applies the expected final location for consistency

## Location Service Design

Primary module:

- `backend/services/tool_location_service.py`

Current responsibilities:

- resolve tool master location
- resolve workflow-aware order item location
- compute milestone-based target location
- update tool master location
- write non-blocking audit records for location changes

## Workflow Integration Points

Current integration points:

- transport completion -> apply location updates
- final confirmation -> re-apply location updates for consistency

Keeper confirmation already captures location context in order item data, so it acts as the source input for later transport/final updates.

## Audit Logging Behavior

Location writes generate audit entries with:

- order id
- operation type `location_update`
- operator identity
- previous location
- new location
- remark containing the tool code and milestone

Audit failures remain non-blocking.

## Validation Scenarios

Validated by implementation and syntax review:

1. tool master lookup by tool code
2. workflow-aware location resolution
3. outbound location writeback on transport completion
4. idempotent re-application on final confirmation
5. search consistency preservation through master `库位` updates

Environment-dependent validation still required:

- live SQL Server updates against `工装身份卡_主表`
- actual order data containing representative outbound and inbound items
- manual verification through tool search and order detail APIs

## Limitations and Assumptions

- this implementation assumes `工装身份卡_主表.[库位]` is the authoritative persisted location field
- `工装位置表` is not yet used for strict location validation beyond being the known location dictionary table
- no separate history table was introduced; audit log entries provide the minimal location-change history for now
- transport-in-progress visibility currently relies on workflow context rather than immediate master-location mutation
