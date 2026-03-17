# Human E2E 8分达标 - 步骤3：打通真实感知采集

## 任务编号
- **执行顺序号**: 00164
- **类型编号**: 30103
- **任务类型**: 测试任务

## 任务目标
关键步骤执行 `snapshot_before/snapshot_after` 并落库，验证：
- `snapshots > 0`
- `workflow_positions > 0`
- `consistency_checks > 0`

## 修改范围
仅限以下文件：
1. `test_runner/api_e2e.py`
2. `.skills/human-e2e-tester/sensing/orchestrator.py`

## 前置依赖
- 步骤1（30101）必须已完成并验收通过
- 步骤2（30102）必须已完成并验收通过

## 步骤3 具体修改要求

### 3.1 在 api_e2e.py 中集成 SensingOrchestrator
参考 human-e2e-tester 技能文档：

```python
import sys
sys.path.insert(0, ".skills/human-e2e-tester")

from sensing import SensingOrchestrator

# 初始化 orchestrator
orch = SensingOrchestrator(
    db_path="test_reports/e2e_sensing.db",
    run_id="<from agent status>",
    test_type="full_workflow",
)

# 设置用户上下文
orch.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")

# 操作前快照
before = orch.snapshot_before(driver)

# 操作后快照 + 异常检测
snap, anomalies, checks = orch.snapshot_after(
    driver,
    operation="keeper_confirm",
    expected_next_status="keeper_confirmed",
)
```

### 3.2 为关键步骤添加感知采集
在每个 `execute_step` 调用中添加：
- `snapshot_before` - 记录操作前页面状态
- `snapshot_after` - 记录操作后页面状态

关键步骤包括：
1. `login` - 登录后快照
2. `create_order` - 创建订单前后快照
3. `submit_order` - 提交前后快照
4. `keeper_confirm` - 保管员确认前后快照
5. `transport_start` - 运输开始前后快照
6. `final_confirm` - 最终确认前后快照

### 3.3 检查 orchestrator.py 的 snapshot_after 方法
读取 `.skills/human-e2e-tester/sensing/orchestrator.py`，确认：
- `snapshot_after` 方法正确保存到数据库
- `workflow_positions` 表有数据写入
- `consistency_checks` 表有数据写入

### 3.4 语法检查
```powershell
python -m py_compile test_runner/api_e2e.py .skills/human-e2e-tester/sensing/orchestrator.py
```

### 3.5 验证命令
```bash
# 启动完整工作流测试
python test_runner/test_runner_agent.py --command start --test-type full_workflow

# 运行一段时间后检查
python test_runner/test_runner_agent.py --command status
python test_runner/test_runner_agent.py --command stop --reason "step3-check"

# 查询数据库关键表
python -c "
import sqlite3
conn = sqlite3.connect('test_reports/e2e_sensing.db')
cursor = conn.cursor()
tables = ['snapshots', 'workflow_positions', 'consistency_checks', 'anomalies']
for t in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {t}')
        count = cursor.fetchone()[0]
        print(f'{t}: {count}')
        if count > 0:
            cursor.execute(f'SELECT * FROM {t} LIMIT 1')
            print(f'  Sample: {cursor.fetchone()}')
    except Exception as e:
        print(f'{t}: error - {e}')
conn.close()
"
```

### 3.6 验收门槛
- `snapshots` 表有记录（> 0）
- `workflow_positions` 表有记录（> 0）
- `consistency_checks` 表有记录（> 0）

## 约束
- 不得顺手改其他步骤（步骤1-2、4-10）的内容
- 只做最小改动，聚焦于感知采集打通

## 输出要求
1. 代码改动清单
2. 验证命令执行结果
3. 各关键表的数据计数
4. 风险评估
5. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP3_REPORT_YYYYMMDD_HHMMSS.md`
