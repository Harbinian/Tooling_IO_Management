Primary Executor: Codex
Task Type: Bug Fix
Priority: P0
Stage: 10170
Goal: Fix human-e2e-tester persistent sensing loop - snapshot_before/snapshot_after not being called during test steps
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述

`human-e2e-tester` 技能的持久化感知环完全不工作。运行 `python test_runner/api_e2e.py` 后，数据库 `test_reports/e2e_sensing.db` 中所有感知表都是空的：

- `snapshots = 0`
- `anomalies = 0`
- `consistency_checks = 0`
- `workflow_positions = 0`

**根因已确认**：`api_e2e.py` 和 `playwright_e2e.py` 初始化了 `SensingOrchestrator` 并调用了 `finalize()`，但**没有在每个测试步骤中调用 `snapshot_before` 和 `snapshot_after`**。

### 参考报告

- `test_reports/HUMAN_E2E_FIX_ACCEPTANCE_CHECKLIST.md` - 必做修复清单
- `test_reports/HUMAN_E2E_SKILL_VALIDATION_RERUN_20260327_131012.md` - 验证结果（评级 5/10）

### 相关文件

```
test_runner/
├── api_e2e.py              # API E2E 测试入口
├── playwright_e2e.py       # Playwright E2E 测试入口
├── commands.py             # Agent 命令接口
└── test_runner_agent.py    # Agent 核心

.skills/human-e2e-tester/sensing/
├── orchestrator.py         # SensingOrchestrator 感知协调器
├── page_observer.py        # 页面感知层
├── workflow_detector.py     # 工作流感知层
├── anomaly_detector.py      # 异常感知层
├── consistency_verifier.py  # 数据一致性层
└── storage.py              # SQLite 存储

test_reports/e2e_sensing.db # 感知数据库（统一路径）
```

---

## Required References / 必需参考

1. **SensingOrchestrator API** - 读取 `.skills/human-e2e-tester/sensing/orchestrator.py`，理解以下方法的签名和用法：
   - `__init__(db_path, run_id, test_type)`
   - `set_user_context(user_name, role, org_id)`
   - `snapshot_before(driver)` - 操作前快照
   - `snapshot_after(driver, operation, expected_next_status, api_response)` - 操作后快照
   - `finalize()` - 结束测试

2. **当前 Runner 实现** - 读取 `test_runner/api_e2e.py`，找到**所有执行测试步骤的位置**，确认这些位置是否调用了 `snapshot_before/snapshot_after`。

3. **Agent 命令接口** - 读取 `test_runner/commands.py`，理解 `advance(op_name, anomalies_count, critical_count)` 的用法。

4. **数据库 Schema** - 读取 `.skills/human-e2e-tester/sensing/storage.py`，理解 snapshots/anomalies/consistency_checks/workflow_positions 表结构。

---

## Core Task / 核心任务

### Bug: 感知采集调用缺失

**问题本质**：`api_e2e.py` 和 `playwright_e2e.py` 在关键步骤只做了：
1. 调用 API
2. 检查响应
3. **没有**调用 `orchestrator.snapshot_before()` 和 `orchestrator.snapshot_after()`

**正确流程应该是**：
```python
# 每个测试步骤都需要：
1. orchestrator.set_user_context(...)  # 设置当前用户
2. before = orchestrator.snapshot_before(driver)  # 操作前快照
3. 执行动作（API 调用 / 按钮点击）
4. after = orchestrator.snapshot_after(driver, "operation_name", expected_status, api_response)  # 操作后快照
5. 检测异常数量后调用 advance(op_name, anomalies_count, critical_count)
```

### 需要修改的文件

1. **`test_runner/api_e2e.py`** - 为每个 API 测试步骤添加感知采集调用
2. **`test_runner/playwright_e2e.py`** - 为每个浏览器操作步骤添加感知采集调用

---

## Required Work / 必需工作

### Step 1: 理解现有代码结构

读取以下文件，理解完整实现：

1. `.skills/human-e2e-tester/sensing/orchestrator.py` - 重点理解：
   - `snapshot_before(driver)` 返回什么
   - `snapshot_after(driver, operation, expected_next_status, api_response)` 的参数和返回值
   - `has_blocking_issues()` 和 `should_trigger_self_healing()` 的用法

2. `test_runner/api_e2e.py` - 找到所有 `def test_*` 或 `def step_*` 函数，列出它们的执行流程

3. `test_runner/playwright_e2e.py` - 找到所有操作步骤（login, click, submit 等）

