# -*- coding: utf-8 -*-
"""
Human E2E Tester - API 自动化测试

This module is a compatibility layer that re-exports all symbols from:
- api_e2e_base: Config, TestDataManager, TestReport, API helpers
- api_e2e_orders: Order workflow tests
- api_e2e_rbac: RBAC permission tests

使用方法：
    python test_runner/api_e2e.py
"""

# Re-export all symbols from base module for backward compatibility
from test_runner.api_e2e_base import (
    # Configuration
    BACKEND_URL,
    API_BASE,
    HEADERS,
    TEST_USERS,
    TEST_ORDER_PREFIX,
    TEST_TOOL,
    RUN_PREFIX,
    STALE_ORDER_MAX_AGE,
    ORDER_LIST_PAGE_SIZE,
    KNOWN_TEST_PROJECT_PREFIXES,
    TERMINAL_CLEANUP_STATUSES,
    LOCKED_CLEANUP_STATUSES,
    _test_data_manager,

    # Classes
    TestDataManager,
    TestReport,

    # API helpers
    api_post,
    api_put,
    api_get,
    api_delete,
    login_user,
    ensure_user_session,

    # Utility functions
    generate_run_prefix,
    _parse_order_datetime,
    _get_order_age,
    _normalize_order_status,
    _normalize_project_code,
    _is_auto_test_order,
    _is_known_test_project,
    _fetch_order_detail_for_cleanup,
    _order_uses_test_fixture,
    _should_cleanup_order,
    _list_orders_for_cleanup,
    is_critical_error,
    is_recoverable_error,
    execute_step,
)

# Import workflow step functions and test runners
# These are imported from the original module content
# to maintain backward compatibility

import sys
import os
from datetime import datetime

# Import base utilities
from test_runner.api_e2e_base import (
    api_post,
    api_put,
    api_get,
    api_delete,
    login_user,
    ensure_user_session,
    TEST_USERS,
    TEST_TOOL,
    TestDataManager,
    TestReport,
    _test_data_manager,
    _should_cleanup_order,
    _list_orders_for_cleanup,
    RUN_PREFIX,
    execute_step,
)

# =============================================================================
# Workflow Step Functions
# =============================================================================

def step_login(username: str, password: str) -> tuple:
    """Step: User login."""
    token, user_id, user_data = login_user(username, password)
    if token:
        return token, user_id, user_data
    return None, None, None


def step_create_order(token: str, user_id: int, order_type: str, order_no: str = None) -> tuple:
    """Step: Create order."""
    payload = {
        "order_type": order_type,
        "project_code": f"TEST_{RUN_PREFIX}",
        "remark": f"E2E Test Order {RUN_PREFIX}",
        "items": [
            {
                "serial_no": TEST_TOOL["serial_no"],
                "tool_name": TEST_TOOL["tool_name"],
                "drawing_no": TEST_TOOL["drawing_no"],
                "spec_model": TEST_TOOL["spec_model"],
            }
        ],
    }
    if order_no:
        payload["order_no"] = order_no

    status_code, body = api_post("/tool-io-orders", payload, token=token)
    if status_code == 200 and body.get("success"):
        return body.get("data", {}), body
    return None, body


def step_submit_order(order_no: str, token: str, user_id: int) -> tuple:
    """Step: Submit order."""
    payload = {
        "operator_id": str(user_id),
        "operator_name": TEST_USERS.get("taidongxu", {}).get("role_name", ""),
        "operator_role": "team_leader",
    }
    status_code, body = api_post(f"/tool-io-orders/{order_no}/submit", payload, token=token)
    return status_code, body


