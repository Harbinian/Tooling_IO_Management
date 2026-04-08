# -*- coding: utf-8 -*-
"""
E2E Test Base Module - Shared utilities, config, and test infrastructure.
"""

import sys
import os
import json
import time
import uuid
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from test_runner.commands import start, advance, status, stop


# =============================================================================
# Configuration
# =============================================================================

BACKEND_URL = "http://localhost:8151"
API_BASE = f"{BACKEND_URL}/api"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

TEST_USERS = {
    "taidongxu": {
        "password": "test1234",
        "role": "TEAM_LEADER",
        "role_name": "班组长",
        "user_id": None,
        "token": None
    },
    "hutingting": {
        "password": "test1234",
        "role": "KEEPER",
        "role_name": "保管员",
        "user_id": None,
        "token": None
    },
    "fengliang": {
        "password": "test1234",
        "role": "PRODUCTION_PREP",
        "role_name": "生产准备工",
        "user_id": None,
        "token": None
    },
    "admin": {
        "password": "admin123",
        "role": "SYS_ADMIN",
        "role_name": "系统管理员",
        "user_id": None,
        "token": None
    }
}

# =============================================================================
# Test Data Isolation - Run-level unique prefix
# =============================================================================

def generate_run_prefix():
    """Generate unique test data prefix to avoid conflicts across runs."""
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%m%d%H%M")
    return f"AUTO_{timestamp}_{run_id}"


RUN_PREFIX = generate_run_prefix()
TEST_ORDER_PREFIX = "AUTO_"
STALE_ORDER_MAX_AGE = timedelta(hours=24)
ORDER_LIST_PAGE_SIZE = 200
KNOWN_TEST_PROJECT_PREFIXES = ("TEST", "WF_TEST")
TERMINAL_CLEANUP_STATUSES = {"completed", "rejected", "cancelled"}
LOCKED_CLEANUP_STATUSES = {
    "submitted",
    "keeper_confirmed",
    "partially_confirmed",
    "transport_notified",
    "transport_in_progress",
    "transport_completed",
    "final_confirmation_pending",
}

# Global test data manager instance (initialized by main())
_test_data_manager = None


# =============================================================================
# Test Data Manager - setup/teardown mechanism
# =============================================================================

