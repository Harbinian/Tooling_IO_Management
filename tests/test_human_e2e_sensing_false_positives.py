import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SENSING_ROOT = REPO_ROOT / ".skills" / "human-e2e-tester"
if str(SENSING_ROOT) not in sys.path:
    sys.path.insert(0, str(SENSING_ROOT))

from sensing.anomaly_detector import detect_all_anomalies
from sensing.consistency_verifier import verify_all_consistency
from sensing.orchestrator import SensingOrchestrator
from sensing.snapshot import PageSnapshot, TestContext, WorkflowPosition
from sensing.workflow_detector import (
    detect_illegal_transition,
    detect_workflow_anomalies,
    detect_workflow_position,
    infer_workflow_state,
)


class HumanE2ESensingFalsePositiveTests(unittest.TestCase):
    def test_infer_workflow_state_ignores_login_page(self):
        snapshot = PageSnapshot(
            page_name="Login",
            url="http://localhost:8150/login",
            raw_text="登录 请输入用户名 请输入密码",
        )

        state, label = infer_workflow_state(snapshot)

        self.assertIsNone(state)
        self.assertIsNone(label)

    def test_detect_illegal_transition_skips_non_workflow_target_state(self):
        anomaly = detect_illegal_transition(
            "transport_in_progress",
            "logged_in",
            "outbound",
            TestContext(current_order_no="OUT001"),
        )

        self.assertIsNone(anomaly)

    def test_empty_order_page_becomes_medium_blank_page_instead_of_critical_blocked(self):
        snapshot = PageSnapshot(
            page_name="OrderList",
            url="http://localhost:8150/tool-io",
            raw_text="",
        )
        position = detect_workflow_position(snapshot, TestContext())

        anomalies = detect_workflow_anomalies(snapshot, position, TestContext())

        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0].anomaly_type, "blank_page")
        self.assertEqual(anomalies[0].severity, "medium")

    def test_silent_fail_skips_test_navigation_operations(self):
        snapshot = PageSnapshot(
            page_name="Dashboard",
            url="http://localhost:8150/",
            raw_text="首页",
        )
        context = TestContext(
            last_operation="smoke_login",
            last_operation_type="test_action",
            last_api_called=True,
            last_api_response={"login_success": True},
        )

        anomalies = detect_all_anomalies(snapshot, context)

        self.assertFalse(any(a.anomaly_type == "silent_fail" for a in anomalies))

    def test_silent_fail_skips_successful_submit_summary_response(self):
        snapshot = PageSnapshot(
            page_name="OrderCreate",
            url="http://localhost:8150/create",
            raw_text="创建出库单",
        )
        context = TestContext(
            last_operation="pw_wf_submit_order",
            last_operation_type="user_action",
            last_api_called=True,
            last_api_response={"submitted": True},
        )

        anomalies = detect_all_anomalies(snapshot, context)

        self.assertFalse(any(a.anomaly_type == "silent_fail" for a in anomalies))

    def test_silent_fail_still_reports_failed_submit_without_feedback(self):
        snapshot = PageSnapshot(
            page_name="OrderCreate",
            url="http://localhost:8150/create",
            raw_text="创建出库单",
        )
        context = TestContext(
            last_operation="pw_wf_submit_order",
            last_operation_type="user_action",
            last_api_called=True,
            last_api_response={"status_code": 500, "body": {"error": "db failed"}},
        )

        anomalies = detect_all_anomalies(snapshot, context)

        self.assertTrue(any(a.anomaly_type == "silent_fail" for a in anomalies))

    def test_silent_fail_skips_login_redirect_pages(self):
        snapshot = PageSnapshot(
            page_name="Login",
            url="http://localhost:8150/login",
            raw_text="登录",
        )
        context = TestContext(
            last_operation="pw_wf_submit_order",
            last_operation_type="user_action",
            last_api_called=True,
            last_api_response={"status_code": 401, "body": {"error": "unauthorized"}},
        )

        anomalies = detect_all_anomalies(snapshot, context)

        self.assertFalse(any(a.anomaly_type == "silent_fail" for a in anomalies))

    def test_orchestrator_classifies_submit_as_user_action(self):
        self.assertEqual(
            SensingOrchestrator._infer_operation_type("pw_wf_submit_order"),
            "user_action",
        )
        self.assertEqual(
            SensingOrchestrator._infer_operation_type("pw_wf_open_tool_search"),
            "test_action",
        )

    def test_status_mapping_only_checked_on_workflow_pages(self):
        snapshot = PageSnapshot(
            page_name="OrderCreate",
            url="http://localhost:8150/create",
            raw_text="创建出库单",
        )
        context = TestContext(current_order_no="OUT001", current_order_status="submitted")

        checks, anomalies = verify_all_consistency(snapshot, context)

        self.assertFalse(any(c.check_name == "status_label_exists" for c in checks))
        self.assertFalse(any(a.anomaly_type == "status_mismatch" for a in anomalies))

    def test_dashboard_text_does_not_trigger_button_visibility_checks(self):
        snapshot = PageSnapshot(
            page_name="Dashboard",
            url="http://localhost:8150/",
            raw_text="运输中 统计看板",
        )
        position = detect_workflow_position(snapshot, TestContext(current_order_type="outbound"))

        self.assertEqual(position.current_state, "unknown")
        anomalies = detect_workflow_anomalies(snapshot, position, TestContext())
        self.assertEqual(anomalies, [])


if __name__ == "__main__":
    unittest.main()
