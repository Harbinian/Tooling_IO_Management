# Human E2E Skill Validation Rerun Report

- Date: 2026-03-27
- Scope: `.skills/human-e2e-tester` + `test_runner`
- Baseline: previous validation on 2026-03-27

## Executive Conclusion
Current status: **partially fixed**.

Infrastructure and command reliability improved, but the core persistent sensing loop is still not fully active in runtime step flow.

Overall rating: **5/10**.

## What Is Confirmed Fixed
1. `report` command works in `test_runner_agent.py` command set.
2. `test_runner.commands.report()` now returns structured output.
3. Agent DB path unified to `test_reports/e2e_sensing.db`.
4. `playwright_e2e.py` now enforces service readiness on ports 8150/8151.
5. `page_observer.py` migrated to Playwright-compatible query APIs.
6. Runners now invoke agent lifecycle commands (`start/advance/stop`) and orchestrator finalize hook.

## Remaining Critical Gap
1. Persistent sensing records are still not being written during actual run:
   - `snapshots = 0`
   - `anomalies = 0`
   - `consistency_checks = 0`
   - `workflow_positions = 0`
2. Root cause: runners initialize/finalize orchestrator but still do not perform per-step `snapshot_before/snapshot_after` capture calls.

## Runtime Observation
- `python test_runner/api_e2e.py` executes and returns non-zero due to business/data failures (e.g., occupied test tool and RBAC expectation mismatch in some cases).
- This execution still does not produce sensing snapshot/check rows.

## Final Verdict
The latest patch is a meaningful improvement for control plane reliability, but the data plane of sensing (real capture + persistence) remains incomplete.

To declare this skill "persistent-sensing capable", each major test step must execute:
- `snapshot_before`
- action
- `snapshot_after`
- persist and verify row growth in sensing tables.

## Appendix: Fix and Acceptance Checklist

### 目标
把 `human-e2e-tester` 从“可运行脚本”提升为“可验证的持久化嗅探拟人测试系统”。

### 必做修复（按优先级）
1. 打通每步感知采集（P0）
- 在 `api_e2e.py` 和 `playwright_e2e.py` 的关键步骤统一执行：
  - `snapshot_before`
  - 执行动作
  - `snapshot_after`
  - `advance`
- 不允许只初始化/finalize orchestrator 而不采集。

2. 感知落库可见（P0）
- 每次测试运行后，`test_reports/e2e_sensing.db` 至少应有：
  - `snapshots > 0`
  - `consistency_checks > 0`
  - `workflow_positions > 0`
- 若有失败步骤，`anomalies >= 0` 且可解释。

3. 失败路径也要推进状态（P1）
- 任一步骤异常时，仍要调用 `advance` 或 `stop`，避免 run 卡死。
- 保证 run 最终状态可追踪（completed/interrupted）。

4. 端口守卫一致化（P1）
- `playwright_e2e.py` 和 `api_e2e.py` 都执行同级别服务检查。
- 不满足端口条件时，统一 `[ABORT]` 并退出。

5. 报告闭环（P1）
- `test_runner_agent.py --command report` 输出要包含：
  - run_id / state / operation_index
  - anomalies 统计
  - 最近 checkpoint 信息（如有）
- `commands.report()` 直接可用，不抛异常。

### 验收门槛（必须全部满足）
1. 命令链路
- `start/status/advance/report/stop` 全部可执行，返回 JSON。

2. 持久化链路
- 跑一次 `python test_runner/api_e2e.py` 后：
  - `snapshots > 0`
  - `consistency_checks > 0`
  - `workflow_positions > 0`

3. 单库一致性
- 仅使用 `test_reports/e2e_sensing.db` 作为事实库。
- 不再产生 `test_runner/test_reports/e2e_sensing.db` 分叉数据。

4. 回归报告
- 输出一份验收报告到 `test_reports/`，包含：
  - 本次 run_id
  - 关键表计数
  - 失败步骤与原因
  - 与上次对比结论
