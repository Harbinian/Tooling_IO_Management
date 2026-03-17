# -*- coding: utf-8 -*-
"""
Sensing 集成层 - 主会话通过这个脚本调用感知模块

解决 import 路径问题：主会话在仓库根目录运行，
需要把 .skills/human-e2e-tester 加入 sys.path 才能 import sensing 模块。
"""

import sys
import os
import json
import argparse

# =============================================================================
# 路径设置
# =============================================================================

# 仓库根目录
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSING_PACKAGE_ROOT = os.path.join(REPO_ROOT, ".skills", "human-e2e-tester")

# 加入 sys.path（如果还没加入）
if SENSING_PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, SENSING_PACKAGE_ROOT)

# =============================================================================
# 感知操作命令
# =============================================================================

def cmd_orchestrator_init(db_path: str, test_type: str, run_id: str = None, checkpoint_interval: int = 10):
    """初始化感知协调器"""
    from sensing.orchestrator import SensingOrchestrator

    orch = SensingOrchestrator(
        db_path=db_path,
        test_type=test_type,
        run_id=run_id,
        checkpoint_interval=checkpoint_interval,
    )

    result = {
        "success": True,
        "run_id": orch.run_id,
        "test_type": orch.test_type,
        "resumed": orch.resumed_from_checkpoint,
        "operation_count": orch.operation_count,
    }

    if orch.resumed_from_checkpoint:
        cp = orch.db.get_latest_checkpoint(orch.run_id)
        if cp:
            ctx = json.loads(cp.context_json)
            result["restored_context"] = ctx
            result["restored_operation_index"] = cp.operation_index

    return result


def cmd_snapshot_before(db_path: str, run_id: str, driver_type: str = "playwright"):
    """
    执行操作前快照 - P1-3 已废弃

    此命令仅返回指南信息。snapshot_before 需要真实的 driver 对象，
    应由 E2E runner (playwright_e2e.py / api_e2e.py) 在测试执行时直接调用。
    sensing_integration.py 现在是纯报告生成工具。
    """
    return {
        "success": True,
        "message": "snapshot_before is deprecated - integrate SensingOrchestrator directly in E2E runners",
        "run_id": run_id,
        "note": "Use playwright_e2e.py or api_e2e.py which now have built-in sensing integration",
    }


def cmd_snapshot_after(db_path: str, run_id: str, operation: str,
                       expected_next_status: str = None,
                       api_response_status: int = None,
                       api_response_body: str = None):
    """
    执行操作后快照（分析） - P1-3 已废弃

    此命令仅返回指南信息。snapshot_after 需要真实的 driver 对象，
    应由 E2E runner (playwright_e2e.py / api_e2e.py) 在测试执行时直接调用。
    sensing_integration.py 现在是纯报告生成工具。
    """
    return {
        "success": True,
        "message": "snapshot_after is deprecated - integrate SensingOrchestrator directly in E2E runners",
        "run_id": run_id,
        "operation": operation,
        "note": "Use playwright_e2e.py or api_e2e.py which now have built-in sensing integration",
    }


def cmd_get_report(db_path: str, run_id: str = None):
    """获取完整感知报告（直接查 storage，不走 orchestrator 初始化）"""
    from sensing.storage import SQLiteStorage

    db = SQLiteStorage(db_path)

    if run_id is None:
        run = db.get_latest_test_run()
        if not run:
            return {"success": False, "error": "No test runs found"}
        run_id = run.run_id
    else:
        run = db.get_test_run(run_id)
        if not run:
            return {"success": False, "error": f"Run {run_id} not found"}

    # 直接从数据库读取所有数据
    all_data = db.get_all_for_run(run_id)
    summary = db.get_run_summary(run_id)

    # 格式化 anomalies
    anomalies = []
    for a in all_data["anomalies"]:
        anomalies.append({
            "anomaly_type": a.anomaly_type,
            "severity": a.severity,
            "description": a.description,
            "page_name": a.page_name,
            "order_no": a.order_no,
            "evidence": json.loads(a.evidence_json) if a.evidence_json else {},
        })

    # 格式化 consistency checks
    checks = []
    for c in all_data["consistency_checks"]:
        checks.append({
            "check_name": c.check_name,
            "passed": bool(c.passed),
            "expected": c.expected,
            "actual": c.actual,
            "details": c.details,
            "order_no": c.order_no,
        })

    # 格式化 workflow positions
    positions = []
    for p in all_data["workflow_positions"]:
        positions.append({
            "order_no": p.order_no,
            "state": p.current_state,
            "label": p.current_label,
            "buttons_match": bool(p.buttons_match),
        })

    return {
        "run_id": run_id,
        "test_type": run.test_type,
        "status": run.status,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "summary": summary,
        "anomalies": anomalies,
        "consistency_checks": checks,
        "workflow_positions": positions,
    }


def cmd_status(db_path: str, run_id: str = None):
    """获取感知层状态（直接查 storage，不走 orchestrator 初始化）"""
    from sensing.storage import SQLiteStorage

    db = SQLiteStorage(db_path)

    if run_id:
        summary = db.get_run_summary(run_id)
        run = db.get_test_run(run_id)
        return {
            "success": True,
            "run_id": run_id,
            "status": run.status if run else "unknown",
            "test_type": run.test_type if run else "unknown",
            "summary": summary,
        }
    else:
        run = db.get_latest_test_run()
        if not run:
            return {"success": False, "error": "No test runs found"}
        summary = db.get_run_summary(run.run_id)
        return {
            "success": True,
            "run_id": run.run_id,
            "status": run.status,
            "test_type": run.test_type,
            "summary": summary,
        }


# =============================================================================
# 主入口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Sensing Integration Layer")
    parser.add_argument("--command", required=True,
                        choices=["orchestrator_init", "snapshot_before", "snapshot_after",
                                "get_report", "status"])
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--test-type", default="full_workflow")
    parser.add_argument("--checkpoint-interval", type=int, default=10)
    parser.add_argument("--operation", default="")
    parser.add_argument("--expected-next-status", default=None)
    parser.add_argument("--api-response-status", type=int, default=None)
    parser.add_argument("--api-response-body", default=None)
    parser.add_argument("--driver-type", default="playwright")

    args = parser.parse_args()

    # 默认 db_path
    if args.db_path is None:
        args.db_path = os.path.join(REPO_ROOT, "test_reports", "e2e_sensing.db")

    try:
        if args.command == "orchestrator_init":
            result = cmd_orchestrator_init(
                args.db_path, args.test_type, args.run_id, args.checkpoint_interval
            )
        elif args.command == "snapshot_before":
            result = cmd_snapshot_before(args.db_path, args.run_id, args.driver_type)
        elif args.command == "snapshot_after":
            result = cmd_snapshot_after(
                args.db_path, args.run_id, args.operation,
                args.expected_next_status, args.api_response_status, args.api_response_body
            )
        elif args.command == "get_report":
            result = cmd_get_report(args.db_path, args.run_id)
        elif args.command == "status":
            result = cmd_status(args.db_path, args.run_id)
        else:
            result = {"success": False, "error": f"Unknown command: {args.command}"}

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }, ensure_ascii=False, indent=2))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
