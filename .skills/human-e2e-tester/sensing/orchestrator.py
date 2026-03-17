# -*- coding: utf-8 -*-
"""
TestSensingOrchestrator - 测试感知协调器

整合所有感知层，在每个测试步骤后自动执行感知和分析，
汇总异常并输出感知报告。支持断点续传。
"""

import uuid
import json
from datetime import datetime
from typing import Optional, Any

from .snapshot import (
    PageSnapshot,
    WorkflowPosition,
    AnomalyReport,
    ConsistencyCheck,
    TestContext,
    WORKFLOW_TRANSITIONS,
)
from .page_observer import sense_page
from .workflow_detector import (
    detect_workflow_position,
    detect_workflow_anomalies,
    detect_illegal_transition,
)
from .anomaly_detector import detect_all_anomalies
from .consistency_verifier import verify_all_consistency
from .storage import (
    SQLiteStorage,
    TestRun,
    Checkpoint,
    Snapshot as StorageSnapshot,
    Anomaly as StorageAnomaly,
    ConsistencyCheckRecord,
    WorkflowPositionRecord,
)


class SensingOrchestrator:
    """
    感知协调器 - 整合所有感知层，支持断点续传

    使用流程：
    1. 测试开始 → __init__() 自动检测是否需要续传
    2. 每个操作前 → snapshot_before() 记录前置状态
    3. 每个操作后 → snapshot_after() 记录后置状态并分析
    4. 测试结束 → generate_report() / finalize() 生成报告并写入数据库
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        checkpoint_interval: int = 10,
        run_id: Optional[str] = None,
        test_type: str = "full_workflow",
    ):
        """
        初始化感知协调器

        Args:
            db_path: SQLite 数据库路径，默认为 test_reports/e2e_sensing.db
            checkpoint_interval: 每 N 步强制断点，默认 10
            run_id: 可选，指定测试运行 ID，不指定则生成新的或从数据库恢复
            test_type: 测试类型 full_workflow / rbac / single_order
        """
        self.db = SQLiteStorage(db_path)
        self.checkpoint_interval = checkpoint_interval
        self.test_type = test_type

        # 尝试恢复未完成的测试
        self.run_id = run_id
        self.resumed_from_checkpoint = False
        self.cp_id: Optional[str] = None  # 当前检查点 ID

        existing_run = self.db.get_running_test_run()
        if existing_run and not run_id:
            # 有未完成的测试，询问是否恢复
            # 这里采用自动恢复策略：直接恢复
            latest_cp = self.db.get_latest_checkpoint(existing_run.run_id)
            if latest_cp:
                self._restore_from_checkpoint(latest_cp)
                self.run_id = existing_run.run_id
                self.resumed_from_checkpoint = True
            else:
                # 有运行记录但没有检查点，创建新运行
                self.run_id = str(uuid.uuid4())
                self._start_new_run()
        elif run_id:
            # 指定了 run_id，检查是否存在
            existing = self.db.get_test_run(run_id)
            if existing and existing.status == "running":
                latest_cp = self.db.get_latest_checkpoint(run_id)
                if latest_cp:
                    self._restore_from_checkpoint(latest_cp)
                    self.resumed_from_checkpoint = True
                else:
                    # 有 running run_id 但无检查点，生成新 run_id 避免 UNIQUE 冲突
                    self.run_id = str(uuid.uuid4())
                    self._start_new_run()
            else:
                self._start_new_run()
        else:
            # 创建新测试运行
            self.run_id = str(uuid.uuid4())
            self._start_new_run()

    def _start_new_run(self):
        """开始新的测试运行"""
        test_run = TestRun(
            run_id=self.run_id,
            started_at=datetime.now().isoformat(),
            status="running",
            test_type=self.test_type,
        )
        self.db.insert_test_run(test_run)

        # 重置内存中的数据
        self.context = TestContext()
        self.before_snapshot: Optional[PageSnapshot] = None
        self.after_snapshot: Optional[PageSnapshot] = None
        self.workflow_positions: list[WorkflowPosition] = []
        self.all_anomalies: list[AnomalyReport] = []
        self.all_checks: list[ConsistencyCheck] = []
        self.list_snapshot: Optional[PageSnapshot] = None
        self.operation_count = 0
        self.last_cp_operation_count = 0

    def _restore_from_checkpoint(self, cp: Checkpoint):
        """从检查点恢复"""
        # 解析上下文
        context_data = json.loads(cp.context_json)
        self.context = TestContext()
        self.context.current_user = context_data.get("current_user", "")
        self.context.current_role = context_data.get("current_role", "")
        self.context.current_org = context_data.get("current_org", "")
        self.context.current_order_no = context_data.get("current_order_no")
        self.context.current_order_status = context_data.get("current_order_status")
        self.context.current_order_type = context_data.get("current_order_type", "outbound")

        self.operation_count = cp.operation_index
        self.last_cp_operation_count = cp.operation_index

        # 从数据库加载已有的感知数据（用于报告）
        self.all_anomalies = []
        self.all_checks = []
        self.workflow_positions = []

        # 加载已存储的数据到内存
        db_anomalies = self.db.get_anomalies_for_run(self.run_id)
        db_checks = self.db.get_consistency_checks_for_run(self.run_id)
        db_positions = self.db.get_workflow_positions_for_run(self.run_id)

        for a in db_anomalies:
            self.all_anomalies.append(AnomalyReport(
                anomaly_type=a.anomaly_type,
                severity=a.severity,
                description=a.description,
                page_name=a.page_name,
                order_no=a.order_no,
                evidence=json.loads(a.evidence_json) if a.evidence_json else {},
            ))

        for c in db_checks:
            self.all_checks.append(ConsistencyCheck(
                check_name=c.check_name,
                passed=bool(c.passed),
                expected=c.expected,
                actual=c.actual,
                details=c.details,
                order_no=c.order_no,
            ))

        self.before_snapshot = None
        self.after_snapshot = None
        self.list_snapshot = None
        self.cp_id = cp.cp_id

    def reset(self, user: str = "", role: str = "", org: str = ""):
        """重置上下文，准备新测试（仅重置内存中的上下文）"""
        self.context = TestContext()
        self.context.current_user = user
        self.context.current_role = role
        self.context.current_org = org
        self.before_snapshot = None
        self.after_snapshot = None
        self.workflow_positions = []
        self.all_anomalies = []
        self.all_checks = []
        self.list_snapshot = None
        self.operation_count = 0
        self.last_cp_operation_count = 0

    def set_user_context(self, user: str, role: str, org: str = ""):
        """设置用户上下文"""
        self.context.current_user = user
        self.context.current_role = role
        self.context.current_org = org

    def set_order_context(self, order_no: str, order_status: str = "", order_type: str = "outbound"):
        """设置订单上下文"""
        self.context.current_order_no = order_no
        self.context.current_order_status = order_status
        self.context.current_order_type = order_type

    def snapshot_before(self, driver) -> PageSnapshot:
        """
        操作前快照

        在执行操作前调用，记录当前页面状态

        Args:
            driver: Selenium WebDriver 或 Playwright Page 对象

        Returns:
            PageSnapshot
        """
        self.before_snapshot = sense_page(driver, self.context)
        return self.before_snapshot

    def snapshot_after(
        self,
        driver,
        operation: str,
        api_response: Optional[Any] = None,
        expected_next_status: Optional[str] = None
    ) -> tuple[PageSnapshot, list[AnomalyReport], list[ConsistencyCheck]]:
        """
        操作后快照和分析

        在执行操作后调用，记录页面状态并执行全面感知分析

        Args:
            driver: Selenium WebDriver 或 Playwright Page 对象
            operation: 执行的操作用于记录
            api_response: API 响应对象（如果有）
            expected_next_status: 期望的下一状态（用于状态转换验证）

        Returns:
            (PageSnapshot, 异常列表, 一致性检查列表)
        """
        self.operation_count += 1

        # 记录操作和 API 响应
        self.context.record_operation(operation)
        if api_response:
            self.context.record_api_call(api_response)

        # 获取操作后快照
        self.after_snapshot = sense_page(driver, self.context)

        # 首次访问列表页时保存快照（用于后续详情页对比）
        if self.after_snapshot.page_name == "OrderList" and self.list_snapshot is None:
            self.list_snapshot = self.after_snapshot

        anomalies = []
        checks = []

        # 1. 基础异常检测
        page_anomalies = detect_all_anomalies(self.after_snapshot, self.context)
        anomalies.extend(page_anomalies)

        # 2. 工作流检测
        position = detect_workflow_position(self.after_snapshot, self.context)
        self.workflow_positions.append(position)

        workflow_anomalies = detect_workflow_anomalies(self.after_snapshot, position, self.context)
        anomalies.extend(workflow_anomalies)

        # 3. 状态转换验证
        if expected_next_status and self.before_snapshot:
            before_state = self.context.current_order_status
            if before_state and before_state != expected_next_status:
                transition_anomaly = detect_illegal_transition(
                    before_state, expected_next_status,
                    self.context.current_order_type or "outbound",
                    self.context
                )
                if transition_anomaly:
                    anomalies.append(transition_anomaly)

        # 4. 数据一致性验证
        consistency_checks, consistency_anomalies = verify_all_consistency(
            self.after_snapshot, self.context, self.list_snapshot
        )
        checks.extend(consistency_checks)
        anomalies.extend(consistency_anomalies)

        # 更新上下文状态
        if position.current_state != "unknown":
            self.context.current_order_status = position.current_state

        # 汇总异常到内存
        self.all_anomalies.extend(anomalies)
        self.all_checks.extend(checks)

        # 立即写入数据库（持久化）
        self._persist_sensing_data(self.after_snapshot, anomalies, checks, position)

        # 检查是否需要断点
        if self._should_checkpoint():
            self._write_checkpoint()

        return self.after_snapshot, anomalies, checks

    def _persist_sensing_data(
        self,
        snapshot: PageSnapshot,
        anomalies: list[AnomalyReport],
        checks: list[ConsistencyCheck],
        position: WorkflowPosition,
    ):
        """将感知数据持久化到数据库"""
        now = datetime.now().isoformat()
        snap_id = f"snap_{self.run_id}_{self.operation_count}"

        # 存储快照（大数据单独存储，不放在检查点）
        storage_snap = StorageSnapshot(
            snap_id=snap_id,
            cp_id=self.cp_id,
            run_id=self.run_id,
            created_at=now,
            page_name=snapshot.page_name,
            order_no=snapshot.order_no,
            order_status=snapshot.order_status,
            table_rows=snapshot.table_rows,
            visible_buttons=json.dumps(snapshot.visible_buttons, ensure_ascii=False),
            error_message=snapshot.error_message,
            raw_text=snapshot.raw_text[:5000] if snapshot.raw_text else "",  # 限制长度
            raw_html="",  # HTML 太大，不存储在快照表
        )
        self.db.insert_snapshot(storage_snap)

        # 存储异常
        for anomaly in anomalies:
            anomaly_id = f"anomaly_{uuid.uuid4().hex[:8]}"
            storage_anomaly = StorageAnomaly(
                anomaly_id=anomaly_id,
                cp_id=self.cp_id,
                run_id=self.run_id,
                created_at=now,
                anomaly_type=anomaly.anomaly_type,
                severity=anomaly.severity,
                description=anomaly.description[:1000] if anomaly.description else "",
                page_name=anomaly.page_name,
                order_no=anomaly.order_no,
                evidence_json=json.dumps(anomaly.evidence, ensure_ascii=False) if anomaly.evidence else "{}",
            )
            self.db.insert_anomaly(storage_anomaly)

        # 存储一致性检查
        for check in checks:
            check_id = f"check_{uuid.uuid4().hex[:8]}"
            storage_check = ConsistencyCheckRecord(
                check_id=check_id,
                cp_id=self.cp_id,
                run_id=self.run_id,
                created_at=now,
                check_name=check.check_name,
                passed=1 if check.passed else 0,
                expected=str(check.expected)[:500] if check.expected else "",
                actual=str(check.actual)[:500] if check.actual else "",
                details=check.details[:1000] if check.details else "",
                order_no=check.order_no,
            )
            self.db.insert_consistency_check(storage_check)

        # 存储工作流位置
        pos_id = f"pos_{uuid.uuid4().hex[:8]}"
        storage_pos = WorkflowPositionRecord(
            pos_id=pos_id,
            cp_id=self.cp_id,
            run_id=self.run_id,
            created_at=now,
            order_no=position.order_no,
            current_state=position.current_state,
            current_label=position.current_state_label,
            buttons_match=1 if position.actual_buttons_match else 0,
        )
        self.db.insert_workflow_position(storage_pos)

    def _should_checkpoint(self) -> bool:
        """
        判断是否应该写入断点

        触发条件：
        1. 每 checkpoint_interval 步强制断点
        2. 发现 critical 异常
        3. 操作数超过上次断点后有一定增量
        """
        # 强制断点条件
        if self.operation_count % self.checkpoint_interval == 0:
            return True

        # 有 critical 异常立即断点
        if self._has_critical_anomaly():
            return True

        return False

    def _has_critical_anomaly(self) -> bool:
        """检查是否有 critical 异常"""
        # 只检查自上次断点以来的新异常
        for anomaly in self.all_anomalies:
            if anomaly.severity == "critical":
                return True
        return False

    def _predict_next_operation(self) -> str:
        """预测下一步操作"""
        current_state = self.context.current_order_status
        order_type = self.context.current_order_type or "outbound"

        transitions = WORKFLOW_TRANSITIONS.get(order_type, {})
        allowed = transitions.get(current_state, [])

        # 根据当前状态返回预期的下一步
        state_next_op_map = {
            "draft": "submit",
            "submitted": "keeper_confirm",
            "keeper_confirmed": "notify_transport",
            "transport_notified": "transport_start",
            "transport_in_progress": "transport_complete",
            "transport_completed": "final_confirm",
            "final_confirmation_pending": "final_confirm",
            "rejected": "resubmit",
        }

        return state_next_op_map.get(current_state, "unknown")

    def _predict_next_status(self) -> str:
        """预测下一步状态"""
        current_state = self.context.current_order_status
        order_type = self.context.current_order_type or "outbound"

        transitions = WORKFLOW_TRANSITIONS.get(order_type, {})
        allowed = transitions.get(current_state, [])

        if allowed:
            return allowed[0]  # 返回第一个允许的转换
        return current_state

    def _write_checkpoint(self):
        """写入检查点"""
        cp_id = f"cp_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()

        # 序列号上下文（不含大数据）
        context_data = {
            "current_user": self.context.current_user,
            "current_role": self.context.current_role,
            "current_org": self.context.current_org,
            "current_order_no": self.context.current_order_no,
            "current_order_status": self.context.current_order_status,
            "current_order_type": self.context.current_order_type,
        }

        cp = Checkpoint(
            cp_id=cp_id,
            run_id=self.run_id,
            created_at=now,
            operation_index=self.operation_count,
            context_json=json.dumps(context_data, ensure_ascii=False),
            next_expected_op=self._predict_next_operation(),
            next_expected_status=self._predict_next_status(),
        )

        self.db.insert_checkpoint(cp)
        self.cp_id = cp_id
        self.last_cp_operation_count = self.operation_count

    def resume(self) -> Optional[Checkpoint]:
        """获取当前可恢复的检查点"""
        return self.db.get_latest_checkpoint(self.run_id)

    def finalize(self, status: str = "completed"):
        """
        结束测试运行

        Args:
            status: completed / interrupted
        """
        summary = self.generate_summary()
        self.db.update_test_run_status(
            self.run_id,
            status,
            json.dumps(summary, ensure_ascii=False),
        )

    def get_critical_anomalies(self) -> list[AnomalyReport]:
        """获取严重异常"""
        return [a for a in self.all_anomalies if a.severity == "critical"]

    def get_high_anomalies(self) -> list[AnomalyReport]:
        """获取高优先级异常"""
        return [a for a in self.all_anomalies if a.severity == "high"]

    def generate_summary(self) -> dict:
        """生成汇总数据（不含详情，用于数据库存储）"""
        return {
            "total_anomalies": len(self.all_anomalies),
            "critical": len([a for a in self.all_anomalies if a.severity == "critical"]),
            "high": len([a for a in self.all_anomalies if a.severity == "high"]),
            "medium": len([a for a in self.all_anomalies if a.severity == "medium"]),
            "low": len([a for a in self.all_anomalies if a.severity == "low"]),
            "total_consistency_checks": len(self.all_checks),
            "passed_checks": len([c for c in self.all_checks if c.passed]),
            "failed_checks": len([c for c in self.all_checks if not c.passed]),
            "operation_count": self.operation_count,
            "resumed": self.resumed_from_checkpoint,
        }

    def generate_report(self) -> dict:
        """
        生成感知报告

        Returns:
            包含所有感知结果的字典
        """
        report = {
            "run_id": self.run_id,
            "test_type": self.test_type,
            "resumed_from_checkpoint": self.resumed_from_checkpoint,
            "operation_count": self.operation_count,
            "summary": self.generate_summary(),
            "anomalies": [a.to_dict() for a in self.all_anomalies],
            "consistency_checks": [c.to_dict() for c in self.all_checks],
            "workflow_positions": [
                {
                    "order_no": p.order_no,
                    "state": p.current_state,
                    "label": p.current_state_label,
                    "buttons_match": p.actual_buttons_match,
                }
                for p in self.workflow_positions
            ],
            "context": {
                "user": self.context.current_user,
                "role": self.context.current_role,
                "order_no": self.context.current_order_no,
                "order_status": self.context.current_order_status,
            },
        }

        return report

    def get_full_report(self) -> dict:
        """
        从数据库获取完整报告（包含所有检查点的数据）

        用于测试中断后重新加载并生成最终报告。
        """
        all_data = self.db.get_all_for_run(self.run_id)

        # 重建异常列表
        anomalies = []
        for a in all_data["anomalies"]:
            anomalies.append(AnomalyReport(
                anomaly_type=a.anomaly_type,
                severity=a.severity,
                description=a.description,
                page_name=a.page_name,
                order_no=a.order_no,
                evidence=json.loads(a.evidence_json) if a.evidence_json else {},
            ))

        # 重建一致性检查列表
        checks = []
        for c in all_data["consistency_checks"]:
            checks.append(ConsistencyCheck(
                check_name=c.check_name,
                passed=bool(c.passed),
                expected=c.expected,
                actual=c.actual,
                details=c.details,
                order_no=c.order_no,
            ))

        # 重建工作流位置列表
        positions = []
        for p in all_data["workflow_positions"]:
            positions.append({
                "order_no": p.order_no,
                "state": p.current_state,
                "label": p.current_label,
                "buttons_match": bool(p.buttons_match),
            })

        summary = self.db.get_run_summary(self.run_id)
        test_run = all_data["test_run"]

        return {
            "run_id": self.run_id,
            "test_type": test_run.test_type if test_run else self.test_type,
            "status": test_run.status if test_run else "unknown",
            "started_at": test_run.started_at if test_run else None,
            "ended_at": test_run.ended_at if test_run else None,
            "summary": summary,
            "anomalies": [a.to_dict() for a in anomalies],
            "consistency_checks": [c.to_dict() for c in checks],
            "workflow_positions": positions,
        }

    def has_blocking_issues(self) -> bool:
        """是否有阻断性问题（critical 或 high 级别异常）"""
        blocking = [a for a in self.all_anomalies if a.severity in ("critical", "high")]
        return len(blocking) > 0

    def should_trigger_self_healing(self) -> bool:
        """是否应该触发自愈流程"""
        critical = [a for a in self.all_anomalies if a.severity == "critical"]
        return len(critical) > 0
