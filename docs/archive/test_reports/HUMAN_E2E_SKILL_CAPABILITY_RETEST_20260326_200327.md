# Human E2E Skill Capability Retest

Date: 2026-03-26
Baseline: `test_reports/HUMAN_E2E_SKILL_CAPABILITY_AUDIT_20260326_194304.md`

## Retest Scope
Recheck persistent sensing + human-like E2E real execution capability after Claude script updates.

## Runtime Verification
- Backend 8151 reachable: TRUE
- Frontend 8150 reachable: TRUE
- Ran: `python test_runner/api_e2e.py`
  - Result: completed with failures (exit code 1)
  - Failures included tool occupancy and several expectation mismatches

## Findings (Delta vs Baseline)

### 1) Report command path: NOT FIXED
- `test_runner/commands.py` still calls `run_command("report")`.
- `test_runner/test_runner_agent.py` still only accepts: start/resume/status/stop/advance.
- Runtime check:
  - `python test_runner/test_runner_agent.py --command report` -> invalid choice
  - `from test_runner.commands import report; report()` -> JSONDecodeError

### 2) Sensing integration into runners: NOT FIXED
- `test_runner/playwright_e2e.py` and `test_runner/api_e2e.py` import agent commands but do not call start/advance/status/stop in flow.
- No `SensingOrchestrator.snapshot_before/snapshot_after` invocation in these runners.

### 3) sensing_integration snapshot API: NOT FIXED
- Still placeholder message: "snapshot_before called - pass driver object in actual execution".
- Still notes it cannot pass real driver for `snapshot_after`.

### 4) Observer API mismatch (Playwright compatibility): NOT FIXED
- `.skills/human-e2e-tester/sensing/page_observer.py` still uses Selenium-style APIs (`find_element(s)_by_css_selector`).

### 5) DB split/fragmentation: NOT FIXED
- Both DBs still exist:
  - `test_reports/e2e_sensing.db`
  - `test_runner/test_reports/e2e_sensing.db`
- Data remains fragmented and sensing tables remain mostly empty.

### 6) Port guard implementation: PARTIALLY IMPROVED
- New `api_e2e.py` checks backend health endpoint before run.
- But skill-level mandatory 8150/8151 abort rule is still documented-only and not enforced by `playwright_e2e.py`.

## Current Capability Rating
- Persistence state machine: 6/10
- Real sensing: 3/10
- Human-like E2E automation: 6/10
- End-to-end persistent sensing + human E2E: 4/10 (unchanged)

## Conclusion
Core target capability (persistent sensing + humanized execution in one reliable pipeline) is still not truly achieved.