class TestDataManager:
    """
    Manage test data creation and cleanup, ensuring data isolation per run.

    Usage:
        dm = TestDataManager(RUN_PREFIX)
        try:
            dm.setup()
            # run tests...
        finally:
            dm.teardown()
    """

    def __init__(self, run_prefix: str):
        self.run_prefix = run_prefix
        self.created_orders = []
        self.created_tools = []
        self._setup_complete = False

    def setup(self):
        """Setup: cleanup old data with same prefix."""
        if self._setup_complete:
            return

        print(f"\n[TEST DATA MANAGER] Setting up test data with prefix: {self.run_prefix}")

        self.cleanup_stale_orders()
        self.cleanup_old_data(self.run_prefix)

        self._setup_complete = True
        print(f"[TEST DATA MANAGER] Setup complete")

    def teardown(self):
        """Teardown: delete test data created during this run."""
        print(f"\n[TEST DATA MANAGER] Tearing down test data...")

        cleanup_count = 0

        for order_no in self.created_orders:
            try:
                self._delete_order(order_no)
                cleanup_count += 1
            except Exception as e:
                print(f"   [WARN] Failed to cleanup order {order_no}: {e}")

        for tool_code in self.created_tools:
            try:
                self._delete_test_tool(tool_code)
                cleanup_count += 1
            except Exception as e:
                print(f"   [WARN] Failed to cleanup tool {tool_code}: {e}")

        print(f"[TEST DATA MANAGER] Teardown complete, cleaned {cleanup_count} items")
        self._setup_complete = False

    def cleanup_old_data(self, prefix: str):
        """Clean up orphaned historical AUTO test orders."""
        del prefix
        self._cleanup_orders("orphaned AUTO test orders", _should_cleanup_order)

    def cleanup_stale_orders(self):
        """Clean up stale historical orders that can still lock tools."""
        self._cleanup_orders("stale locked orders", _should_cleanup_order)

    def _cleanup_orders(self, label: str, predicate):
        token_admin, user_id_admin, _ = login_user("admin", "admin123")
        if not token_admin:
            print(f"   [WARN] Skip cleanup for {label}: admin login failed")
            return

        deleted_count = 0
        inspected_count = 0

        for order in _list_orders_for_cleanup(token_admin):
            inspected_count += 1
            should_delete, reason = predicate(order, token_admin)
            if not should_delete:
                continue

            order_no = str(order.get("order_no") or "").strip()
            status_code, body = api_delete(
                f"/tool-io-orders/{order_no}",
                {
                    "operator_id": user_id_admin,
                    "operator_name": "管理员",
                    "operator_role": "sys_admin",
                },
                token=token_admin,
            )
            if status_code == 200 and body.get("success"):
                deleted_count += 1
                print(f"   [CLEANUP] Deleted stale order: {order_no} ({reason})")
            else:
                print(
                    f"   [WARN] Failed to delete stale order {order_no}: "
                    f"status={status_code}, error={body.get('error')}"
                )

        print(
            f"   [INFO] Cleanup scan complete for {label}: "
            f"inspected={inspected_count}, deleted={deleted_count}"
        )

    def _delete_order(self, order_no: str):
        """Delete specified test order."""
        try:
            token_admin, user_id_admin, _ = login_user("admin", "admin123")
            if token_admin:
                status_code, body = api_delete(f"/tool-io-orders/{order_no}", {
                    "operator_id": user_id_admin,
                    "operator_name": "管理员",
                    "operator_role": "admin"
                }, token=token_admin)
                if status_code == 200:
                    print(f"   [CLEANUP] Deleted order: {order_no}")
                else:
                    print(f"   [CLEANUP] Order {order_no} delete returned {status_code}")
        except Exception as e:
            print(f"   [CLEANUP] Failed to delete order {order_no}: {e}")

    def _delete_test_tool(self, tool_code: str):
        """Delete test tool (usually managed externally)."""
        print(f"   [CLEANUP] Tool cleanup not implemented for: {tool_code}")

    def add_order(self, order_no: str):
        """Track created order for teardown cleanup."""
        if order_no:
            self.created_orders.append(order_no)
            print(f"   [TRACK] Order tracked for cleanup: {order_no}")

    def remove_order(self, order_no: str):
        """Remove order from teardown tracking after successful explicit cleanup."""
        if order_no in self.created_orders:
            self.created_orders = [tracked for tracked in self.created_orders if tracked != order_no]

    def add_tool(self, tool_code: str):
        """Track created tool for teardown cleanup."""
        if tool_code:
            self.created_tools.append(tool_code)
            print(f"   [TRACK] Tool tracked for cleanup: {tool_code}")

    def generate_order_no(self, order_type: str = "IO"):
        """Generate order number with unique prefix."""
        seq = len(self.created_orders) + 1
        return f"{order_type}_{self.run_prefix}_{seq:03d}"


# =============================================================================
# Helper Functions
# =============================================================================

def _parse_order_datetime(raw_value):
    """Parse API order datetime field into datetime."""
    if not raw_value:
        return None
    text = str(raw_value).strip()
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(text, fmt)
                break
            except ValueError:
                parsed = None
        if parsed is None:
            return None
    if parsed.tzinfo is not None:
        return parsed.astimezone().replace(tzinfo=None)
    return parsed


def _get_order_age(order):
    """Return order age based on created_at."""
    created_at = _parse_order_datetime(order.get("created_at"))
    if created_at is None:
        return None
    return datetime.now() - created_at


def _normalize_order_status(order):
    return str(order.get("order_status") or "").strip().lower()


def _normalize_project_code(order):
    return str(order.get("project_code") or "").strip().upper()


def _is_auto_test_order(order):
    order_no = str(order.get("order_no") or "").strip().upper()
    return TEST_ORDER_PREFIX in order_no