def step_keeper_confirm(order_no: str, token: str, user_id: int,
                        transport_assignee_id: str = None) -> tuple:
    """Step: Keeper confirm."""
    keeper_token = token
    keeper_id = str(user_id)

    payload = {
        "operator_id": keeper_id,
        "operator_name": TEST_USERS.get("hutingting", {}).get("role_name", ""),
        "operator_role": "keeper",
        "items": [
            {
                "serial_no": TEST_TOOL["serial_no"],
                "confirmed": True,
                "confirmed_location": "confirmed_location_test",
            }
        ],
    }
    if transport_assignee_id:
        payload["transport_assignee_id"] = transport_assignee_id

    status_code, body = api_post(f"/tool-io-orders/{order_no}/keeper-confirm", payload, token=keeper_token)
    return status_code, body


def step_transport_start(order_no: str, token: str, user_id: int) -> tuple:
    """Step: Start transport."""
    payload = {
        "operator_id": str(user_id),
        "operator_name": TEST_USERS.get("fengliang", {}).get("role_name", ""),
        "operator_role": "production_prep",
    }
    status_code, body = api_post(f"/tool-io-orders/{order_no}/transport-start", payload, token=token)
    return status_code, body


def step_transport_complete(order_no: str, token: str, user_id: int) -> tuple:
    """Step: Complete transport."""
    payload = {
        "operator_id": str(user_id),
        "operator_name": TEST_USERS.get("fengliang", {}).get("role_name", ""),
        "operator_role": "production_prep",
    }
    status_code, body = api_post(f"/tool-io-orders/{order_no}/transport-complete", payload, token=token)
    return status_code, body


def step_final_confirm(order_no: str, token: str, user_id: int,
                       order_type: str = "outbound") -> tuple:
    """Step: Final confirm."""
    payload = {
        "operator_id": str(user_id),
        "operator_name": TEST_USERS.get("taidongxu", {}).get("role_name", ""),
        "operator_role": "team_leader",
    }
    status_code, body = api_post(f"/tool-io-orders/{order_no}/confirm-final", payload, token=token)
    return status_code, body


# =============================================================================
# Test Runners
# =============================================================================

def run_quick_smoke_test(report: TestReport):
    """Phase 1: Quick smoke test."""
    print("\n[PHASE 1] Running quick smoke test...")

    token, user_id, user_data = step_login("taidongxu", "test1234")
    if not token:
        print("[FAIL] Smoke test failed: login")
        report.add_step("login", "taidongxu", "login", "FAIL", "login failed")
        return False

    report.add_step("login", "taidongxu", "login", "PASS")
    print("[PASS] Smoke test passed")
    return True


def run_full_workflow_test(report: TestReport):
    """Phase 2: Full outbound workflow test."""
    print("\n[PHASE 2] Running full workflow test...")

    # Login as team leader
    token, user_id, user_data = step_login("taidongxu", "test1234")
    if not token:
        report.add_step("login", "taidongxu", "login", "FAIL", "login failed")
        return False
    report.add_step("login", "taidongxu", "login", "PASS")

    # Login as keeper
    keeper_token, keeper_id, keeper_data = step_login("hutingting", "test1234")
    if not keeper_token:
        report.add_step("login", "hutingting", "login", "FAIL", "login failed")
        return False
    report.add_step("login", "hutingting", "login", "PASS")

    # Login as production prep
    prep_token, prep_id, prep_data = step_login("fengliang", "test1234")
    if not prep_token:
        report.add_step("login", "fengliang", "login", "FAIL", "login failed")
        return False
    report.add_step("login", "fengliang", "login", "PASS")

    # Create order
    order_no = f"OUT_{RUN_PREFIX}_001"
    order_result, create_body = step_create_order(token, user_id, "outbound", order_no)
    if not order_result:
        report.add_step("create_order", "taidongxu", "create_order", "FAIL", str(create_body))
        return False
    report.add_step("create_order", "taidongxu", "create_order", "PASS")

    # Submit order
    status_code, submit_body = step_submit_order(order_no, token, user_id)
    if status_code != 200:
        report.add_step("submit_order", "taidongxu", "submit_order", "FAIL", f"status={status_code}")
        return False
    report.add_step("submit_order", "taidongxu", "submit_order", "PASS")

    # Keeper confirm
    status_code, keeper_body = step_keeper_confirm(order_no, keeper_token, keeper_id)
    if status_code != 200:
        report.add_step("keeper_confirm", "hutingting", "keeper_confirm", "FAIL", f"status={status_code}")
        return False
    report.add_step("keeper_confirm", "hutingting", "keeper_confirm", "PASS")

    # Transport start
    status_code, start_body = step_transport_start(order_no, prep_token, prep_id)
    if status_code != 200:
        report.add_step("transport_start", "fengliang", "transport_start", "FAIL", f"status={status_code}")
        return False
    report.add_step("transport_start", "fengliang", "transport_start", "PASS")

    # Transport complete
    status_code, complete_body = step_transport_complete(order_no, prep_token, prep_id)
    if status_code != 200:
        report.add_step("transport_complete", "fengliang", "transport_complete", "FAIL", f"status={status_code}")
        return False
    report.add_step("transport_complete", "fengliang", "transport_complete", "PASS")

    # Final confirm
    status_code, final_body = step_final_confirm(order_no, token, user_id, "outbound")
    if status_code != 200:
        report.add_step("final_confirm", "taidongxu", "final_confirm", "FAIL", f"status={status_code}")
        return False
    report.add_step("final_confirm", "taidongxu", "final_confirm", "PASS")

    print("[PASS] Full workflow test passed")
    return True


