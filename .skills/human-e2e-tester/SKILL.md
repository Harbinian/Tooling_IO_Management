# Human E2E Tester

命令触发: /human-e2e-tester / Command Trigger: /human-e2e-tester

---

name: human-e2e-tester
executor: Claude Code
description: Simulate real human end-to-end system usage across roles to discover workflow defects, RBAC issues, usability problems, and integration failures.

PURPOSE

This skill performs human-simulated exploratory testing of the system.

Unlike automated test scripts, this skill tries to behave like a real user.

It verifies whether the system is actually usable and whether workflows make sense from a human perspective.

This skill is especially useful before releases and after major feature changes.

WHEN TO USE

Use this skill when:

- a major feature is completed
- RBAC logic changes
- workflow states change
- frontend navigation changes
- before pilot release
- before production release

This skill should NOT be used for writing code.

Its purpose is discovery and validation.

CORE TEST AREAS

The skill must evaluate:

authentication flow
RBAC permission behavior
organization data scope
workflow usability
navigation clarity
UI state feedback
notification behavior
audit log generation
dashboard correctness

STEP 1 — IDENTIFY TEST ROLES

Detect available roles such as:

Team Leader
Keeper
Planner
System Administrator
Auditor

Each role must be tested independently.

STEP 2 — SIMULATE REAL USER ACTIONS

**CRITICAL CONSTRAINT: TEST DATA RESTRICTION**

All testing MUST use ONLY the following test tooling data:

| Field | Value |
|-------|-------|
| Serial Number (序列号) | T000001 |
| Tooling Drawing Number (工装图号) | Tooling_IO_TEST |
| Tool Name (工装名称) | 测试用工装 |
| Model (机型) | 测试机型 |

**DO NOT use any other tooling data for testing!**

- DO NOT use fuzzy search with other keywords
- DO NOT try to search for other tools
- Only search and operate with the exact data above
- If the test tool is not found, report it as a test issue

Simulate typical actions such as:

login
open dashboard
navigate through sidebar
search tools (use: T000001 or Tooling_IO_TEST)
create an order (with test tool only)
submit an order
keeper confirmation
transport workflow
final confirmation
view dashboard metrics
view audit logs

These actions must be evaluated as a human would experience them.

STEP 3 — CHECK WORKFLOW COMPLETENESS

Ensure the complete workflow works:

Create Order
Submit Order
Keeper Confirmation
Transport
Final Confirmation
Order Closed

Verify that:

state transitions are valid
invalid transitions are blocked
UI feedback is clear
the user understands what to do next

STEP 4 — VERIFY RBAC BEHAVIOR

Check that roles behave correctly.

Verify:

menu visibility
button visibility
page access
data scope filtering
forbidden actions

Users must not see actions they cannot perform.

STEP 5 — VERIFY UI EXPERIENCE

Evaluate:

navigation clarity
empty states
error messages
loading indicators
button placement
action discoverability

Identify areas where users might become confused.

STEP 6 — VERIFY NOTIFICATION AND LOGGING

Confirm that:

notification records are created
Feishu delivery attempts are recorded
audit logs are written
workflow transitions produce logs

Failures should be diagnosable.

STEP 7 — CLASSIFY ISSUES

All issues must be categorized:

Critical
High
Medium
Low

Include:

description
affected module
recommended fix

STEP 8 — GENERATE TEST REPORT

Create:

docs/HUMAN_SIMULATED_E2E_TEST_REPORT.md

The report must include:

roles tested
scenarios executed
successful workflows
usability problems
RBAC issues
workflow blockers
notification or logging issues
recommended fixes

EXPECTED RESULT

After execution:

the system has been tested from a human perspective
workflow usability is validated
hidden blockers are discovered
a structured test report is generated