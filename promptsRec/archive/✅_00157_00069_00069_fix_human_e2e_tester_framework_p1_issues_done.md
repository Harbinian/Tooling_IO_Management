# Human E2E Tester 框架 P1 问题修复

Primary Executor: Claude Code
Task Type: Feature Development
Priority: P1
Stage: 00069
Goal: 修复 human-e2e-tester 框架的 P1 级问题，实现感知持久化与执行流程闭环
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

根据 `test_reports/HUMAN_E2E_SKILL_FINAL_RETEST_REPORT_20260327.md` 的复测结论，Human E2E Tester 框架存在以下 P1 级问题：

### P1-1: `report` 命令链路断裂

**现象**：
- `commands.py` 暴露 `report()` 函数并调用 `run_command("report")`
- `test_runner_agent.py` 的 `--command` 不接受 `report`
- 实测：`python test_runner/test_runner_agent.py --command report` 报 invalid choice

**影响**：无法通过统一命令接口获取 Agent 报告

### P1-2: 执行脚本与感知持久化未闭环

**现象**：
- `api_e2e.py`、`playwright_e2e.py` 导入了 agent commands，但未实际调用状态推进
- 未看到 `SensingOrchestrator.snapshot_before/snapshot_after` 的执行链路

**影响**：测试在跑但感知快照/异常/一致性记录不会稳定落库

### P1-3: `sensing_integration.py` 快照命令仍是占位

**现象**：
- 明确返回"需在实际执行中传入 driver"
- 注释明确"这里无法传入真实的 driver"

**影响**：CLI 集成层无法独立完成真实感知采集

---

## Required References / 必需参考

1. `test_runner/test_runner_agent.py` - Agent 核心逻辑
2. `test_runner/commands.py` - 命令行工具
3. `test_runner/api_e2e.py` - API E2E 执行器
4. `test_runner/playwright_e2e.py` - Playwright E2E 执行器
5. `.skills/human-e2e-tester/sensing/orchestrator.py` - 感知协调器
6. `.skills/human-e2e-tester/sensing/storage.py` - 存储层
7. `.skills/human-e2e-tester/sensing_integration.py` - CLI 集成

---

## Core Task / 核心任务

### P1-1: 补齐 `report` 命令

在 `test_runner_agent.py` 中添加 `report` 命令分支：

1. 添加 `_cmd_report` 方法
2. 从 SQLite 数据库读取测试运行摘要
3. 返回格式化的报告 JSON

在 `commands.py` 中修复 `report()` 函数：
1. 确保与 agent 的 report 输出 schema 对齐
2. 处理可能的 JSONDecodeError

### P1-2: Runner 强制接入 agent + sensing

修改 `playwright_e2e.py` 和/或 `api_e2e.py`：

1. 每步骤固定顺序：
   ```
   snapshot_before -> action -> snapshot_after -> advance
   ```

2. 失败场景保证 `advance`/`stop` 仍执行（try-finally）

3. 初始化 SensingOrchestrator 并传入 db_path

### P1-3: 修复 sensing_integration.py

`sensing_integration.py` 应作为感知报告生成工具，而不是执行工具：

1. 从 SQLite 读取已保存的快照和异常数据
2. 生成格式化的感知报告
3. 不需要传入 driver

---

## Required Work / 必需工作

### P1-1: 修复 report 命令
- [ ] 在 `test_runner_agent.py` 添加 `report` 命令分支
- [ ] 在 `commands.py` 修复 `report()` 函数
- [ ] 测试：`python test_runner/test_runner_agent.py --command report`

### P1-2: 连接执行与感知
- [ ] 修改 `playwright_e2e.py` 接入 SensingOrchestrator
- [ ] 在每个测试步骤后调用 `snapshot_after` 和 `advance`
- [ ] 使用 try-finally 确保 stop/advance 在失败时仍执行

### P1-3: 修复 sensing_integration.py
- [ ] 将 `sensing_integration.py` 重构为报告生成器
- [ ] 从 SQLite 读取数据，生成感知报告
- [ ] 不再尝试传入 driver

### 统一数据库路径
- [ ] 确认 `test_runner/commands.py` 和 `test_runner_agent.py` 使用相同的 DB_PATH
- [ ] 确认 `e2e_sensing.db` 路径统一

---

## Constraints / 约束条件

- **保持向后兼容**：现有命令（start, resume, status, stop）必须继续工作
- **单一数据源**：所有状态必须写入单一 SQLite 数据库
- **测试脚本可独立运行**：playwright_e2e.py 应可在没有感知层的情况下运行基本测试

---

## Completion Criteria / 完成标准

1. `python test_runner/test_runner_agent.py --command report` 返回有效的 JSON 报告
2. `playwright_e2e.py` 在运行时通过 advance 更新 Agent 状态
3. `sensing_integration.py` 可以从 SQLite 读取数据生成报告
4. 运行一次测试后，SQLite 中有快照/异常/一致性检查记录
5. 所有命令（start, resume, status, stop, report）均可正常工作