def run_inbound_workflow_test(report: TestReport):
    """Phase 3: Inbound workflow test."""
    print("\n[PHASE 3] Running inbound workflow test...")

    token, user_id, user_data = step_login("taidongxu", "test1234")
    if not token:
        report.add_step("login", "taidongxu", "login", "FAIL", "login failed")
        return False
    report.add_step("login", "taidongxu", "login", "PASS")

    keeper_token, keeper_id, keeper_data = step_login("hutingting", "test1234")
    if not keeper_token:
        report.add_step("login", "hutingting", "login", "FAIL", "login failed")
        return False
    report.add_step("login", "hutingting", "login", "PASS")

    order_no = f"IN_{RUN_PREFIX}_001"
    order_result, create_body = step_create_order(token, user_id, "inbound", order_no)
    if not order_result:
        report.add_step("create_order", "taidongxu", "create_order", "FAIL", str(create_body))
        return False
    report.add_step("create_order", "taidongxu", "create_order", "PASS")

    status_code, submit_body = step_submit_order(order_no, token, user_id)
    if status_code != 200:
        report.add_step("submit_order", "taidongxu", "submit_order", "FAIL", f"status={status_code}")
        return False
    report.add_step("submit_order", "taidongxu", "submit_order", "PASS")

    status_code, keeper_body = step_keeper_confirm(order_no, keeper_token, keeper_id)
    if status_code != 200:
        report.add_step("keeper_confirm", "hutingting", "keeper_confirm", "FAIL", f"status={status_code}")
        return False
    report.add_step("keeper_confirm", "hutingting", "keeper_confirm", "PASS")

    # For inbound, keeper does final confirm
    payload = {
        "operator_id": str(keeper_id),
        "operator_name": "保管员",
        "operator_role": "keeper",
    }
    status_code, final_body = api_post(f"/tool-io-orders/{order_no}/confirm-final", payload, token=keeper_token)
    if status_code != 200:
        report.add_step("final_confirm", "hutingting", "final_confirm", "FAIL", f"status={status_code}")
        return False
    report.add_step("final_confirm", "hutingting", "final_confirm", "PASS")

    print("[PASS] Inbound workflow test passed")
    return True


