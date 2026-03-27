# -*- coding: utf-8 -*-
"""
Test Runner Agent - 拟人 E2E 测试状态管理器

后台运行的状态管理器，不受 Claude Code auto-compact 影响。
通过 SQLite 存储测试状态，主会话负责实际执行。

使用方法：
    python test_runner/test_runner_agent.py --command start
    python test_runner/test_runner_agent.py --command resume
    python test_runner/test_runner_agent.py --command status
    python test_runner/test_runner_agent.py --command stop --reason "用户停止"
"""

import argparse
import json
import os
import sys
import sqlite3
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Any


# =============================================================================
# 配置
# =============================================================================

# 使用统一的数据库路径：repo_root/test_reports/e2e_sensing.db
# 与 playwright_e2e.py、api_e2e.py、sensing_integration.py 保持一致
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(AGENT_DIR)
TEST_REPORTS_DIR = os.path.join(REPO_ROOT, "test_reports")
DB_PATH = os.path.join(TEST_REPORTS_DIR, "e2e_sensing.db")
COMMAND_FILE = os.path.join(TEST_REPORTS_DIR, ".agent_command.json")
STATUS_FILE = os.path.join(TEST_REPORTS_DIR, ".agent_status.json")
PID_FILE = os.path.join(TEST_REPORTS_DIR, ".agent.pid")

os.makedirs(TEST_REPORTS_DIR, exist_ok=True)


# =============================================================================
# 状态定义
# =============================================================================

class AgentState:
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# =============================================================================
# 稳定 JSON 报告模板
# =============================================================================

REPORT_TEMPLATE = {
    "success": True,
    "report": {
        "metadata": {
            "run_id": "",
            "test_type": "",
            "status": "",  # RUNNING/PAUSED/COMPLETED/FAILED
            "started_at": "",
            "ended_at": None,
            "duration_seconds": None
        },
        "summary": {
            "total_operations": 0,
            "completed_operations": 0,
            "failed_operations": 0,
            "anomalies_count": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0
        },
        "operations": [],
        "sensing": {
            "snapshots_count": 0,
            "workflow_positions_count": 0,
            "consistency_checks_passed": 0,
            "consistency_checks_failed": 0,
            "anomalies": []
        },
        "workflow_positions": []
    }
}


@dataclass
class AgentStatus:
    """Agent 状态"""
    state: str
    run_id: Optional[str]
    test_type: Optional[str]
    operation_index: int
    total_operations: int
    current_operation: Optional[str]
    next_operation: Optional[str]
    anomalies_count: int
    critical_count: int
    high_count: int
    last_updated: str
    message: str
    resumed: bool = False


# =============================================================================
# 数据库操作
# =============================================================================

def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()

    schema = """
        CREATE TABLE IF NOT EXISTS test_runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            status TEXT DEFAULT 'running',
            test_type TEXT DEFAULT 'full_workflow',
            summary_json TEXT
        );

        CREATE TABLE IF NOT EXISTS checkpoints (
            cp_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            operation_index INTEGER DEFAULT 0,
            context_json TEXT,
            next_expected_op TEXT,
            next_expected_status TEXT
        );

        CREATE TABLE IF NOT EXISTS agent_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            state TEXT NOT NULL,
            run_id TEXT,
            test_type TEXT,
            operation_index INTEGER DEFAULT 0,
            total_operations INTEGER DEFAULT 0,
            current_operation TEXT,
            next_operation TEXT,
            last_updated TEXT
        );

        CREATE TABLE IF NOT EXISTS anomalies (
            anomaly_id TEXT PRIMARY KEY,
            cp_id TEXT,
            run_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            anomaly_type TEXT,
            severity TEXT,
            description TEXT,
            page_name TEXT,
            order_no TEXT,
            evidence_json TEXT DEFAULT '{}'
        );
    """

    # SQLite 不支持多语句一次执行，需要拆分
    for stmt in schema.split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError:
                pass  # 表已存在

    conn.commit()
    conn.close()