### Step 2: 修复 api_e2e.py

在**每个** API 测试步骤中插入感知调用：

```python
# 示例结构
def step_login_taidongxu(orch, driver):
    # 1. 设置用户上下文
    orch.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")

    # 2. 操作前快照
    before = orchestrator.snapshot_before(driver)

    # 3. 执行动作
    response = api_login("taidongxu", "test123")

    # 4. 操作后快照
    snap, anomalies, checks = orchestrator.snapshot_after(
        driver,
        operation="login_taidongxu",
        expected_next_status="logged_in",
        api_response=response
    )

    # 5. 检测异常
    critical = sum(1 for a in anomalies if a.severity == "critical")
    high = sum(1 for a in anomalies if a.severity == "high")

    # 6. 推进 Agent
    advance("login_taidongxu", len(anomalies), critical)
```

**必须覆盖的步骤**（参考 `api_e2e.py` 中的实际步骤）：
- login 相关步骤
- 创建订单步骤
- 提交订单步骤
- 保管员确认步骤
- 运输通知步骤
- 运输开始/完成步骤
- 最终确认步骤

### Step 3: 修复 playwright_e2e.py

同样为每个浏览器操作步骤添加感知采集：

```python
# 示例结构
def step_keeper_confirm_order(orch, driver):
    orch.set_user_context("hutingting", "KEEPER", "ORG001")
    before = orchestrator.snapshot_before(driver)

    # 浏览器操作
    driver.click("#confirm-btn")
    driver.wait_for_selector(".el-message-box")

    snap, anomalies, checks = orchestrator.snapshot_after(
        driver,
        operation="keeper_confirm",
        expected_next_status="keeper_confirmed",
        api_response=None
    )

    critical = sum(1 for a in anomalies if a.severity == "critical")
    advance("keeper_confirm", len(anomalies), critical)
```

### Step 4: 确保失败路径也能推进

每个步骤的异常处理必须保证状态推进：

```python
try:
    # 正常流程
    ...
except Exception as e:
    # 即使失败也必须调用 advance 或记录异常
    anomalies.append(AnomalyReport(
        anomaly_type="operation_error",
        severity="high",
        description=str(e)
    ))
    advance("step_name", len(anomalies), critical_count)
```

### Step 5: 验证持久化

运行修复后的测试并验证数据库记录：

```powershell
python test_runner/api_e2e.py

# 然后检查数据库
import sqlite3
p = r"test_reports/e2e_sensing.db"
conn = sqlite3.connect(p)
cur = conn.cursor()
for t in ["snapshots", "anomalies", "consistency_checks", "workflow_positions"]:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t}: {cur.fetchone()[0]}")
conn.close()
```

**验收标准**：
- `snapshots >= 10`（每个步骤至少 1 个 before + 1 个 after）
- `anomalies >= 0`（允许为空，但需可解释）
- `consistency_checks >= 5`
- `workflow_positions >= 5`

---

## Constraints / 约束条件

1. **不改变现有测试逻辑** - 只在现有步骤中插入感知调用，不修改测试流程
2. **使用统一的 DB 路径** - `test_reports/e2e_sensing.db`，不允许分叉到 `test_runner/test_reports/`
3. **保持 Agent 状态机正确** - advance 必须在正确的时机调用，避免 run 卡死
4. **不引入新的依赖** - 只使用已有的 orchestrator API
5. **失败步骤也必须推进** - 即使 API 返回错误，也要调用 advance

---

## Completion Criteria / 完成标准

1. **感知数据落库** - 运行 `python test_runner/api_e2e.py` 后：
   - `snapshots > 0`（至少每个步骤有 before + after）
   - `consistency_checks > 0`
   - `workflow_positions > 0`

2. **命令链路完整** - `start/status/advance/report/stop` 全部正常工作

3. **失败路径处理** - 在测试中故意引入一个会失败的步骤，验证异常被正确记录且 run 不会卡死

4. **与上次对比** - 生成对比报告，确认与 `HUMAN_E2E_SKILL_VALIDATION_RERUN_20260327_131012.md` 相比：
   - snapshots: 0 → >0
   - anomalies: 0 → >=0（取决于是否有真实异常）
   - consistency_checks: 0 → >0
   - workflow_positions: 0 → >0

5. **输出验收报告** - 将结果写入 `test_reports/HUMAN_E2E_SENSING_FIX_VALIDATION_YYYYMMDD.md`
