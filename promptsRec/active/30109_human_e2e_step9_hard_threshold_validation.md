# Human E2E 8分达标 - 步骤9：增加硬门槛校验脚本

## 任务编号
- **执行顺序号**: 00170
- **类型编号**: 30109
- **任务类型**: 测试任务

## 任务目标
新增 `test_runner/validate_sensing_run.py`，自动判定是否达标，低于阈值即 `exit 1`。

## 新增文件
- `test_runner/validate_sensing_run.py`

## 前置依赖
- 步骤8（30108）必须已完成并验收通过

## 步骤9 具体修改要求

### 9.1 定义 8 分达标阈值
```python
# 8分达标阈值定义
SCORE_THRESHOLDS = {
    # 关键表必须有数据
    "min_snapshots": 10,           # 快照数 >= 10
    "min_workflow_positions": 5,   # 工作流位置 >= 5
    "min_consistency_checks": 5,   # 一致性检查 >= 5

    # 通过率要求
    "min_pass_rate": 0.8,          # 测试通过率 >= 80%

    # 关键指标
    "max_critical": 0,            # 关键异常 = 0
    "max_high": 2,                # 高优先级异常 <= 2

    # 报告完整性
    "require_rbac_results": True,  # 必须有 RBAC 测试结果
    "require_workflow_results": True,  # 必须有工作流测试结果
}
```

### 9.2 实现 validate_sensing_run.py
```python
#!/usr/bin/env python
"""
E2E 感知数据校验脚本

验收 8 分达标标准：
- snapshots >= 10
- workflow_positions >= 5
- consistency_checks >= 5
- pass_rate >= 80%
- critical_anomalies = 0
- high_anomalies <= 2
"""

import sys
import sqlite3
import json
from pathlib import Path

DB_PATH = "test_reports/e2e_sensing.db"
THRESHOLDS = {
    "min_snapshots": 10,
    "min_workflow_positions": 5,
    "min_consistency_checks": 5,
    "min_pass_rate": 0.8,
    "max_critical": 0,
    "max_high": 2,
}

def validate_run(run_id: str = None) -> dict:
    """验证指定 run 或最新的 run"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取最新的 run_id
    if run_id is None:
        cursor.execute("SELECT DISTINCT run_id FROM snapshots ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        if not result:
            return {"valid": False, "error": "No runs found"}
        run_id = result[0]

    # 查询各项指标
    checks = {}

    # snapshots
    cursor.execute("SELECT COUNT(*) FROM snapshots WHERE run_id = ?", (run_id,))
    checks["snapshots"] = cursor.fetchone()[0]

    # workflow_positions
    cursor.execute("SELECT COUNT(*) FROM workflow_positions WHERE run_id = ?", (run_id,))
    checks["workflow_positions"] = cursor.fetchone()[0]

    # consistency_checks
    cursor.execute("SELECT COUNT(*) FROM consistency_checks WHERE run_id = ?", (run_id,))
    checks["consistency_checks"] = cursor.fetchone()[0]

    # anomalies by severity
    cursor.execute("""
        SELECT severity, COUNT(*)
        FROM anomalies
        WHERE run_id = ?
        GROUP BY severity
    """, (run_id,))
    anomaly_counts = {row[0]: row[1] for row in cursor.fetchall()}
    checks["critical_anomalies"] = anomaly_counts.get("critical", 0)
    checks["high_anomalies"] = anomaly_counts.get("high", 0)

    # pass rate
    cursor.execute("SELECT COUNT(*) FROM operations WHERE run_id = ? AND status = 'SUCCESS'", (run_id,))
    success_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM operations WHERE run_id = ?", (run_id,))
    total_count = cursor.fetchone()[0]
    checks["pass_rate"] = success_count / total_count if total_count > 0 else 0

    conn.close()

    # 验证各项指标
    results = []
    all_passed = True

    if checks["snapshots"] < THRESHOLDS["min_snapshots"]:
        results.append(f"FAIL: snapshots ({checks['snapshots']}) < {THRESHOLDS['min_snapshots']}")
        all_passed = False
    else:
        results.append(f"PASS: snapshots ({checks['snapshots']}) >= {THRESHOLDS['min_snapshots']}")

    if checks["workflow_positions"] < THRESHOLDS["min_workflow_positions"]:
        results.append(f"FAIL: workflow_positions ({checks['workflow_positions']}) < {THRESHOLDS['min_workflow_positions']}")
        all_passed = False
    else:
        results.append(f"PASS: workflow_positions ({checks['workflow_positions']}) >= {THRESHOLDS['min_workflow_positions']}")

    if checks["consistency_checks"] < THRESHOLDS["min_consistency_checks"]:
        results.append(f"FAIL: consistency_checks ({checks['consistency_checks']}) < {THRESHOLDS['min_consistency_checks']}")
        all_passed = False
    else:
        results.append(f"PASS: consistency_checks ({checks['consistency_checks']}) >= {THRESHOLDS['min_consistency_checks']}")

    if checks["pass_rate"] < THRESHOLDS["min_pass_rate"]:
        results.append(f"FAIL: pass_rate ({checks['pass_rate']:.2%}) < {THRESHOLDS['min_pass_rate']:.2%}")
        all_passed = False
    else:
        results.append(f"PASS: pass_rate ({checks['pass_rate']:.2%}) >= {THRESHOLDS['min_pass_rate']:.2%}")

    if checks["critical_anomalies"] > THRESHOLDS["max_critical"]:
        results.append(f"FAIL: critical_anomalies ({checks['critical_anomalies']}) > {THRESHOLDS['max_critical']}")
        all_passed = False
    else:
        results.append(f"PASS: critical_anomalies ({checks['critical_anomalies']}) <= {THRESHOLDS['max_critical']}")

    if checks["high_anomalies"] > THRESHOLDS["max_high"]:
        results.append(f"FAIL: high_anomalies ({checks['high_anomalies']}) > {THRESHOLDS['max_high']}")
        all_passed = False
    else:
        results.append(f"PASS: high_anomalies ({checks['high_anomalies']}) <= {THRESHOLDS['max_high']}")

    return {
        "valid": all_passed,
        "run_id": run_id,
        "checks": checks,
        "results": results
    }

def main():
    run_id = sys.argv[1] if len(sys.argv) > 1 else None

    result = validate_run(run_id)

    print("=" * 60)
    print(f"E2E Sensing Run Validation")
    print("=" * 60)
    print(f"Run ID: {result['run_id']}")
    print()

    for r in result["results"]:
        status = "✓" if "PASS" in r else "✗"
        print(f"  [{status}] {r}")

    print()
    if result["valid"]:
        print("Result: VALID (8分达标)")
        print("=" * 60)
        sys.exit(0)
    else:
        print("Result: INVALID (未达标)")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 9.3 语法检查
```powershell
python -m py_compile test_runner/validate_sensing_run.py
```

### 9.4 验证命令
```bash
# 运行校验
python test_runner/validate_sensing_run.py

# 验证 exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "Validation PASSED"
} else {
    Write-Host "Validation FAILED"
}
```

### 9.5 验收门槛
- 脚本运行不报错
- 低于阈值返回 exit 1
- 通过阈值返回 exit 0
- 输出清晰可读

## 约束
- 不得顺手改其他步骤（步骤1-8、10）的内容
- 只做最小改动，聚焦于硬门槛校验

## 输出要求
1. 新增文件清单
2. 阈值定义说明
3. 验证命令执行结果
4. 风险评估
5. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP9_REPORT_YYYYMMDD_HHMMSS.md`
