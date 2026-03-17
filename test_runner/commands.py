# -*- coding: utf-8 -*-
"""
Test Runner Agent - 命令行工具

简化与 Agent 的交互。
"""

import subprocess
import json
import os
import sys


def get_script_path():
    """获取脚本路径"""
    return os.path.join(os.path.dirname(__file__), "test_runner_agent.py")


def run_command(command: str, **kwargs) -> dict:
    """执行命令"""
    cmd = [
        sys.executable,
        get_script_path(),
        "--command", command,
    ]

    if "test_type" in kwargs:
        cmd.extend(["--test-type", kwargs["test_type"]])

    if "reason" in kwargs:
        cmd.extend(["--reason", kwargs["reason"]])

    if "current_operation" in kwargs:
        cmd.extend(["--current-operation", kwargs["current_operation"]])

    if "anomalies_count" in kwargs:
        cmd.extend(["--anomalies-count", str(kwargs["anomalies_count"])])

    if "critical_count" in kwargs:
        cmd.extend(["--critical-count", str(kwargs["critical_count"])])

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # 如果 stdout 不是 JSON，返回 stderr 或错误信息
        error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
        raise RuntimeError(f"Agent command failed: {error_msg}")


def start(test_type: str = "full_workflow") -> dict:
    """开始测试"""
    return run_command("start", test_type=test_type)


def resume() -> dict:
    """继续测试"""
    return run_command("resume")


def status() -> dict:
    """查询状态"""
    return run_command("status")


def stop(reason: str = "User stopped") -> dict:
    """停止测试"""
    return run_command("stop", reason=reason)


def advance(current_operation: str, anomalies_count: int = 0, critical_count: int = 0) -> dict:
    """推进测试到下一步"""
    return run_command(
        "advance",
        current_operation=current_operation,
        anomalies_count=anomalies_count,
        critical_count=critical_count,
    )


def report() -> dict:
    """获取报告"""
    try:
        return run_command("report")
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse report response: {str(e)}",
            "raw_output": "Report command may have failed - check agent status",
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Runner Agent Commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--test-type", default="full_workflow")

    resume_parser = subparsers.add_parser("resume")

    status_parser = subparsers.add_parser("status")

    stop_parser = subparsers.add_parser("stop")
    stop_parser.add_argument("--reason", default="User stopped")

    report_parser = subparsers.add_parser("report")

    advance_parser = subparsers.add_parser("advance")
    advance_parser.add_argument("--current-operation", required=True)
    advance_parser.add_argument("--anomalies-count", type=int, default=0)
    advance_parser.add_argument("--critical-count", type=int, default=0)

    args = parser.parse_args()

    if args.command == "start":
        result = start(args.test_type)
    elif args.command == "resume":
        result = resume()
    elif args.command == "status":
        result = status()
    elif args.command == "stop":
        result = stop(args.reason)
    elif args.command == "report":
        result = report()
    elif args.command == "advance":
        result = advance(args.current_operation, args.anomalies_count, args.critical_count)

    print(json.dumps(result, ensure_ascii=False, indent=2))
