# Human E2E 8分达标 - 步骤10：最终回归与评分

## 任务编号
- **执行顺序号**: 00171
- **类型编号**: 30110
- **任务类型**: 测试任务

## 任务目标
连续回归确认达到8分标准。执行 `quick_smoke + full_workflow + rbac` 连跑至少3轮。

## 修改范围
无新增文件修改（此步骤为验证步骤）

## 前置依赖
- 步骤1-9 必须全部已完成并验收通过

## 步骤10 具体修改要求

### 10.1 执行完整回归测试
```bash
# 连续3轮完整回归
for round in 1 2 3; do
    echo "=========================================="
    echo "Regression Round $round / 3"
    echo "=========================================="

    # Round 1: quick_smoke
    echo "[Round $round] Running quick_smoke..."
    python test_runner/test_runner_agent.py --command start --test-type quick_smoke
    python test_runner/test_runner_agent.py --command stop --reason "round_${round}_smoke_done"

    # Round 2: full_workflow
    echo "[Round $round] Running full_workflow..."
    python test_runner/test_runner_agent.py --command start --test-type full_workflow
    python test_runner/test_runner_agent.py --command stop --reason "round_${round}_workflow_done"

    # Round 3: rbac
    echo "[Round $round] Running rbac..."
    python test_runner/test_runner_agent.py --command start --test-type rbac
    python test_runner/test_runner_agent.py --command stop --reason "round_${round}_rbac_done"

    # 验证本轮结果
    python test_runner/validate_sensing_run.py
done
```

### 10.2 评分计算
```python
def calculate_score(run_id: str) -> dict:
    """
    计算测试评分 (满分10分)

    评分维度：
    1. 持久化闭环 (3分)
       - snapshots > 0: 1分
       - workflow_positions > 0: 1分
       - consistency_checks > 0: 1分

    2. 测试通过率 (3分)
       - 100%: 3分
       - 90-99%: 2分
       - 80-89%: 1分
       - <80%: 0分

    3. 异常控制 (2分)
       - 0 critical: 1分
       - 0 high: 1分

    4. 报告完整性 (2分)
       - report JSON 稳定: 1分
       - RBAC + Workflow 结果完整: 1分
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    score = 0
    details = []

    # 1. 持久化闭环
    cursor.execute("SELECT COUNT(*) FROM snapshots WHERE run_id = ?", (run_id,))
    snapshots = cursor.fetchone()[0]
    if snapshots > 0:
        score += 1
        details.append("snapshots: 1/1")
    else:
        details.append("snapshots: 0/1")

    cursor.execute("SELECT COUNT(*) FROM workflow_positions WHERE run_id = ?", (run_id,))
    positions = cursor.fetchone()[0]
    if positions > 0:
        score += 1
        details.append("workflow_positions: 1/1")
    else:
        details.append("workflow_positions: 0/1")

    cursor.execute("SELECT COUNT(*) FROM consistency_checks WHERE run_id = ?", (run_id,))
    checks = cursor.fetchone()[0]
    if checks > 0:
        score += 1
        details.append("consistency_checks: 1/1")
    else:
        details.append("consistency_checks: 0/1")

    # 2. 测试通过率
    cursor.execute("SELECT COUNT(*) FROM operations WHERE run_id = ? AND status = 'SUCCESS'", (run_id,))
    success = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM operations WHERE run_id = ?", (run_id,))
    total = cursor.fetchone()[0]
    pass_rate = success / total if total > 0 else 0

    if pass_rate >= 1.0:
        score += 3
        details.append(f"pass_rate: 3/3 ({pass_rate:.0%})")
    elif pass_rate >= 0.9:
        score += 2
        details.append(f"pass_rate: 2/3 ({pass_rate:.0%})")
    elif pass_rate >= 0.8:
        score += 1
        details.append(f"pass_rate: 1/3 ({pass_rate:.0%})")
    else:
        details.append(f"pass_rate: 0/3 ({pass_rate:.0%})")

    # 3. 异常控制
    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'critical'", (run_id,))
    critical = cursor.fetchone()[0]
    if critical == 0:
        score += 1
        details.append("critical_anomalies: 1/1 (0)")
    else:
        details.append(f"critical_anomalies: 0/1 ({critical})")

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'high'", (run_id,))
    high = cursor.fetchone()[0]
    if high == 0:
        score += 1
        details.append("high_anomalies: 1/1 (0)")
    else:
        details.append(f"high_anomalies: 0/1 ({high})")

    conn.close()

    return {
        "score": score,
        "max_score": 10,
        "percentage": score / 10 * 100,
        "details": details
    }
```

### 10.3 验证命令
```bash
# 运行完整回归
echo "Starting 3-round regression test..."
./run_regression.sh  # 或手动执行 10.1 的命令

# 计算各轮评分
python -c "
import sqlite3
from test_runner.validate_sensing_run import calculate_score

conn = sqlite3.connect('test_reports/e2e_sensing.db')
cursor = conn.cursor()

# 获取所有 run_id
cursor.execute('''
    SELECT DISTINCT run_id, test_type
    FROM snapshots
    ORDER BY created_at DESC
    LIMIT 9
''')
runs = cursor.fetchall()

print('=' * 60)
print('REGRESSION TEST RESULTS')
print('=' * 60)

for i, (run_id, test_type) in enumerate(runs):
    result = calculate_score(run_id)
    print(f'Run {i+1}: {test_type}')
    print(f'  Score: {result[\"score\"]}/10 ({result[\"percentage\"]:.0f}%)')
    for d in result['details']:
        print(f'    {d}')
    print()

# 验证是否达到 8 分
scores = [calculate_score(r[0])['score'] for r in runs]
if all(s >= 8 for s in scores):
    print('ALL RUNS PASSED 8/10 THRESHOLD')
else:
    print(f'SOME RUNS BELOW 8/10: {[s for s in scores if s < 8]}')

conn.close()
"
```

### 10.4 最终验收标准
| 指标 | 门槛 | 说明 |
|------|------|------|
| `quick_smoke` | 通过 | 1轮完成无critical错误 |
| `full_workflow` | 通过 | 1轮完成无critical错误 |
| `rbac` | 通过 | 1轮完成无critical错误 |
| `validate_sensing_run.py` | exit 0 | 所有阈值满足 |
| 评分 | >= 8/10 | 连续3轮平均 |

### 10.5 生成最终报告
```bash
# 生成最终报告
python -c "
import json
from datetime import datetime

report = {
    'title': 'Human E2E 8分达标 - 最终回归报告',
    'generated_at': datetime.now().isoformat(),
    'objective': '总评分从 5/10 提升到稳定 8/10',
    'test_types_run': ['quick_smoke', 'full_workflow', 'rbac'],
    'rounds': 3,
    'results': {...},  # 各轮详细结果
    'score_summary': {...},  # 评分汇总
    'conclusion': 'PASS' if all_passed else 'FAIL',
    'next_steps': []  # 如有未达标项，列出后续工作
}

with open('test_reports/HUMAN_E2E_FINAL_REPORT_YYYYMMDD.json', 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
"
```

## 约束
- 此步骤为验证步骤，聚焦于验证而非修改
- 如有未达标项，记录到 next_steps

## 输出要求
1. 3轮回归测试完整日志
2. 每轮评分详情
3. 最终结论（PASS/FAIL）
4. 如 FAIL，列出 next_steps

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP10_REPORT_YYYYMMDD_HHMMSS.md`