def _is_known_test_project(order):
    project_code = _normalize_project_code(order)
    return any(project_code.startswith(prefix) for prefix in KNOWN_TEST_PROJECT_PREFIXES)


def _fetch_order_detail_for_cleanup(order_no: str, token: str):
    status_code, body = api_get(f"/tool-io-orders/{order_no}", token=token)
    if status_code != 200 or not body.get("success"):
        return None
    return body.get("data") or {}


def _order_uses_test_fixture(order_detail):
    if not _is_known_test_project(order_detail):
        return False
    for item in order_detail.get("items") or []:
        serial_no = str(item.get("serial_no") or "").strip().upper()
        drawing_no = str(item.get("drawing_no") or "").strip().upper()
        if serial_no == TEST_TOOL["serial_no"].upper():
            return True
        if drawing_no == TEST_TOOL["drawing_no"].upper():
            return True
    return False


def _should_cleanup_order(order, token: str = None):
    """Decide whether an order should be cleaned before E2E execution."""
    order_no = str(order.get("order_no") or "").strip()
    if not order_no:
        return False, ""

    status = _normalize_order_status(order)
    if token and _is_known_test_project(order):
        order_detail = _fetch_order_detail_for_cleanup(order_no, token)
        if order_detail and _order_uses_test_fixture(order_detail):
            return True, f"test_fixture_order status={status or 'unknown'}"

    age = _get_order_age(order)
    if age is None or age < STALE_ORDER_MAX_AGE:
        return False, ""

    if _is_auto_test_order(order):
        return True, f"auto_test_order age={age}"
    if status in TERMINAL_CLEANUP_STATUSES:
        return True, f"terminal_status={status} age={age}"
    if status in LOCKED_CLEANUP_STATUSES:
        return True, f"locked_status={status} age={age}"
    return False, ""


def _list_orders_for_cleanup(token: str):
    """Yield paginated orders visible to admin for cleanup inspection."""
    page_no = 1
    while True:
        status_code, body = api_get(
            "/tool-io-orders",
            {"page_no": page_no, "page_size": ORDER_LIST_PAGE_SIZE},
            token=token,
        )
        if status_code != 200 or not body.get("success"):
            print(
                f"   [WARN] Failed to list orders for cleanup: "
                f"status={status_code}, error={body.get('error')}"
            )
            return

        rows = body.get("data") or []
        for row in rows:
            yield row

        if len(rows) < ORDER_LIST_PAGE_SIZE:
            return
        page_no += 1


# =============================================================================
# Test Data
# =============================================================================

TEST_TOOL = {
    "serial_no": "T000001",
    "drawing_no": "Tooling_IO_TEST",
    "tool_name": "测试用工装",
    "spec_model": "标准规格"
}


# =============================================================================
# Report
# =============================================================================

class TestReport:
    def __init__(self):
        self.results = []
        self.anomalies = []
        self.start_time = datetime.now()

    def add_step(self, step_name: str, user: str, action: str, result: str,
                 details: str = "", anomaly: str = None, http_status: int = None):
        self.results.append({
            "step_name": step_name,
            "user": user,
            "action": action,
            "result": result,
            "details": details,
            "anomaly": anomaly,
            "http_status": http_status,
            "timestamp": datetime.now().isoformat()
        })
        if anomaly:
            self.anomalies.append({
                "step_name": step_name,
                "anomaly": anomaly,
                "timestamp": datetime.now().isoformat()
            })

    def print_summary(self):
        duration = datetime.now() - self.start_time
        print("\n" + "=" * 70)
        print("[TEST REPORT] E2E API Test Report")
        print("=" * 70)
        print(f"Duration: {duration}")
        print(f"Total Steps: {len(self.results)}")
        print(f"Anomalies: {len(self.anomalies)}")

        print("\n--- Step Details ---")
        for r in self.results:
            status_icon = "[PASS]" if r["result"] == "PASS" else "[FAIL]" if r["result"] == "FAIL" else "[SKIP]"
            anomaly_icon = " [ANOMALY]" if r["anomaly"] else ""
            status_str = f"HTTP {r['http_status']}" if r["http_status"] else ""
            print(f"{status_icon} [{r['user']}] {r['step_name']}: {r['action']} -> {r['result']} {status_str}{anomaly_icon}")
            if r["details"]:
                print(f"   Details: {r['details'][:200]}")

        if self.anomalies:
            print("\n--- Anomalies ---")
            for a in self.anomalies:
                print(f"[ANOMALY] {a['step_name']}: {a['anomaly']}")

        print("\n" + "=" * 70)
        passed = sum(1 for r in self.results if r["result"] == "PASS")
        failed = sum(1 for r in self.results if r["result"] == "FAIL")
        print(f"Passed: {passed}, Failed: {failed}, Total: {len(self.results)}")
        print("=" * 70)
        return len(self.anomalies) == 0 and failed == 0