def get_agent_state() -> dict:
    """获取 Agent 状态"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agent_state WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "state": AgentState.IDLE,
            "run_id": None,
            "test_type": None,
            "operation_index": 0,
            "total_operations": 0,
            "current_operation": None,
            "next_operation": None,
        }

    return {
        "state": row[1],
        "run_id": row[2],
        "test_type": row[3],
        "operation_index": row[4],
        "total_operations": row[5],
        "current_operation": row[6],
        "next_operation": row[7],
    }


def save_agent_state(state: str, run_id: Optional[str], test_type: Optional[str],
                     operation_index: int, total_operations: int,
                     current_operation: Optional[str], next_operation: Optional[str]):
    """保存 Agent 状态"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO agent_state (id, state, run_id, test_type, operation_index, total_operations, current_operation, next_operation, last_updated)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (state, run_id, test_type, operation_index, total_operations, current_operation, next_operation, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_running_test_run() -> Optional[dict]:
    """获取正在运行的测试（包括 interrupted 的）"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM test_runs WHERE status IN ('running', 'interrupted') ORDER BY started_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "run_id": row[0],
        "started_at": row[1],
        "ended_at": row[2],
        "status": row[3],
        "test_type": row[4],
        "summary_json": row[5],
    }


def create_test_run(run_id: str, test_type: str) -> dict:
    """创建新测试运行"""
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO test_runs (run_id, started_at, status, test_type)
        VALUES (?, ?, 'running', ?)
    """, (run_id, now, test_type))

    conn.commit()
    conn.close()

    return {
        "run_id": run_id,
        "started_at": now,
        "status": "running",
        "test_type": test_type,
    }


def update_test_run_status(run_id: str, status: str, summary_json: Optional[str] = None):
    """更新测试运行状态"""
    conn = get_db_connection()
    cursor = conn.cursor()

    ended_at = datetime.now().isoformat()
    if summary_json:
        cursor.execute("""
            UPDATE test_runs SET status = ?, ended_at = ?, summary_json = ?
            WHERE run_id = ?
        """, (status, ended_at, summary_json, run_id))
    else:
        cursor.execute("""
            UPDATE test_runs SET status = ?, ended_at = ?
            WHERE run_id = ?
        """, (status, ended_at, run_id))

    conn.commit()
    conn.close()


