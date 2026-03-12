name: scripted-e2e-builder
executor: Codex
description: Convert validated human workflows into automated end-to-end and regression test scripts for frontend and backend.

---

# Scripted E2E Builder

## Purpose

This skill converts manually validated workflows into repeatable automated tests.

It takes the results from exploratory testing (such as reports produced by human-e2e-tester) and transforms them into structured automated tests.

The goal is to ensure that critical system workflows remain stable as the system evolves.

This skill focuses on:

- regression protection
- workflow verification
- RBAC validation
- API stability
- frontend navigation stability

---

# When To Use This Skill

Use this skill when:

- a human-simulated test has validated workflows
- a bug has been fixed and needs regression protection
- a new workflow feature has been completed
- a release candidate build is being prepared
- before pilot release or production release

This skill should **not invent new workflows**.  
It should only convert verified workflows into automated tests.

---

# Inputs

The skill should inspect sources such as:

docs/HUMAN_SIMULATED_E2E_TEST_REPORT.md

or other validation documents describing confirmed working scenarios.

These documents describe real user flows that should be protected by regression tests.

---

# Core Responsibilities

The skill must:

1. identify critical workflows
2. translate them into automated test scenarios
3. generate maintainable test scripts
4. ensure tests validate both success paths and permission rules
5. ensure tests fail clearly when system behavior breaks

---

# Step 1 — Identify Critical Workflows

**CRITICAL CONSTRAINT: TEST DATA RESTRICTION**

All automated tests MUST use ONLY the following test tooling data:

| Field | Value |
|-------|-------|
| Serial Number (序列号) | T000001 |
| Tooling Drawing Number (工装图号) | Tooling_IO_TEST |
| Tool Name (工装名称) | 测试用工装 |
| Model (机型) | 测试机型 |

**DO NOT use any other tooling data for testing!**

- DO NOT use fuzzy search with other keywords
- DO NOT create tests with other tools
- Only use the exact data above for test data
- Tests should verify that this specific test tooling can be found and operated

Extract key scenarios such as:

User login

Tool search (search for: T000001 or Tooling_IO_TEST)

Order creation (with test tool only)

Order submission

Keeper confirmation

Transport workflow

Final confirmation

Dashboard metrics visibility

RBAC permission checks

These flows represent the core business system.

---

# Step 2 — Build Backend API Tests

Create automated API-level tests to verify:

authentication endpoints

order lifecycle endpoints

tool search endpoints

dashboard metrics endpoints

RBAC permission enforcement

Tests must validate:

correct status codes  
correct response structure  
correct permission behavior

---

# Step 3 — Build Frontend End-to-End Tests

Use an E2E testing approach suitable for modern frontend systems.

Recommended approach:

Playwright-style tests or equivalent browser automation.

Automated flows should simulate:

login

navigation via sidebar

opening dashboard

creating an order

submitting an order

keeper confirmation flow

viewing audit logs

These tests should verify visible UI states.

---

# Step 4 — Validate RBAC Scenarios

Automated tests must confirm:

Admin can access all system features.

Keeper can process assigned orders but cannot create certain administrative actions.

Team leader can create and submit orders.

Unauthorized users cannot access protected pages.

Tests should confirm both allowed and denied behavior.

---

# Step 5 — Validate Data Scope

Verify that:

users only see data within their organization scope

orders from other organizations are not visible

dashboard metrics reflect scoped data correctly

This protects multi-team environments.

---

# Step 6 — Add Regression Coverage

Ensure the following features remain protected by tests:

order workflow state transitions

notification creation

audit logging generation

dashboard metric calculations

tool location updates

Any regression must cause tests to fail clearly.

---

# Step 7 — Organize Test Structure

Tests should be organized logically, for example:

tests/api/

tests/e2e/

tests/rbac/

tests/workflows/

This ensures maintainability and readability.

---

# Step 8 — Ensure Test Stability

Tests must:

avoid brittle selectors

wait for UI readiness where necessary

fail with meaningful messages

not depend on unstable data ordering

Use realistic but deterministic test data where possible.

---

# Step 9 — Generate Documentation

Create a documentation file:

docs/AUTOMATED_TEST_SUITE.md

The document must include:

list of automated workflows

API tests implemented

E2E tests implemented

RBAC scenarios tested

test execution instructions

guidelines for adding new regression tests

---

# Expected Outcome

After execution:

critical workflows are protected by automated tests

frontend navigation is verified

RBAC rules are automatically validated

regressions become easier to detect

a maintainable automated test suite exists