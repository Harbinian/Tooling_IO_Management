# Human E2E Skill Capability Audit

Date: 2026-03-26
Scope: `.skills/human-e2e-tester` persistent sensing + human-like E2E capability

## Conclusion
Current status is framework-present but not fully wired for real persistent sensing + humanized E2E.

Overall rating: 4/10

## Key Findings
1. Report command path is broken:
   - `test_runner/commands.py` exposes `report()` and calls `run_command("report")`.
   - `test_runner/test_runner_agent.py` does not accept `report` in `--command` choices.
   - Runtime check confirmed `invalid choice: 'report'`.

2. Playwright runner does not actually integrate sensing persistence:
   - `test_runner/playwright_e2e.py` imports `start/advance/status/stop` but does not call them.
   - No `SensingOrchestrator.snapshot_before/snapshot_after` integration in execution flow.

3. `sensing_integration.py` snapshot commands are placeholders:
   - Explicitly states it cannot receive real driver object.
   - So CLI integration cannot perform real page sensing independently.

4. Observer API style mismatch:
   - `.skills/human-e2e-tester/sensing/page_observer.py` uses Selenium-style `find_element(s)_by_css_selector`.
   - This does not directly match Playwright `Page` API.

5. Dual database paths cause split state:
   - Sensing default DB: `test_reports/e2e_sensing.db`.
   - Agent default DB: `test_runner/test_reports/e2e_sensing.db`.
   - Runtime data is fragmented across two SQLite files.

6. Mandatory port precheck in skill doc is not enforced in runner script:
   - Skill requires abort when 8150/8151 are unavailable.
   - `playwright_e2e.py` currently has no implemented port guard.

## Verified Working Part
- `test_runner_agent` state commands (`start/status/advance/stop`) run and persist basic state.

## Ratings
- Persistence state machine: 6/10
- Real sensing: 3/10
- Human-like E2E automation: 6/10
- End-to-end persistent sensing + human E2E: 4/10

## Next Step
After Claude finishes script updates, re-run capability verification against the same checklist and compare delta.