def get_test_summary(run_id: str) -> dict:
    """获取测试汇总"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取异常统计
    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ?", (run_id,))
    total_anomalies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'critical'", (run_id,))
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'high'", (run_id,))
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'medium'", (run_id,))
    medium = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'low'", (run_id,))
    low = cursor.fetchone()[0]

    # 获取已完成操作数
    cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE run_id = ?", (run_id,))
    completed_ops = cursor.fetchone()[0]

    # 获取失败操作数（从anomalies推算）
    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ?", (run_id,))
    failed_ops = cursor.fetchone()[0]

    # 获取检查点
    cursor.execute("SELECT operation_index FROM checkpoints WHERE run_id = ? ORDER BY created_at DESC LIMIT 1", (run_id,))
    row = cursor.fetchone()
    last_checkpoint_op = row[0] if row else 0

    conn.close()

    return {
        "total_anomalies": total_anomalies,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "completed_operations": completed_ops,
        "failed_operations": failed_ops,
        "last_checkpoint_operation": last_checkpoint_op,
    }


def get_run_metadata(cursor: sqlite3.Cursor, run_id: str) -> dict:
    """获取运行元数据"""
    cursor.execute(
        "SELECT run_id, test_type, status, started_at, ended_at FROM test_runs WHERE run_id = ?",
        (run_id,)
    )
    row = cursor.fetchone()

    if not row:
        return {
            "run_id": None,
            "test_type": None,
            "status": "IDLE",
            "started_at": None,
            "ended_at": None,
            "duration_seconds": None,
        }

    started_at = row[3]
    ended_at = row[4]
    duration_seconds = None

    if started_at:
        if ended_at:
            from datetime import datetime
            start_dt = datetime.fromisoformat(started_at)
            end_dt = datetime.fromisoformat(ended_at)
            duration_seconds = int((end_dt - start_dt).total_seconds())
        else:
            from datetime import datetime
            start_dt = datetime.fromisoformat(started_at)
            duration_seconds = int((datetime.now() - start_dt).total_seconds())

    return {
        "run_id": row[0],
        "test_type": row[1],
        "status": row[2].upper() if row[2] else "UNKNOWN",
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration_seconds,
    }


def get_run_summary(cursor: sqlite3.Cursor, run_id: str) -> dict:
    """获取汇总数据"""
    # 获取异常统计
    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ?", (run_id,))
    anomalies_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'critical'", (run_id,))
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'high'", (run_id,))
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'medium'", (run_id,))
    medium = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomalies WHERE run_id = ? AND severity = 'low'", (run_id,))
    low = cursor.fetchone()[0]

    # 获取已完成操作数
    cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE run_id = ?", (run_id,))
    completed_ops = cursor.fetchone()[0]

    # 获取总操作数（从剧本计算）
    cursor.execute("SELECT test_type FROM test_runs WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    test_type = row[0] if row else "quick_smoke"
    script = TEST_SCRIPTS.get(test_type, TEST_SCRIPTS["quick_smoke"])
    total_ops = len(script["steps"])

    return {
        "total_operations": total_ops,
        "completed_operations": completed_ops,
        "failed_operations": anomalies_count,
        "anomalies_count": anomalies_count,
        "critical_count": critical,
        "high_count": high,
        "medium_count": medium,
        "low_count": low,
    }


def get_operations(cursor: sqlite3.Cursor, run_id: str) -> list:
    """获取操作列表"""
    cursor.execute(
        "SELECT operation_index, next_expected_op, created_at FROM checkpoints WHERE run_id = ? ORDER BY created_at ASC",
        (run_id,)
    )
    rows = cursor.fetchall()

    operations = []
    for i, row in enumerate(rows):
        op_index = row[0]
        op_name = row[1] or f"operation_{op_index}"
        created_at = row[2]

        # 获取该操作的异常数
        cursor.execute(
            "SELECT COUNT(*) FROM anomalies WHERE run_id = ?",
            (run_id,)
        )
        anomalies = cursor.fetchone()[0]

        # 计算持续时间（简化：使用下一个操作的创建时间差）
        duration_ms = 0
        if i < len(rows) - 1:
            next_created_at = rows[i + 1][2]
            from datetime import datetime
            start_dt = datetime.fromisoformat(created_at)
            end_dt = datetime.fromisoformat(next_created_at)
            duration_ms = int((end_dt - start_dt).total_seconds() * 1000)

        operations.append({
            "index": op_index,
            "name": op_name,
            "status": "SUCCESS",
            "started_at": created_at,
            "duration_ms": duration_ms,
            "anomalies": anomalies,
            "critical": 0,
        })

    return operations


def get_sensing_summary(cursor: sqlite3.Cursor, run_id: str) -> dict:
    """获取感知数据汇总"""
    # 获取快照数
    cursor.execute(
        "SELECT COUNT(*) FROM checkpoints WHERE run_id = ?",
        (run_id,)
    )
    snapshots_count = cursor.fetchone()[0]

    # 获取工作流位置数（与操作数相同）
    workflow_positions_count = snapshots_count

    # 获取一致性检查结果（暂无专门表，设为0）
    consistency_checks_passed = 0
    consistency_checks_failed = 0

    # 获取异常列表
    cursor.execute(
        "SELECT anomaly_type, severity, description, order_no, anomaly_type FROM anomalies WHERE run_id = ? ORDER BY created_at DESC",
        (run_id,)
    )
    anomaly_rows = cursor.fetchall()

    anomalies = []
    for row in anomaly_rows:
        anomalies.append({
            "type": row[0] or "unknown",
            "severity": (row[1] or "low").upper(),
            "description": row[2] or "",
            "order_no": row[3],
            "operation": row[4] or "",
        })

    return {
        "snapshots_count": snapshots_count,
        "workflow_positions_count": workflow_positions_count,
        "consistency_checks_passed": consistency_checks_passed,
        "consistency_checks_failed": consistency_checks_failed,
        "anomalies": anomalies,
    }


def build_report(run_id: str) -> dict:
    """从数据库构建完整报告"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 元数据
    metadata = get_run_metadata(cursor, run_id)

    # 汇总数据
    summary = get_run_summary(cursor, run_id)

    # 操作列表
    operations = get_operations(cursor, run_id)

    # 感知数据
    sensing = get_sensing_summary(cursor, run_id)

    conn.close()

    return {
        "metadata": metadata,
        "summary": summary,
        "operations": operations,
        "sensing": sensing,
        "workflow_positions": [],
    }


