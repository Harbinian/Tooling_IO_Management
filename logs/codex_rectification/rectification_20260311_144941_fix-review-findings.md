# Codex Rectification Record

## Basic Information
- Time: 2026-03-11 14:49:41 +08:00
- Executor: Codex
- Summary: Fix review findings in API validation, notification persistence, health response, and order correction flow.

## Trigger
- Source: code review
- Context: Fix the issues identified in the previous review of `web_server.py` and `database.py`.

## Defect
- Description: The service hard-coded `SECRET_KEY`, converted bad request input into 500s, allowed empty keeper confirmations to advance state, tied webhook sending to Feishu app tokens, returned 200 on database-unhealthy health checks, risked duplicate order numbers under collisions, and fetched notification IDs via `@@IDENTITY`.
- Impact: These defects could cause security/config drift, incorrect workflow transitions, unreliable notifications, misleading health probes, and incorrect notification record updates.

## Correction
- Files Updated: `web_server.py`, `database.py`
- Change Summary: Read `SECRET_KEY` from centralized settings; added JSON and pagination validation with 400 responses; required non-empty keeper confirmation items; removed the webhook-token gate; returned 503 when DB health fails; retried order creation after duplicate-key collisions; changed notification inserts to `OUTPUT INSERTED.id` on the same connection.

## Verification
- Performed: `C:\Users\charl\AppData\Local\Programs\Python\Python312\python.exe -m py_compile web_server.py database.py config\settings.py utils\feishu_api.py`
- Result: Passed.

## Notes
- Concurrency on order numbers is reduced via duplicate-key retry. A database sequence or transactional allocator would still be a stronger long-term design.