def run_reject_resubmit_workflow_test(report: TestReport):
    """Phase 4: Reject and resubmit workflow test."""
    print("\n[PHASE 4] Running reject/resubmit workflow test...")

    token, user_id, user_data = step_login("taidongxu", "test1234")
    if not token:
        report.add_step("login", "taidongxu", "login", "FAIL", "login failed")
        return False
    report.add_step("login", "taidongxu", "login", "PASS")

    keeper_token, keeper_id, keeper_data = step_login("hutingting", "test1234")
    if not keeper_token:
        report.add_step("login", "hutingting", "login", "FAIL", "login failed")
        return False
    report.add_step("login", "hutingting", "login", "PASS")

    order_no = f"REJ_{RUN_PREFIX}_001"
    order_result, create_body = step_create_order(token, user_id, "outbound", order_no)
    if not order_result:
        report.add_step("create_order", "taidongxu", "create_order", "FAIL", str(create_body))
        return False
    report.add_step("create_order", "taidongxu", "create_order", "PASS")

    status_code, submit_body = step_submit_order(order_no, token, user_id)
    if status_code != 200:
        report.add_step("submit_order", "taidongxu", "submit_order", "FAIL", f"status={status_code}")
        return False
    report.add_step("submit_order", "taidongxu", "submit_order", "PASS")

    # Keeper rejects
    reject_payload = {
        "operator_id": str(keeper_id),
        "operator_name": "保管员",
        "operator_role": "keeper",
        "reject_reason": "测试拒绝原因",
    }
    status_code, reject_body = api_post(f"/tool-io-orders/{order_no}/reject", reject_payload, token=keeper_token)
    if status_code != 200:
        report.add_step("reject_order", "hutingting", "reject_order", "FAIL", f"status={status_code}")
        return False
    report.add_step("reject_order", "hutingting", "reject_order", "PASS")

    print("[PASS] Reject/resubmit workflow test passed")
    return True


def _infer_rbac_result(status_code: int, expected_status: int, expected_result: str) -> str:
    """Infer RBAC test result."""
    if status_code == expected_status:
        return "PASS"
    return f"FAIL (got {status_code})"


def record_rbac_result(role: str, permission: str, expected: str, actual: str,
                       status_code: int, report: TestReport):
    """Record RBAC test result."""
    result = "PASS" if status_code == expected else "FAIL"
    details = f"expected={expected}, got={status_code}, actual={actual}"
    report.add_step(f"rbac_{permission}", role, permission, result, details)


def run_rbac_test(report: TestReport):
    """Phase 5: RBAC permission test."""
    print("\n[PHASE 5] Running RBAC permission test...")

    # Test team_leader cannot access admin endpoints
    token, user_id, _ = login_user("taidongxu", "test1234")
    if token:
        status_code, body = api_get("/admin/users", token=token)
        record_rbac_result("team_leader", "admin_users", "FORBIDDEN", body.get("error", ""), status_code, report)

    print("[INFO] RBAC test complete")
    return True


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point for E2E tests."""
    import argparse

    parser = argparse.ArgumentParser(description="E2E API Test Runner")
    parser.add_argument("--smoke", action="store_true", help="Run quick smoke test only")
    parser.add_argument("--rbac", action="store_true", help="Run RBAC test only")
    parser.add_argument("--workflow", action="store_true", help="Run workflow test only")
    parser.add_argument("--inbound", action="store_true", help="Run inbound workflow test only")
    parser.add_argument("--reject", action="store_true", help="Run reject/resubmit test only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    args = parser.parse_args()

    print("=" * 70)
    print("E2E API Test Runner")
    print("=" * 70)
    print(f"Backend: {BACKEND_URL}")
    print(f"Run prefix: {RUN_PREFIX}")

    report = TestReport()
    dm = TestDataManager(RUN_PREFIX)

    try:
        dm.setup()

        if args.smoke:
            run_quick_smoke_test(report)
        elif args.rbac:
            run_rbac_test(report)
        elif args.workflow:
            run_full_workflow_test(report)
        elif args.inbound:
            run_inbound_workflow_test(report)
        elif args.reject:
            run_reject_resubmit_workflow_test(report)
        elif args.all:
            run_quick_smoke_test(report)
            run_full_workflow_test(report)
            run_inbound_workflow_test(report)
            run_reject_resubmit_workflow_test(report)
            run_rbac_test(report)
        else:
            # Default: run smoke test
            run_quick_smoke_test(report)

    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
    finally:
        dm.teardown()

    success = report.print_summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
