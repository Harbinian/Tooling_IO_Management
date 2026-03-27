# Human E2E Skill Validation Report

- Date: 2026-03-30 14:02
- Scope: `.skills/human-e2e-tester` + `test_runner`
- Database: `test_reports/e2e_sensing.db`
- Baseline:
  - `test_reports/HUMAN_E2E_SKILL_FINAL_RETEST_REPORT_20260327.md`
  - `test_reports/HUMAN_E2E_STEP10_REPORT_20260327_1530.md`

## Executive Conclusion

Current effective rating remains: **4/10**.

Reason:
- The latest completed run still passes 4 of the 6 hard validation checks.
- The latest database activity also includes unfinished `running` runs, so the newest raw run cannot be treated as a final score.

## Validation Basis

Validation script:
- `python test_runner/validate_sensing_run.py`

Hard thresholds from `test_runner/validate_sensing_run.py`:
- `snapshots >= 10`
- `workflow_positions >= 5`
- `consistency_checks >= 5`
- `pass_rate >= 80%`
- `critical_anomalies = 0`
- `high_anomalies <= 2`

Repository scoring convention used by existing reports:
- 6 checks passed partially maps to current reported score style
- 4 passed / 2 failed is recorded as **4/10**

## Current Run State

Most recent runs in `test_runs`:

| run_id | started_at | status | test_type |
|---|---|---|---|
| `4268397b-b666-4b53-9fe0-08b41b279bfa` | 2026-03-30T14:00:12.399842 | `running` | `full_workflow` |
| `51dee916-c9bb-4858-acf2-4aabbb63ac84` | 2026-03-30T14:00:12.230185 | `running` | `full_workflow` |
| `7ddbb582-220c-438d-ada8-acd08fc25a59` | 2026-03-30T13:51:06.968372 | `interrupted` | `full_workflow` |
| `0378d062-f49d-40a4-81c7-b5955d9c8551` | 2026-03-30T13:51:06.774073 | `completed` | `full_workflow` |

Interpretation:
- The newest run is not final because it is still marked `running`.
- The most recent completed run is the correct reference for a stable validation score.

## Latest Raw Run Check

Raw latest run:
- `run_id = 51dee916-c9bb-4858-acf2-4aabbb63ac84`

Validation result:
- `snapshots = 19` -> PASS
- `workflow_positions = 19` -> PASS
- `consistency_checks = 38` -> PASS
- `pass_rate = 0%` -> FAIL
- `critical_anomalies = 33` -> FAIL
- `high_anomalies = 36` -> FAIL

This run is **not suitable as final scoring evidence** because the associated `test_runs.status` is still `running`.

## Latest Completed Run Check

Stable reference run:
- `run_id = 0378d062-f49d-40a4-81c7-b5955d9c8551`

Validation result:
- `snapshots = 32` -> PASS
- `workflow_positions = 32` -> PASS
- `consistency_checks = 64` -> PASS
- `pass_rate = 100%` -> PASS
- `critical_anomalies = 53` -> FAIL
- `high_anomalies = 68` -> FAIL

Summary:
- Passed checks: `4 / 6`
- Effective score by repository convention: **4/10**
- Threshold result: **INVALID / 未达标**

## Comparison With 2026-03-27 Baseline

Compared with the previous final retest:
- The effective score did not improve beyond **4/10**
- Persistent sensing data is now clearly being written for completed runs
- The blocking issue is still anomaly volume, not lack of row creation

What changed in evidence quality:
- Current DB contains multiple real runs and populated sensing tables
- This is better than the older state where persistence could be entirely absent

What still blocks 8/10:
- `critical_anomalies` must be `0`, current completed run is `53`
- `high_anomalies` must be `<= 2`, current completed run is `68`

## Key Risks

1. Unfinished runs distort the "latest" validation result.
2. The score remains capped by anomaly explosion even when workflow persistence is active.
3. The repository contains a scoring-formula mismatch:
   - `test_runner/validate_sensing_run.py` validates 6 hard gates
   - older step10 documentation also mentions a 10-point formula tied to an `operations` table
   - the current database does not contain an `operations` table

## Final Verdict

As of 2026-03-30 14:02, the `human-e2e-tester` skill should still be considered:
- **Validated as runnable**
- **Validated as persisting sensing data**
- **Not validated as 8/10 ready**
- **Current effective score: 4/10**