# =============================================================================
# 测试剧本
# =============================================================================

TEST_SCRIPTS = {
    "full_workflow": {
        "name": "完整出库工作流",
        "steps": [
            {"type": "comment", "name": "=== 完整出库工作流测试 ==="},
            {"type": "sense", "name": "login_taidongxu", "user": "taidongxu", "role": "TEAM_LEADER"},
            {"type": "wait", "name": "wait_page_load", "duration": 2},
            {"type": "sense", "name": "create_order_start"},
            {"type": "sense", "name": "create_order_verify"},
            {"type": "sense", "name": "submit_order_start"},
            {"type": "sense", "name": "submit_order_verify"},
            {"type": "sense", "name": "switch_user_hutingting", "user": "hutingting", "role": "KEEPER"},
            {"type": "sense", "name": "keeper_view_orders"},
            {"type": "sense", "name": "keeper_confirm_start"},
            {"type": "sense", "name": "keeper_confirm_verify"},
            {"type": "sense", "name": "notify_transport_start"},
            {"type": "sense", "name": "notify_transport_verify"},
            {"type": "sense", "name": "switch_user_fengliang", "user": "fengliang", "role": "PRODUCTION_PREP"},
            {"type": "sense", "name": "transport_view"},
            {"type": "sense", "name": "transport_start"},
            {"type": "sense", "name": "transport_complete"},
            {"type": "sense", "name": "switch_user_taidongxu_final", "user": "taidongxu", "role": "TEAM_LEADER"},
            {"type": "sense", "name": "final_confirm_start"},
            {"type": "sense", "name": "final_confirm_verify"},
            {"type": "sense", "name": "verify_completed"},
            {"type": "comment", "name": "=== 测试完成 ==="},
        ]
    },
    "quick_smoke": {
        "name": "快速冒烟测试",
        "steps": [
            {"type": "comment", "name": "=== 快速冒烟测试 ==="},
            {"type": "sense", "name": "login"},
            {"type": "sense", "name": "view_order_list"},
            {"type": "sense", "name": "create_simple_order"},
            {"type": "comment", "name": "=== 冒烟测试完成 ==="},
        ]
    },
    "rbac": {
        "name": "RBAC 权限测试",
        "steps": [
            {"type": "comment", "name": "=== RBAC 权限测试 ==="},
            {"type": "sense", "name": "test_taidongxu_permissions"},
            {"type": "sense", "name": "test_hutingting_permissions"},
            {"type": "sense", "name": "test_fengliang_permissions"},
            {"type": "sense", "name": "test_admin_permissions"},
            {"type": "comment", "name": "=== RBAC 测试完成 ==="},
        ]
    },
}


# =============================================================================
# Test Runner Agent 核心
# =============================================================================

