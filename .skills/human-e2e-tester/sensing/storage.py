# -*- coding: utf-8 -*-
"""
SQLite Storage Layer - 断点续传数据持久化

提供检查点、页面快照、异常记录、一致性检查、工作流位置等数据的
CRUD 操作，支持测试中断后的续传。
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Any
from dataclasses import dataclass, asdict


# 数据库路径 - 使用绝对路径确保一致性
# storage.py 位于: .skills/human-e2e-tester/sensing/storage.py
# 向上3层到达 .skills，再向上一层到达仓库根目录
_SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_ROOT = os.path.dirname(_SKILLS_DIR)
DB_PATH = os.path.join(_REPO_ROOT, "test_reports", "e2e_sensing.db")


def get_db_path() -> str:
    """获取数据库路径"""
    return DB_PATH


def ensure_db_dir():
    """确保数据库目录存在"""
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)


# =============================================================================
# 数据结构定义
# =============================================================================

@dataclass
class TestRun:
    """测试运行记录"""
    run_id: str
    started_at: str
    ended_at: Optional[str] = None
    status: str = "running"          # running / completed / interrupted
    test_type: str = "full_workflow"  # full_workflow / rbac / single_order
    summary_json: Optional[str] = None


@dataclass
class Checkpoint:
    """检查点"""
    cp_id: str
    run_id: str
    created_at: str
    operation_index: int
    context_json: str                 # TestContext 序列化后的 JSON
    next_expected_op: Optional[str] = None
    next_expected_status: Optional[str] = None


@dataclass
class Snapshot:
    """页面快照"""
    snap_id: str
    cp_id: Optional[str]
    run_id: str
    created_at: str
    page_name: str = ""
    order_no: Optional[str] = None
    order_status: Optional[str] = None
    table_rows: int = 0
    visible_buttons: str = "[]"       # JSON 数组
    error_message: Optional[str] = None
    raw_text: str = ""
    raw_html: str = ""


@dataclass
class Anomaly:
    """异常记录"""
    anomaly_id: str
    cp_id: Optional[str]
    run_id: str
    created_at: str
    anomaly_type: str = ""
    severity: str = ""
    description: str = ""
    page_name: str = ""
    order_no: Optional[str] = None
    evidence_json: str = "{}"


@dataclass
class ConsistencyCheckRecord:
    """一致性检查记录"""
    check_id: str
    cp_id: Optional[str]
    run_id: str
    created_at: str
    check_name: str = ""
    passed: int = 1                  # SQLite 没有 bool，用 int
    expected: str = ""
    actual: str = ""
    details: str = ""
    order_no: Optional[str] = None


@dataclass
class WorkflowPositionRecord:
    """工作流位置记录"""
    pos_id: str
    cp_id: Optional[str]
    run_id: str
    created_at: str
    order_no: Optional[str] = None
    current_state: str = ""
    current_label: str = ""
    buttons_match: int = 1


@dataclass
class RbacResultRecord:
    """RBAC 测试结果记录"""
    rbac_id: str
    run_id: str
    created_at: str
    role: str
    permission: str
    expected: str
    actual: str
    status: str
    description: str = ""
    endpoint: str = ""
    method: str = ""
    actual_status_code: Optional[int] = None
    details: str = ""


# =============================================================================
# SQLite Storage 类
# =============================================================================

class SQLiteStorage:
    """
    SQLite 存储层

    提供测试数据的持久化存储，支持断点续传。
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = get_db_path()

        ensure_db_dir()
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        """初始化数据库 schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 测试运行记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                run_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                status TEXT DEFAULT 'running',
                test_type TEXT DEFAULT 'full_workflow',
                summary_json TEXT
            )
        """)

        # 检查点
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                cp_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                operation_index INTEGER DEFAULT 0,
                context_json TEXT,
                next_expected_op TEXT,
                next_expected_status TEXT,
                FOREIGN KEY (run_id) REFERENCES test_runs(run_id)
            )
        """)

        # 页面快照
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snap_id TEXT PRIMARY KEY,
                cp_id TEXT,
                run_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                page_name TEXT,
                order_no TEXT,
                order_status TEXT,
                table_rows INTEGER DEFAULT 0,
                visible_buttons TEXT DEFAULT '[]',
                error_message TEXT,
                raw_text TEXT,
                raw_html TEXT,
                FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
                FOREIGN KEY (cp_id) REFERENCES checkpoints(cp_id)
            )
        """)

        # 异常记录
        cursor.execute("""
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
                evidence_json TEXT DEFAULT '{}',
                FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
                FOREIGN KEY (cp_id) REFERENCES checkpoints(cp_id)
            )
        """)

        # 一致性检查
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consistency_checks (
                check_id TEXT PRIMARY KEY,
                cp_id TEXT,
                run_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                check_name TEXT,
                passed INTEGER DEFAULT 1,
                expected TEXT,
                actual TEXT,
                details TEXT,
                order_no TEXT,
                FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
                FOREIGN KEY (cp_id) REFERENCES checkpoints(cp_id)
            )
        """)

        # 工作流位置
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_positions (
                pos_id TEXT PRIMARY KEY,
                cp_id TEXT,
                run_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                order_no TEXT,
                current_state TEXT,
                current_label TEXT,
                buttons_match INTEGER DEFAULT 1,
                FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
                FOREIGN KEY (cp_id) REFERENCES checkpoints(cp_id)
            )
        """)

        # RBAC 测试结果
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rbac_results (
                rbac_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                role TEXT NOT NULL,
                permission TEXT NOT NULL,
                expected TEXT NOT NULL,
                actual TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT,
                endpoint TEXT,
                method TEXT,
                actual_status_code INTEGER,
                details TEXT,
                FOREIGN KEY (run_id) REFERENCES test_runs(run_id)
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_run ON checkpoints(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_run ON snapshots(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_cp ON snapshots(cp_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_run ON anomalies(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_cp ON anomalies(cp_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consistency_run ON consistency_checks(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_run ON workflow_positions(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rbac_results_run ON rbac_results(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rbac_results_role ON rbac_results(role)")

        conn.commit()
        conn.close()

    def commit(self):
        """提交事务（空操作，保留接口兼容）"""
        pass

    # =========================================================================
    # TestRun 操作
    # =========================================================================

    def insert_test_run(self, run: TestRun):
        """插入测试运行记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_runs (run_id, started_at, ended_at, status, test_type, summary_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (run.run_id, run.started_at, run.ended_at, run.status, run.test_type, run.summary_json))
        conn.commit()
        conn.close()

    def update_test_run_status(self, run_id: str, status: str, summary_json: Optional[str] = None):
        """更新测试运行状态"""
        conn = self._get_connection()
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

    def get_running_test_run(self) -> Optional[TestRun]:
        """获取最近一个 running/interrupted 状态的测试运行"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM test_runs WHERE status IN ('running', 'interrupted') ORDER BY started_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        if row:
            return TestRun(
                run_id=row["run_id"],
                started_at=row["started_at"],
                ended_at=row["ended_at"],
                status=row["status"],
                test_type=row["test_type"],
                summary_json=row["summary_json"],
            )
        return None

    def get_latest_test_run(self) -> Optional[TestRun]:
        """获取最近一个测试运行（不限状态）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM test_runs ORDER BY started_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        if row:
            return TestRun(
                run_id=row["run_id"],
                started_at=row["started_at"],
                ended_at=row["ended_at"],
                status=row["status"],
                test_type=row["test_type"],
                summary_json=row["summary_json"],
            )
        return None

    def get_test_run(self, run_id: str) -> Optional[TestRun]:
        """获取指定测试运行"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_runs WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return TestRun(
                run_id=row["run_id"],
                started_at=row["started_at"],
                ended_at=row["ended_at"],
                status=row["status"],
                test_type=row["test_type"],
                summary_json=row["summary_json"],
            )
        return None

    # =========================================================================
    # Checkpoint 操作
    # =========================================================================

    def insert_checkpoint(self, cp: Checkpoint):
        """插入检查点"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO checkpoints (cp_id, run_id, created_at, operation_index, context_json, next_expected_op, next_expected_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cp.cp_id, cp.run_id, cp.created_at, cp.operation_index, cp.context_json, cp.next_expected_op, cp.next_expected_status))
        conn.commit()
        conn.close()

    def get_latest_checkpoint(self, run_id: str) -> Optional[Checkpoint]:
        """获取最新的检查点"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM checkpoints WHERE run_id = ? ORDER BY created_at DESC LIMIT 1
        """, (run_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Checkpoint(
                cp_id=row["cp_id"],
                run_id=row["run_id"],
                created_at=row["created_at"],
                operation_index=row["operation_index"],
                context_json=row["context_json"],
                next_expected_op=row["next_expected_op"],
                next_expected_status=row["next_expected_status"],
            )
        return None

    def get_all_checkpoints(self, run_id: str) -> list[Checkpoint]:
        """获取所有检查点"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM checkpoints WHERE run_id = ? ORDER BY created_at ASC
        """, (run_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            Checkpoint(
                cp_id=row["cp_id"],
                run_id=row["run_id"],
                created_at=row["created_at"],
                operation_index=row["operation_index"],
                context_json=row["context_json"],
                next_expected_op=row["next_expected_op"],
                next_expected_status=row["next_expected_status"],
            )
            for row in rows
        ]

    # =========================================================================
    # Snapshot 操作
    # =========================================================================

    def insert_snapshot(self, snap: Snapshot):
        """插入页面快照"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO snapshots (snap_id, cp_id, run_id, created_at, page_name, order_no, order_status, table_rows, visible_buttons, error_message, raw_text, raw_html)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (snap.snap_id, snap.cp_id, snap.run_id, snap.created_at, snap.page_name, snap.order_no, snap.order_status, snap.table_rows, snap.visible_buttons, snap.error_message, snap.raw_text, snap.raw_html))
        conn.commit()
        conn.close()

    def get_snapshots_for_run(self, run_id: str) -> list[Snapshot]:
        """获取指定测试运行的所有快照"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM snapshots WHERE run_id = ? ORDER BY created_at ASC
        """, (run_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            Snapshot(
                snap_id=row["snap_id"],
                cp_id=row["cp_id"],
                run_id=row["run_id"],
                created_at=row["created_at"],
                page_name=row["page_name"],
                order_no=row["order_no"],
                order_status=row["order_status"],
                table_rows=row["table_rows"],
                visible_buttons=row["visible_buttons"],
                error_message=row["error_message"],
                raw_text=row["raw_text"],
                raw_html=row["raw_html"],
            )
            for row in rows
        ]

    # =========================================================================
    # Anomaly 操作
    # =========================================================================

    def insert_anomaly(self, anomaly: Anomaly):
        """插入异常记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO anomalies (anomaly_id, cp_id, run_id, created_at, anomaly_type, severity, description, page_name, order_no, evidence_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (anomaly.anomaly_id, anomaly.cp_id, anomaly.run_id, anomaly.created_at, anomaly.anomaly_type, anomaly.severity, anomaly.description, anomaly.page_name, anomaly.order_no, anomaly.evidence_json))
        conn.commit()
        conn.close()

    def get_anomalies_for_run(self, run_id: str) -> list[Anomaly]:
        """获取指定测试运行的所有异常"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM anomalies WHERE run_id = ? ORDER BY created_at ASC
        """, (run_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            Anomaly(
                anomaly_id=row["anomaly_id"],
                cp_id=row["cp_id"],
                run_id=row["run_id"],
                created_at=row["created_at"],
                anomaly_type=row["anomaly_type"],
                severity=row["severity"],
                description=row["description"],
                page_name=row["page_name"],
                order_no=row["order_no"],
                evidence_json=row["evidence_json"],
            )
            for row in rows
        ]

    # =========================================================================
    # ConsistencyCheck 操作
    # =========================================================================

    def insert_consistency_check(self, check: ConsistencyCheckRecord):
        """插入一致性检查记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO consistency_checks (check_id, cp_id, run_id, created_at, check_name, passed, expected, actual, details, order_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (check.check_id, check.cp_id, check.run_id, check.created_at, check.check_name, check.passed, check.expected, check.actual, check.details, check.order_no))
        conn.commit()
        conn.close()

    def get_consistency_checks_for_run(self, run_id: str) -> list[ConsistencyCheckRecord]:
        """获取指定测试运行的所有一致性检查"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM consistency_checks WHERE run_id = ? ORDER BY created_at ASC
        """, (run_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            ConsistencyCheckRecord(
                check_id=row["check_id"],
                cp_id=row["cp_id"],
                run_id=row["run_id"],
                created_at=row["created_at"],
                check_name=row["check_name"],
                passed=row["passed"],
                expected=row["expected"],
                actual=row["actual"],
                details=row["details"],
                order_no=row["order_no"],
            )
            for row in rows
        ]

    # =========================================================================
    # WorkflowPosition 操作
    # =========================================================================

    def insert_workflow_position(self, pos: WorkflowPositionRecord):
        """插入工作流位置记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workflow_positions (pos_id, cp_id, run_id, created_at, order_no, current_state, current_label, buttons_match)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pos.pos_id, pos.cp_id, pos.run_id, pos.created_at, pos.order_no, pos.current_state, pos.current_label, pos.buttons_match))
        conn.commit()
        conn.close()

    def get_workflow_positions_for_run(self, run_id: str) -> list[WorkflowPositionRecord]:
        """获取指定测试运行的所有工作流位置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM workflow_positions WHERE run_id = ? ORDER BY created_at ASC
        """, (run_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            WorkflowPositionRecord(
                pos_id=row["pos_id"],
                cp_id=row["cp_id"],
                run_id=row["run_id"],
                created_at=row["created_at"],
                order_no=row["order_no"],
                current_state=row["current_state"],
                current_label=row["current_label"],
                buttons_match=row["buttons_match"],
            )
            for row in rows
        ]

    # =========================================================================
    # RBAC Result 操作
    # =========================================================================

    def insert_rbac_result(self, result: RbacResultRecord):
        """插入 RBAC 测试结果"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rbac_results (rbac_id, run_id, created_at, role, permission, expected, actual, status, description, endpoint, method, actual_status_code, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (result.rbac_id, result.run_id, result.created_at, result.role, result.permission, result.expected, result.actual, result.status, result.description, result.endpoint, result.method, result.actual_status_code, result.details))
        conn.commit()
        conn.close()

    def get_rbac_results_for_run(self, run_id: str) -> list[RbacResultRecord]:
        """获取指定测试运行的所有 RBAC 结果"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM rbac_results WHERE run_id = ? ORDER BY created_at ASC
        """, (run_id,))
        rows = cursor.fetchall()
        conn.close()

        return [
            RbacResultRecord(
                rbac_id=row["rbac_id"],
                run_id=row["run_id"],
                created_at=row["created_at"],
                role=row["role"],
                permission=row["permission"],
                expected=row["expected"],
                actual=row["actual"],
                status=row["status"],
                description=row["description"] or "",
                endpoint=row["endpoint"] or "",
                method=row["method"] or "",
                actual_status_code=row["actual_status_code"],
                details=row["details"] or "",
            )
            for row in rows
        ]

    def get_rbac_results_summary(self, run_id: str) -> dict:
        """获取 RBAC 测试结果汇总"""
        results = self.get_rbac_results_for_run(run_id)

        total = len(results)
        passed = sum(1 for r in results if r.status == "PASS")
        failed = sum(1 for r in results if r.status == "FAIL")

        by_role = {}
        for r in results:
            if r.role not in by_role:
                by_role[r.role] = {"total": 0, "passed": 0, "failed": 0}
            by_role[r.role]["total"] += 1
            if r.status == "PASS":
                by_role[r.role]["passed"] += 1
            else:
                by_role[r.role]["failed"] += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A",
            "by_role": by_role,
        }

    # =========================================================================
    # 汇总查询
    # =========================================================================

    def get_all_for_run(self, run_id: str) -> dict:
        """获取指定测试运行的完整数据（用于生成报告）"""
        return {
            "test_run": self.get_test_run(run_id),
            "checkpoints": self.get_all_checkpoints(run_id),
            "snapshots": self.get_snapshots_for_run(run_id),
            "anomalies": self.get_anomalies_for_run(run_id),
            "consistency_checks": self.get_consistency_checks_for_run(run_id),
            "workflow_positions": self.get_workflow_positions_for_run(run_id),
            "rbac_results": self.get_rbac_results_for_run(run_id),
        }

    def get_run_summary(self, run_id: str) -> dict:
        """获取测试运行汇总"""
        anomalies = self.get_anomalies_for_run(run_id)
        checks = self.get_consistency_checks_for_run(run_id)
        rbac_results = self.get_rbac_results_for_run(run_id)

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for a in anomalies:
            if a.severity in severity_counts:
                severity_counts[a.severity] += 1

        passed_checks = sum(1 for c in checks if c.passed)
        rbac_passed = sum(1 for r in rbac_results if r.status == "PASS")
        rbac_failed = sum(1 for r in rbac_results if r.status == "FAIL")

        return {
            "total_anomalies": len(anomalies),
            "severity_counts": severity_counts,
            "total_consistency_checks": len(checks),
            "passed_checks": passed_checks,
            "failed_checks": len(checks) - passed_checks,
            "total_rbac_tests": len(rbac_results),
            "rbac_passed": rbac_passed,
            "rbac_failed": rbac_failed,
        }
