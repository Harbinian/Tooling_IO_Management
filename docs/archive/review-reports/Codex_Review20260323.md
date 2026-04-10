# Codex Review 2026-03-23

Repository: `E:\CA001\Tooling_IO_Management`

Review basis:
- reviewer model output from current `review` action
- current workspace paths referenced by findings

## Findings

### 1. High: keeper batch status update payload key mismatches backend contract

Files:
- [frontend/src/pages/tool-io/KeeperProcess.vue](/E:/CA001/Tooling_IO_Management/frontend/src/pages/tool-io/KeeperProcess.vue#L545)

Problem:
- keeper batch status update sends `status` instead of `new_status`
- backend `PATCH /api/tools/batch-status` validates `new_status` as required

Impact:
- keeper-side batch status updates fail with 400 validation errors
- the newly added batch status workflow is non-functional for real users

Recommendation:
- change request payload key from `status` to `new_status` in keeper batch update call
- add an integration test to assert successful request/response contract for batch status updates

### 2. Medium: password client-side checks do not match backend policy

Files:
- [frontend/src/pages/settings/SettingsPage.vue](/E:/CA001/Tooling_IO_Management/frontend/src/pages/settings/SettingsPage.vue#L321)
- [frontend/src/pages/settings/SettingsPage.vue](/E:/CA001/Tooling_IO_Management/frontend/src/pages/settings/SettingsPage.vue#L322)

Problem:
- frontend allows passwords with 6-character minimum
- backend password-change API requires at least 8 characters and uppercase/lowercase/digit composition

Impact:
- users can pass client-side validation but fail server-side
- avoidable password change failures and poor UX

Recommendation:
- align frontend validation to backend password policy (length + composition)
- mirror backend error messaging on client to reduce ambiguity when policy changes

