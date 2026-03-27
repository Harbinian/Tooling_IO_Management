#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import io
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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

    # pass rate - based on test_runs table: completed=success, interrupted/running=fail
    cursor.execute("SELECT COUNT(*) FROM test_runs WHERE run_id = ? AND status = 'completed'", (run_id,))
    success_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM test_runs WHERE run_id = ?", (run_id,))
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
        status = "[PASS]" if "PASS" in r else "[FAIL]"
        print(f"  {status} {r}")

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