class TestRunnerAgent:
    """
    测试运行器 Agent

    维护测试状态，响应命令。
    注意：这是一个"状态管理器"，实际测试执行由主会话负责。
    """

    def __init__(self):
        init_db()
        self.run_id: Optional[str] = None
        self.test_type: Optional[str] = None
        self.operation_index = 0
        self.total_operations = 0
        self.current_operation: Optional[str] = None
        self.resumed = False

        # 恢复状态
        state = get_agent_state()
        if state["state"] != AgentState.IDLE and state["run_id"]:
            self.run_id = state["run_id"]
            self.test_type = state["test_type"]
            self.operation_index = state["operation_index"]
            self.total_operations = state["total_operations"]
            self.current_operation = state["current_operation"]

    def handle_command(self, command: str, payload: dict) -> dict:
        """处理命令"""
        handlers = {
            "start": self._cmd_start,
            "resume": self._cmd_resume,
            "status": self._cmd_status,
            "stop": self._cmd_stop,
            "advance": self._cmd_advance,
            "report": self._cmd_report,
        }

        handler = handlers.get(command)
        if not handler:
            return {"success": False, "error": f"Unknown command: {command}"}

        return handler(payload)

    def _cmd_start(self, payload: dict) -> dict:
        """开始新测试"""
        current_state = get_agent_state()
        if current_state["state"] == AgentState.RUNNING:
            return {"success": False, "error": "Test already running", "state": current_state["state"]}

        self.test_type = payload.get("test_type", "full_workflow")
        self.run_id = str(uuid.uuid4())
        self.operation_index = 0
        self.resumed = False

        # 获取剧本
        script = TEST_SCRIPTS.get(self.test_type, TEST_SCRIPTS["quick_smoke"])
        self.total_operations = len(script["steps"])

        # 创建测试运行记录
        create_test_run(self.run_id, self.test_type)

        # 保存状态
        save_agent_state(
            AgentState.RUNNING,
            self.run_id,
            self.test_type,
            self.operation_index,
            self.total_operations,
            None,
            script["steps"][0]["name"] if script["steps"] else None
        )

        # 保存 PID
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        return {
            "success": True,
            "state": AgentState.RUNNING,
            "run_id": self.run_id,
            "test_type": self.test_type,
            "operation_index": self.operation_index,
            "total_operations": self.total_operations,
            "next_operation": script["steps"][0]["name"] if script["steps"] else None,
            "message": f"Test started: {script['name']}",
        }

    def _cmd_resume(self, payload: dict) -> dict:
        """继续测试"""
        current_state = get_agent_state()

        if current_state["state"] == AgentState.RUNNING:
            return {"success": False, "error": "Test already running", "state": AgentState.RUNNING}

        # 查找最近的 paused 或 running 测试
        running = get_running_test_run()
        if not running:
            return {"success": False, "error": "No interrupted test found"}

        self.run_id = running["run_id"]
        self.test_type = running["test_type"]

        # 获取检查点恢复操作索引
        summary = get_test_summary(self.run_id)
        self.operation_index = summary.get("last_checkpoint_operation", 0)
        self.resumed = True

        # 获取剧本
        script = TEST_SCRIPTS.get(self.test_type, TEST_SCRIPTS["quick_smoke"])
        self.total_operations = len(script["steps"])

        # 计算下一步
        next_idx = self.operation_index
        next_op = script["steps"][next_idx]["name"] if next_idx < len(script["steps"]) else None

        # 更新状态
        save_agent_state(
            AgentState.RUNNING,
            self.run_id,
            self.test_type,
            self.operation_index,
            self.total_operations,
            self.current_operation,
            next_op
        )

        return {
            "success": True,
            "state": AgentState.RUNNING,
            "run_id": self.run_id,
            "test_type": self.test_type,
            "operation_index": self.operation_index,
            "total_operations": self.total_operations,
            "next_operation": next_op,
            "message": f"Test resumed from operation {self.operation_index}",
            "resumed": True,
        }

    def _cmd_status(self, payload: dict) -> dict:
        """查询状态"""
        state = get_agent_state()
        running = get_running_test_run()

        response = {
            "success": True,
            "state": state["state"],
            "operation_index": state["operation_index"],
            "total_operations": state["total_operations"],
            "current_operation": state["current_operation"],
            "next_operation": state["next_operation"],
        }

        if state["run_id"]:
            response["run_id"] = state["run_id"]
            response["test_type"] = state["test_type"]
            summary = get_test_summary(state["run_id"])
            response["anomalies_count"] = summary["total_anomalies"]
            response["critical_count"] = summary["critical"]
            response["high_count"] = summary["high"]

        return response

    def _cmd_stop(self, payload: dict) -> dict:
        """停止测试"""
        reason = payload.get("reason", "User stopped")

        state = get_agent_state()
        if state["run_id"]:
            update_test_run_status(state["run_id"], "interrupted")

        save_agent_state(
            AgentState.IDLE,
            None,
            None,
            0,
            0,
            None,
            None
        )

        # 清理 PID
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

        return {
            "success": True,
            "message": f"Stopped: {reason}",
            "state": AgentState.IDLE,
        }

    def _cmd_advance(self, payload: dict) -> dict:
        """
        推进测试到下一步（由主会话调用）

        主会话每执行完一个测试步骤，调用此命令推进状态。
        """
        state = get_agent_state()

        if state["state"] != AgentState.RUNNING:
            return {"success": False, "error": "No test running"}

        current_op = payload.get("current_operation", state["current_operation"])
        anomalies = payload.get("anomalies_count", 0)
        critical = payload.get("critical_count", 0)

        # 获取剧本
        script = TEST_SCRIPTS.get(state["test_type"] or "quick_smoke", TEST_SCRIPTS["quick_smoke"])

        # 推进索引
        self.operation_index = state["operation_index"] + 1
        next_idx = self.operation_index
        next_op = script["steps"][next_idx]["name"] if next_idx < len(script["steps"]) else None

        # 检查是否完成
        if next_idx >= len(script["steps"]):
            # 测试完成
            summary = {
                "total_anomalies": anomalies,
                "critical": critical,
            }
            update_test_run_status(state["run_id"], "completed", json.dumps(summary))
            save_agent_state(
                AgentState.COMPLETED,
                state["run_id"],
                state["test_type"],
                self.operation_index,
                len(script["steps"]),
                current_op,
                None
            )
            return {
                "success": True,
                "state": AgentState.COMPLETED,
                "operation_index": self.operation_index,
                "total_operations": len(script["steps"]),
                "message": "Test completed",
            }

        # 检查是否因异常暂停
        if critical > 0:
            save_agent_state(
                AgentState.PAUSED,
                state["run_id"],
                state["test_type"],
                self.operation_index,
                len(script["steps"]),
                current_op,
                next_op
            )
            return {
                "success": True,
                "state": AgentState.PAUSED,
                "operation_index": self.operation_index,
                "total_operations": len(script["steps"]),
                "next_operation": next_op,
                "message": "Test paused due to critical anomaly",
            }

        # 正常推进
        save_agent_state(
            AgentState.RUNNING,
            state["run_id"],
            state["test_type"],
            self.operation_index,
            len(script["steps"]),
            current_op,
            next_op
        )

        return {
            "success": True,
            "state": AgentState.RUNNING,
            "operation_index": self.operation_index,
            "total_operations": len(script["steps"]),
            "next_operation": next_op,
            "current_operation": current_op,
        }

    def _cmd_report(self, payload: dict) -> dict:
        """获取测试报告 - 返回稳定的 JSON 结构"""
        state = get_agent_state()

        if not state["run_id"]:
            return {
                "success": False,
                "error": "No test run found",
            }

        # 使用 build_report 构建完整报告
        report_data = build_report(state["run_id"])

        return {
            "success": True,
            "report": report_data,
        }


# =============================================================================
# 主入口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Test Runner Agent")
    parser.add_argument("--command", required=True,
                        choices=["start", "resume", "status", "stop", "advance", "report"])
    parser.add_argument("--test-type", default="full_workflow")
    parser.add_argument("--reason", default="")
    parser.add_argument("--current-operation", default="")
    parser.add_argument("--anomalies-count", type=int, default=0)
    parser.add_argument("--critical-count", type=int, default=0)

    args = parser.parse_args()

    agent = TestRunnerAgent()

    payload = {}
    if args.command in ("start",):
        payload["test_type"] = args.test_type
    elif args.command == "stop":
        payload["reason"] = args.reason
    elif args.command == "advance":
        payload["current_operation"] = args.current_operation
        payload["anomalies_count"] = args.anomalies_count
        payload["critical_count"] = args.critical_count

    result = agent.handle_command(args.command, payload)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
