# Human E2E 8分达标分步执行方案

## 目标定义
1. 总评分从 `5/10` 提升到稳定 `8/10`。
2. 核心达标条件是“真实持久化嗅探闭环”：每轮测试后 `snapshots/consistency_checks/workflow_positions` 都有有效增量。
3. 每一步都可回滚、可验收、可追踪。

## 执行节奏
1. 每次只做一个最小目标（建议 1-2 个文件，<200 行改动）。
2. 每步必须跑验证命令并写 `test_reports` 报告。
3. 每步通过后再进入下一步，不做大包提交。

## 分步实施方案（10步）

### 步骤1：建立单一事实库约束
- 目标：全链路统一写 `test_reports/e2e_sensing.db`
- 涉及文件：
  - `test_runner/test_runner_agent.py`
  - `test_runner/api_e2e.py`
  - `test_runner/playwright_e2e.py`
  - `test_runner/sensing_integration.py`
  - `.skills/human-e2e-tester/sensing/storage.py`
- 验收：不再出现分叉库数据增量

### 步骤2：固化步骤执行框架
- 目标：统一步骤函数 `before -> action -> after -> advance`
- 涉及文件：`test_runner/api_e2e.py`
- 验收：至少5个关键步骤接入

### 步骤3：打通真实感知采集
- 目标：关键步骤执行 `snapshot_before/snapshot_after` 并落库
- 涉及文件：
  - `test_runner/api_e2e.py`
  - `.skills/human-e2e-tester/sensing/orchestrator.py`
- 验收：`snapshots > 0`、`workflow_positions > 0`、`consistency_checks > 0`

### 步骤4：完成失败分支闭环
- 目标：异常时仍执行 `snapshot_after` 与 `advance/stop`
- 涉及文件：`test_runner/api_e2e.py`
- 验收：失败 run 也有完整状态与感知数据

### 步骤5：修正 RBAC 用例假阳性
- 目标：RBAC 用例改为“前置数据 + 明确预期响应”
- 涉及文件：`test_runner/api_e2e.py`
- 验收：RBAC 报告可解释、可复现

### 步骤6：测试数据隔离
- 目标：run 级唯一前缀 + setup/teardown
- 涉及文件：`test_runner/api_e2e.py`
- 验收：连续3次执行不因脏数据冲突失败

### 步骤7：Playwright 路径同框架接入
- 目标：Playwright 执行也触发同级感知落库
- 涉及文件：
  - `test_runner/playwright_e2e.py`
  - `.skills/human-e2e-tester/sensing/page_observer.py`
- 验收：Playwright 跑后关键表有增量

### 步骤8：统一报告协议
- 目标：`report` 输出稳定、结构化
- 涉及文件：
  - `test_runner/test_runner_agent.py`
  - `test_runner/commands.py`
- 验收：`start/status/advance/report/stop` 全可用且 JSON 稳定

### 步骤9：增加硬门槛校验脚本
- 目标：自动判定是否达标
- 涉及文件：新增 `test_runner/validate_sensing_run.py`
- 验收：低于阈值即 `exit 1`

### 步骤10：最终回归与评分
- 目标：连续回归确认达到8分
- 执行：`quick_smoke + full_workflow + rbac` 连跑至少3轮
- 验收：通过率、落库、报告完整度均满足8分标准

## 每步统一验收命令
1. `python -m py_compile ...`（本步涉及文件）
2. `python test_runner\test_runner_agent.py --command start --test-type quick_smoke`
3. `python test_runner\test_runner_agent.py --command report`
4. `python test_runner\test_runner_agent.py --command stop --reason "step-check"`
5. `python test_runner\api_e2e.py`（或对应 runner）
6. 查询 `test_reports/e2e_sensing.db` 关键表计数并写入报告

## 给 Claude 的单步任务模板
1. 任务目标：只完成【步骤N】。
2. 修改范围：仅限【文件列表】。
3. 约束：不得顺手改其他步骤内容。
4. 输出：代码改动、验证命令结果、风险、回滚方式。
5. 报告：写入 `test_reports/HUMAN_E2E_STEP_N_REPORT_YYYYMMDD_HHMMSS.md`。
6. 通过标准：满足该步骤验收门槛，否则继续修到通过。