# =============================================================================
# API Helper Functions
# =============================================================================

def api_post(endpoint: str, data: dict = None, token: str = None, user: str = None) -> tuple:
    """Send POST request."""
    url = f"{API_BASE}{endpoint}"
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        return resp.status_code, resp.json() if resp.content else {}
    except Exception as e:
        return 0, {"error": str(e)}


def api_put(endpoint: str, data: dict = None, token: str = None) -> tuple:
    """Send PUT request."""
    url = f"{API_BASE}{endpoint}"
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.put(url, json=data, headers=headers, timeout=30)
        return resp.status_code, resp.json() if resp.content else {}
    except Exception as e:
        return 0, {"error": str(e)}


def api_get(endpoint: str, params: dict = None, token: str = None) -> tuple:
    """Send GET request."""
    url = f"{API_BASE}{endpoint}"
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        return resp.status_code, resp.json() if resp.content else {}
    except Exception as e:
        return 0, {"error": str(e)}


def api_delete(endpoint: str, data: dict = None, token: str = None) -> tuple:
    """Send DELETE request."""
    url = f"{API_BASE}{endpoint}"
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.delete(url, json=data, headers=headers, timeout=30)
        return resp.status_code, resp.json() if resp.content else {}
    except Exception as e:
        return 0, {"error": str(e)}


def login_user(username: str, password: str) -> tuple:
    """Login and return token."""
    status_code, body = api_post("/auth/login", {
        "login_name": username,
        "password": password
    })

    if status_code == 200 and body.get("success"):
        token = body.get("token", "")
        user_data = body.get("user", {})
        return token, user_data.get("user_id"), user_data
    return None, None, None


def ensure_user_session(username: str) -> tuple:
    """Ensure a test user has a fresh token and cached user_id."""
    user = TEST_USERS[username]
    token, user_id, user_data = login_user(username, user["password"])
    if token:
        user["token"] = token
        user["user_id"] = user_id
    return token, user_id, user_data


# =============================================================================
# Step Execution Framework - Error Handling
# =============================================================================

def is_critical_error(e: Exception) -> bool:
    """
    Determine if error is critical (causes immediate test stop).

    Critical errors include: API 500, database connection, permission denied.
    """
    error_msg = str(e).lower()
    critical_indicators = [
        "500",
        "internal server error",
        "connection refused",
        "database",
        "permission denied",
        "access denied",
        "unauthorized",
    ]
    return any(indicator in error_msg for indicator in critical_indicators)


def is_recoverable_error(e: Exception) -> bool:
    """
    Determine if error is recoverable (can continue to next step).

    Recoverable errors include: validation, timeout, network, 400 errors.
    """
    error_msg = str(e).lower()
    recoverable_indicators = [
        "timeout",
        "connection timeout",
        "network",
        "400",
        "bad request",
        "validation",
        "not found",
        "404",
    ]
    return any(indicator in error_msg for indicator in recoverable_indicators)


def execute_step(step_name: str, before_action: callable, action: callable,
                 after_action: callable, expected_next_state: str = None):
    """
    Unified step execution framework: before -> action -> after -> advance.

    Exception handling: even if action fails, after_action and advance/stop
    are still executed to ensure complete state on failure.
    """
    try:
        result = action()
        status_code, body = result if isinstance(result, tuple) else (result, None)
        return result
    except Exception as e:
        raise
