# -*- coding: utf-8 -*-
"""
Human E2E Tester - API 自动化测试

通过直接调用后端 API 执行完整的拟人 E2E 测试，覆盖：
1. 快速冒烟测试 (quick_smoke)
2. 完整出库工作流 (full_workflow)
3. RBAC 权限测试 (rbac)

使用方法：
    python test_runner/api_e2e.py
"""

import sys
import os
import json
import time
import uuid
import requests
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from test_runner.commands import start, advance, status, stop

# P1-2: 集成感知层
SENSING_PACKAGE_ROOT = REPO_ROOT / ".skills" / "human-e2e-tester"
if str(SENSING_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(SENSING_PACKAGE_ROOT))

# 统一数据库路径
E2E_SENSING_DB = REPO_ROOT / "test_reports" / "e2e_sensing.db"

# API E2E 测试不使用感知系统，因为没有浏览器页面可以观察
# SensingOrchestrator 依赖 Playwright/Selenium driver 来获取页面状态
# API 测试只有 HTTP 响应，没有页面状态可言
SENSING_AVAILABLE = False
print("[INFO] API E2E mode: sensing disabled (no browser available)")


# =============================================================================
# 配置
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
# 测试数据隔离 - Run级唯一前缀
# =============================================================================

def generate_run_prefix():
    """生成唯一的测试数据前缀，避免多次运行的测试数据冲突"""
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%m%d%H%M")
    return f"AUTO_{timestamp}_{run_id}"


RUN_PREFIX = generate_run_prefix()

# 全局测试数据管理器实例（由 main() 初始化）
_test_data_manager = None


# =============================================================================
# 测试数据管理器 - setup/teardown 机制
# =============================================================================

class TestDataManager:
    """
    管理测试数据的创建和清理，确保每次测试运行的数据隔离

    使用方法:
        dm = TestDataManager(RUN_PREFIX)
        try:
            dm.setup()
            # 执行测试...
        finally:
            dm.teardown()
    """

    def __init__(self, run_prefix: str):
        self.run_prefix = run_prefix
        self.created_orders = []
        self.created_tools = []
        self._setup_complete = False

    def setup(self):
        """测试前准备：清理旧数据（同一前缀但已过期的）"""
        if self._setup_complete:
            return

        print(f"\n[TEST DATA MANAGER] Setting up test data with prefix: {self.run_prefix}")

        # 清理上次的残留数据（同一前缀）
        self.cleanup_old_data(self.run_prefix)

        self._setup_complete = True
        print(f"[TEST DATA MANAGER] Setup complete")

    def teardown(self):
        """测试后清理：删除本次创建的测试数据"""
        print(f"\n[TEST DATA MANAGER] Tearing down test data...")

        cleanup_count = 0

        # 删除本次创建的测试订单
        for order_no in self.created_orders:
            try:
                self._delete_order(order_no)
                cleanup_count += 1
            except Exception as e:
                print(f"   [WARN] Failed to cleanup order {order_no}: {e}")

        # 删除本次创建的测试工装（如果支持）
        for tool_code in self.created_tools:
            try:
                self._delete_test_tool(tool_code)
                cleanup_count += 1
            except Exception as e:
                print(f"   [WARN] Failed to cleanup tool {tool_code}: {e}")

        print(f"[TEST DATA MANAGER] Teardown complete, cleaned {cleanup_count} items")
        self._setup_complete = False

    def cleanup_old_data(self, prefix: str):
        """
        清理旧数据（同一前缀但已过期的）
        注意：由于订单号包含时间戳，旧数据自动失效
        """
        print(f"   [INFO] Old data cleanup for prefix '{prefix}' skipped (timestamp-based auto-expiry)")

    def _delete_order(self, order_no: str):
        """删除指定的测试订单"""
        try:
            # 尝试使用 admin token 删除
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
        """删除测试工装（如果测试创建了工装）"""
        # 工装通常由外部系统管理，这里仅做日志记录
        print(f"   [CLEANUP] Tool cleanup not implemented for: {tool_code}")

    def add_order(self, order_no: str):
        """记录创建的订单，用于 teardown 时清理"""
        if order_no:
            self.created_orders.append(order_no)
            print(f"   [TRACK] Order tracked for cleanup: {order_no}")

    def add_tool(self, tool_code: str):
        """记录创建的工装，用于 teardown 时清理"""
        if tool_code:
            self.created_tools.append(tool_code)
            print(f"   [TRACK] Tool tracked for cleanup: {tool_code}")

    def generate_order_no(self, order_type: str = "IO"):
        """生成使用唯一前缀的订单号"""
        seq = len(self.created_orders) + 1
        return f"{order_type}_{self.run_prefix}_{seq:03d}"


# =============================================================================
# 测试数据
# =============================================================================

TEST_TOOL = {
    "serial_no": "T000001",
    "drawing_no": "Tooling_IO_TEST",
    "tool_name": "测试用工装"
}


# =============================================================================
# 报告
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
# API 辅助函数
# =============================================================================

def api_post(endpoint: str, data: dict = None, token: str = None, user: str = None) -> tuple:
    """发送 POST 请求"""
    url = f"{API_BASE}{endpoint}"
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        return resp.status_code, resp.json() if resp.content else {}
    except Exception as e:
        return 0, {"error": str(e)}


def api_get(endpoint: str, params: dict = None, token: str = None) -> tuple:
    """发送 GET 请求"""
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
    """发送 DELETE 请求"""
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
    """登录并返回 token"""
    status_code, body = api_post("/auth/login", {
        "login_name": username,
        "password": password
    })

    if status_code == 200 and body.get("success"):
        token = body.get("token", "")
        user_data = body.get("user", {})
        return token, user_data.get("user_id"), user_data
    return None, None, None


# =============================================================================
# 步骤执行框架 - 异常处理
# =============================================================================

def is_critical_error(e: Exception) -> bool:
    """
    判断是否为关键错误（会导致测试立即停止）

    关键错误包括：
    - API 500 错误
    - 数据库连接错误
    - 权限拒绝错误
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
    判断是否为可恢复错误（可以继续执行下一步）

    可恢复错误包括：
    - 验证错误
    - 超时错误
    - 网络错误
    - 400 客户端错误
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
                 after_action: callable, expected_next_state: str = None,
                 orchestrator=None):
    """
    统一步骤执行框架: before -> action -> after -> advance

    异常处理：即使 action 失败，仍会执行 snapshot_after 和 advance/stop，
    确保失败 run 也有完整状态与感知数据。

    Args:
        step_name: 步骤名称
        before_action: 执行前的准备操作（如快照）
        action: 主要操作，返回 (status_code, body)
        after_action: 执行后的验证操作
        expected_next_state: 期望的下一步状态
        orchestrator: 感知协调器（可选）
    """
    # before
    if orchestrator:
        orchestrator.snapshot_before(None)

    try:
        # action
        result = action()
        status_code, body = result if isinstance(result, tuple) else (result, None)

        # after
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation=step_name,
                api_response={"status_code": status_code, "body": body},
                expected_next_status=expected_next_state
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, step_name, anomalies, critical)

        return result  # Return the original result tuple, not (status_code, body)

    except Exception as e:
        # 即使失败，也要执行 snapshot_after
        if orchestrator:
            try:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    None,
                    operation=step_name,
                    api_response={"status_code": 0, "body": {"error": str(e)}},
                    expected_next_status=expected_next_state
                )
            except Exception:
                # snapshot_after 本身也可能失败，忽略
                anomalies = []
                checks = []

            # 记录异常
            anomalies_count = 1
            critical_count = 1 if is_critical_error(e) else 0

            # 仍要 advance 或 stop
            if is_recoverable_error(e):
                _sensing_advance(orchestrator, step_name, anomalies, critical_count)
            else:
                _sensing_advance(orchestrator, step_name, anomalies, critical_count)
                try:
                    stop(f"step_failed: {step_name}, error: {str(e)}")
                except Exception:
                    pass

        # 重新抛出异常
        raise


# =============================================================================
# PHASE 1: 快速冒烟测试
# =============================================================================

def run_quick_smoke_test(report: TestReport, orchestrator=None):
    """快速冒烟测试 - 验证基本功能"""
    print("\n" + "=" * 50)
    print("[PHASE 1] Quick Smoke Test")
    print("=" * 50)

    # 1. 测试登录 API
    print("\n[1/4] Testing login API...")
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.snapshot_before(None)

    token, user_id, user_data = login_user("taidongxu", "test123")

    if orchestrator:
        snap, anomalies, checks = orchestrator.snapshot_after(
            None,
            operation="smoke_login",
            api_response={"status_code": 200 if token else 401, "body": user_data},
            expected_next_status="logged_in"
        )
        critical = sum(1 for a in anomalies if a.severity == "critical")
        try:
            advance("smoke_login", len(anomalies), critical)
        except Exception:
            pass

    if token:
        report.add_step("smoke_01", "taidongxu", "登录", "PASS",
                       details=f"user_id={user_id}, roles={user_data.get('roles')}", http_status=200)
        TEST_USERS["taidongxu"]["token"] = token
        TEST_USERS["taidongxu"]["user_id"] = user_id
    else:
        report.add_step("smoke_01", "taidongxu", "登录", "FAIL", "Login failed", http_status=401)
        print("   [WARN] Login failed, stopping smoke test")
        return

    # 2. 测试获取订单列表
    print("[2/4] Testing order list API...")
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_get("/tool-io-orders", token=token)

    if orchestrator:
        snap, anomalies, checks = orchestrator.snapshot_after(
            None,
            operation="smoke_list_orders",
            api_response={"status_code": status_code, "body": body},
            expected_next_status="orders_viewed"
        )
        critical = sum(1 for a in anomalies if a.severity == "critical")
        try:
            advance("smoke_list_orders", len(anomalies), critical)
        except Exception:
            pass

    if status_code == 200:
        report.add_step("smoke_02", "taidongxu", "获取订单列表", "PASS",
                       details=f"success={body.get('success')}, total={len(body.get('data', []))}", http_status=status_code)
    else:
        report.add_step("smoke_02", "taidongxu", "获取订单列表", "FAIL",
                       details=f"status={status_code}", http_status=status_code)

    # 3. 测试创建订单
    print("[3/4] Testing order creation API...")
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_post("/tool-io-orders", {
        "order_type": "outbound",
        "initiator_id": user_id,
        "initiator_name": "太东旭",
        "initiator_role": "team_leader",
        "department": "生产部",
        "project_code": "TEST001",
        "usage_purpose": "生产使用",
        "planned_use_time": "2026-04-01",
        "target_location_text": "测试位置",
        "items": [{
            "tool_code": TEST_TOOL["serial_no"],
            "tool_name": TEST_TOOL["tool_name"],
            "drawing_no": TEST_TOOL["drawing_no"],
            "spec_model": "测试规格"
        }]
    }, token=token)

    order_no = None
    # 注意：创建成功返回 201 Created
    if status_code in [200, 201] and body.get("success"):
        order_no = body.get("order_no")
        # 追踪订单以便 teardown 时清理
        global _test_data_manager
        if _test_data_manager:
            _test_data_manager.add_order(order_no)
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="smoke_create_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="draft"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            try:
                advance("smoke_create_order", len(anomalies), critical)
            except Exception:
                pass
        report.add_step("smoke_03", "taidongxu", "创建订单", "PASS",
                       details=f"order_no={order_no}", http_status=status_code)
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="smoke_create_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="draft"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            try:
                advance("smoke_create_order", len(anomalies), critical)
            except Exception:
                pass
        report.add_step("smoke_03", "taidongxu", "创建订单", "FAIL",
                       details=f"status={status_code}, error={body.get('error')}", http_status=status_code)

    # 4. 清理测试订单 (team_leader 不能删除订单，需要用 admin)
    if order_no:
        print(f"[4/4] Cleaning up test order {order_no}...")
        admin_token, _, _ = login_user("admin", "admin123")
        if orchestrator:
            orchestrator.set_user_context("admin", "SYS_ADMIN", "ORG001")
            orchestrator.snapshot_before(None)
        status_code, body = api_delete(f"/tool-io-orders/{order_no}", {
            "operator_id": "U_ADMIN",
            "operator_name": "管理员",
            "operator_role": "admin"
        }, token=admin_token)
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="smoke_delete_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="deleted"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            try:
                advance("smoke_delete_order", len(anomalies), critical)
            except Exception:
                pass
        if status_code == 200:
            report.add_step("smoke_04", "admin", "删除测试订单", "PASS",
                           details=f"order_no={order_no}", http_status=status_code)
        else:
            report.add_step("smoke_04", "admin", "删除测试订单", "FAIL",
                           details=f"status={status_code}", http_status=status_code)
    else:
        report.add_step("smoke_04", "taidongxu", "删除测试订单", "SKIP", "No order to delete")

    print("[DONE] Smoke test completed")


# =============================================================================
# PHASE 2: 完整出库工作流测试
# =============================================================================

def _sensing_advance(orchestrator, operation, anomalies, critical_count):
    """Helper to call advance with error handling"""
    try:
        advance(operation, len(anomalies), critical_count)
    except Exception:
        pass


# =============================================================================
# 关键步骤封装 (使用 execute_step 框架)
# =============================================================================

def step_login(username: str, password: str, orchestrator=None) -> tuple:
    """
    步骤: login - 用户登录

    Returns:
        (token, user_id, user_data)
    """
    def action():
        return login_user(username, password)

    status_code, result = execute_step(
        step_name=f"wf_login_{username}",
        before_action=None,
        action=action,
        after_action=None,
        expected_next_state="logged_in",
        orchestrator=orchestrator
    )

    # login_user returns (token, user_id, user_data)
    if result and len(result) == 3:
        return result
    return None, None, None


def step_create_order(token: str, user_id: int, order_type: str, order_no: str = None,
                      orchestrator=None) -> tuple:
    """
    步骤: create_order - 创建订单

    Returns:
        (status_code, body, order_no)
    """
    def action():
        return api_post("/tool-io-orders", {
            "order_type": order_type,
            "initiator_id": user_id,
            "initiator_name": "太东旭",
            "initiator_role": "team_leader",
            "department": "生产部",
            "project_code": "WF_TEST_001",
            "usage_purpose": "生产使用",
            "planned_use_time": "2026-04-15",
            "target_location_text": "车间A-1",
            "items": [{
                "tool_code": TEST_TOOL["serial_no"],
                "tool_name": TEST_TOOL["tool_name"],
                "drawing_no": TEST_TOOL["drawing_no"],
                "spec_model": "标准规格"
            }]
        }, token=token)

    status_code, body = execute_step(
        step_name="wf_create_order",
        before_action=None,
        action=action,
        after_action=None,
        expected_next_state="draft",
        orchestrator=orchestrator
    )

    result_order_no = body.get("order_no") if body else None
    return status_code, body, result_order_no


def step_submit_order(order_no: str, token: str, user_id: int,
                      orchestrator=None) -> tuple:
    """
    步骤: submit_order - 提交订单

    Returns:
        (status_code, body)
    """
    def action():
        return api_post(f"/tool-io-orders/{order_no}/submit", {
            "operator_id": user_id,
            "operator_name": "太东旭",
            "operator_role": "team_leader"
        }, token=token)

    status_code, body = execute_step(
        step_name="wf_submit_order",
        before_action=None,
        action=action,
        after_action=None,
        expected_next_state="submitted",
        orchestrator=orchestrator
    )

    return status_code, body


def step_keeper_confirm(order_no: str, token: str, user_id: int,
                        transport_assignee_id: str, orchestrator=None,
                        order_items: list = None) -> tuple:
    """
    步骤: keeper_confirm - 保管员确认

    Args:
        order_no: 订单号
        token: 认证令牌
        user_id: 保管员用户ID
        transport_assignee_id: 运输接收人ID
        orchestrator: 感知编排器(可选)
        order_items: 订单明细列表(可选)，如果提供则使用其中的item_id

    Returns:
        (status_code, body)
    """
    def action():
        # If order_items is provided, extract item_id from it
        items_payload = []
        if order_items:
            for item in order_items:
                items_payload.append({
                    "item_id": item.get("id"),  # Use the database item_id
                    "tool_code": item.get("tool_code"),
                    "location_id": item.get("location_id") or 1,
                    "location_text": item.get("location_text") or item.get("keeper_confirm_location_text") or "仓库A-1",
                    "check_result": "approved",
                    "approved_qty": item.get("confirmed_qty") or item.get("apply_qty") or 1,
                    "status": "approved"
                })
        else:
            # Fallback: try to get order detail to extract item_ids
            _, order_detail = api_get(f"/tool-io-orders/{order_no}", token=token)
            if order_detail and order_detail.get("items"):
                for item in order_detail.get("items", []):
                    items_payload.append({
                        "item_id": item.get("id"),
                        "tool_code": item.get("tool_code"),
                        "location_id": item.get("location_id") or 1,
                        "location_text": item.get("location_text") or item.get("keeper_confirm_location_text") or "仓库A-1",
                        "check_result": "approved",
                        "approved_qty": item.get("confirmed_qty") or item.get("apply_qty") or 1,
                        "status": "approved"
                    })
            else:
                # Last resort fallback (should not reach here normally)
                items_payload = [{
                    "tool_code": TEST_TOOL["serial_no"],
                    "location_id": 1,
                    "location_text": "仓库A-1",
                    "check_result": "approved",
                    "approved_qty": 1,
                    "status": "approved"
                }]

        return api_post(f"/tool-io-orders/{order_no}/keeper-confirm", {
            "keeper_id": user_id,
            "keeper_name": "胡婷婷",
            "transport_type": "self",
            "transport_assignee_id": transport_assignee_id,
            "transport_assignee_name": "冯亮",
            "items": items_payload,
            "operator_id": user_id,
            "operator_name": "胡婷婷",
            "operator_role": "keeper"
        }, token=token)

    status_code, body = execute_step(
        step_name="wf_keeper_confirm",
        before_action=None,
        action=action,
        after_action=None,
        expected_next_state="keeper_confirmed",
        orchestrator=orchestrator
    )

    return status_code, body


def step_transport_start(order_no: str, token: str, user_id: int,
                          orchestrator=None) -> tuple:
    """
    步骤: transport_execute (start) - 开始运输

    Returns:
        (status_code, body)
    """
    def action():
        return api_post(f"/tool-io-orders/{order_no}/transport-start", {
            "operator_id": user_id,
            "operator_name": "冯亮",
            "operator_role": "production_prep"
        }, token=token)

    status_code, body = execute_step(
        step_name="wf_transport_start",
        before_action=None,
        action=action,
        after_action=None,
        expected_next_state="transport_in_progress",
        orchestrator=orchestrator
    )

    return status_code, body


def step_transport_complete(order_no: str, token: str, user_id: int,
                             orchestrator=None) -> tuple:
    """
    步骤: transport_execute (complete) - 完成运输

    Returns:
        (status_code, body)
    """
    def action():
        return api_post(f"/tool-io-orders/{order_no}/transport-complete", {
            "operator_id": user_id,
            "operator_name": "冯亮",
            "operator_role": "production_prep"
        }, token=token)

    status_code, body = execute_step(
        step_name="wf_transport_complete",
        before_action=None,
        action=action,
        after_action=None,
        expected_next_state="transport_completed",
        orchestrator=orchestrator
    )

    return status_code, body


def step_final_confirm(order_no: str, token: str, user_id: int,
                        operator_role: str, orchestrator=None) -> tuple:
    """
    步骤: final_confirm - 最终确认

    Returns:
        (status_code, body)
    """
    def action():
        return api_post(f"/tool-io-orders/{order_no}/final-confirm", {
            "operator_id": user_id,
            "operator_name": "太东旭",
            "operator_role": operator_role
        }, token=token)

    status_code, body = execute_step(
        step_name="wf_final_confirm",
        before_action=None,
        action=action,
        after_action=None,
        expected_next_state="completed",
        orchestrator=orchestrator
    )

    return status_code, body


def run_full_workflow_test(report: TestReport, orchestrator=None):
    """完整出库工作流测试"""
    print("\n" + "=" * 50)
    print("[PHASE 2] Full Outbound Workflow Test")
    print("=" * 50)

    # -------------------------------------------------------------------------
    # 步骤 1-4: 太东旭 - 登录并创建订单
    # -------------------------------------------------------------------------
    print("\n--- Phase 2A: Order Creation (taidongxu) ---")

    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.snapshot_before(None)

    token_td, user_id_td, _ = login_user("taidongxu", "test123")

    if orchestrator:
        snap, anomalies, checks = orchestrator.snapshot_after(
            None,
            operation="wf_login_taidongxu",
            api_response={"status_code": 200 if token_td else 401},
            expected_next_status="logged_in"
        )
        critical = sum(1 for a in anomalies if a.severity == "critical")
        _sensing_advance(orchestrator, "wf_login_taidongxu", anomalies, critical)

    if not token_td:
        report.add_step("wf_01", "taidongxu", "登录", "FAIL", "Login failed")
        print("   [ERROR] Login failed, stopping workflow test")
        return

    report.add_step("wf_01", "taidongxu", "登录", "PASS", f"user_id={user_id_td}")
    TEST_USERS["taidongxu"]["token"] = token_td
    TEST_USERS["taidongxu"]["user_id"] = user_id_td

    # 创建出库订单
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_post("/tool-io-orders", {
        "order_type": "outbound",
        "initiator_id": user_id_td,
        "initiator_name": "太东旭",
        "initiator_role": "team_leader",
        "department": "生产部",
        "project_code": "WF_TEST_001",
        "usage_purpose": "生产使用",
        "planned_use_time": "2026-04-15",
        "target_location_text": "车间A-1",
        "items": [{
            "tool_code": TEST_TOOL["serial_no"],
            "tool_name": TEST_TOOL["tool_name"],
            "drawing_no": TEST_TOOL["drawing_no"],
            "spec_model": "标准规格"
        }]
    }, token=token_td)

    order_no = None
    # 注意：创建成功返回 201 Created
    if status_code in [200, 201] and body.get("success"):
        order_no = body.get("order_no")
        # 追踪订单以便 teardown 时清理
        global _test_data_manager
        if _test_data_manager:
            _test_data_manager.add_order(order_no)
        if orchestrator:
            orchestrator.set_order_context(order_no, "draft", "outbound")
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_create_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="draft"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_create_order", anomalies, critical)
        report.add_step("wf_02", "taidongxu", "创建出库订单", "PASS", f"order_no={order_no}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_create_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="draft"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_create_order", anomalies, critical)
        report.add_step("wf_02", "taidongxu", "创建出库订单", "FAIL",
                       details=f"status={status_code}, error={body}")
        print(f"   [ERROR] Failed to create order: {body}")
        return

    # 提交订单
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_post(f"/tool-io-orders/{order_no}/submit", {
        "operator_id": user_id_td,
        "operator_name": "太东旭",
        "operator_role": "team_leader"
    }, token=token_td)

    if status_code == 200 and body.get("success"):
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_submit_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="submitted"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_submit_order", anomalies, critical)
        report.add_step("wf_03", "taidongxu", "提交订单", "PASS", f"order_no={order_no}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_submit_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="submitted"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_submit_order", anomalies, critical)
        report.add_step("wf_03", "taidongxu", "提交订单", "FAIL",
                       details=f"status={status_code}, error={body}")
        print(f"   [ERROR] Failed to submit order: {body}")
        return

    # 验证订单状态变为 submitted
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.set_order_context(order_no, "submitted", "outbound")
        orchestrator.snapshot_before(None)

    status_code, body = api_get(f"/tool-io-orders/{order_no}", token=token_td)
    if status_code == 200:
        order_data = body.get("data", {})
        current_status = order_data.get("order_status", "")
        if current_status in ["submitted", "已提交"]:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    None,
                    operation="wf_verify_status",
                    api_response={"status_code": status_code, "body": body},
                    expected_next_status="submitted"
                )
                critical = sum(1 for a in anomalies if a.severity == "critical")
                _sensing_advance(orchestrator, "wf_verify_status", anomalies, critical)
            report.add_step("wf_04", "taidongxu", "验证订单状态", "PASS",
                           details=f"status={current_status}")
        else:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    None,
                    operation="wf_verify_status",
                    api_response={"status_code": status_code, "body": body},
                    expected_next_status="submitted"
                )
                critical = sum(1 for a in anomalies if a.severity == "critical")
                _sensing_advance(orchestrator, "wf_verify_status", anomalies, critical)
            report.add_step("wf_04", "taidongxu", "验证订单状态", "FAIL",
                           details=f"expected=submitted, actual={current_status}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_verify_status",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="submitted"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_verify_status", anomalies, critical)
        report.add_step("wf_04", "taidongxu", "验证订单状态", "FAIL",
                       details=f"status={status_code}")

    # -------------------------------------------------------------------------
    # 步骤 5-9: 胡婷婷 - 保管员确认
    # -------------------------------------------------------------------------
    print("\n--- Phase 2B: Keeper Confirmation (hutingting) ---")

    if orchestrator:
        orchestrator.set_user_context("hutingting", "KEEPER", "ORG001")
        orchestrator.snapshot_before(None)

    token_ht, user_id_ht, _ = login_user("hutingting", "test123")

    if orchestrator:
        snap, anomalies, checks = orchestrator.snapshot_after(
            None,
            operation="wf_login_hutingting",
            api_response={"status_code": 200 if token_ht else 401},
            expected_next_status="logged_in"
        )
        critical = sum(1 for a in anomalies if a.severity == "critical")
        _sensing_advance(orchestrator, "wf_login_hutingting", anomalies, critical)

    if not token_ht:
        report.add_step("wf_05", "hutingting", "登录", "FAIL", "Login failed")
        return

    report.add_step("wf_05", "hutingting", "登录", "PASS", f"user_id={user_id_ht}")
    TEST_USERS["hutingting"]["token"] = token_ht
    TEST_USERS["hutingting"]["user_id"] = user_id_ht

    # 获取待确认订单列表
    if orchestrator:
        orchestrator.set_user_context("hutingting", "KEEPER", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_get("/tool-io-orders/pending-keeper",
                                 params={"keeper_id": user_id_ht}, token=token_ht)

    if status_code == 200:
        pending_orders = body.get("data", [])
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_get_pending_orders",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="pending_viewed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_get_pending_orders", anomalies, critical)
        report.add_step("wf_06", "hutingting", "获取待确认订单", "PASS",
                       details=f"count={len(pending_orders)}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_get_pending_orders",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="pending_viewed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_get_pending_orders", anomalies, critical)
        report.add_step("wf_06", "hutingting", "获取待确认订单", "FAIL",
                       details=f"status={status_code}")

    # 保管员确认
    if orchestrator:
        orchestrator.set_user_context("hutingting", "KEEPER", "ORG001")
        orchestrator.set_order_context(order_no, "submitted", "outbound")
        orchestrator.snapshot_before(None)

    # First get order detail to extract item_ids
    _, order_detail = api_get(f"/tool-io-orders/{order_no}", token=token_ht)
    order = order_detail.get("data", {}) if order_detail else {}
    order_items = order.get("items", []) if order else []

    status_code, body = step_keeper_confirm(
        order_no,
        token_ht,
        user_id_ht,
        TEST_USERS["fengliang"]["user_id"],
        orchestrator=orchestrator,
        order_items=order_items
    )

    if status_code == 200 and body.get("success"):
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_keeper_confirm",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="keeper_confirmed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_keeper_confirm", anomalies, critical)
        report.add_step("wf_07", "hutingting", "保管员确认", "PASS",
                       details=f"approved_count={body.get('approved_count')}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_keeper_confirm",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="keeper_confirmed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_keeper_confirm", anomalies, critical)
        report.add_step("wf_07", "hutingting", "保管员确认", "FAIL",
                       details=f"status={status_code}, error={body}")
        print(f"   [ERROR] Keeper confirm failed: {body}")
        return

    # 发送运输通知
    if orchestrator:
        orchestrator.set_user_context("hutingting", "KEEPER", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_post(f"/tool-io-orders/{order_no}/notify-transport", {
        "operator_id": user_id_ht,
        "operator_name": "胡婷婷",
        "operator_role": "keeper"
    }, token=token_ht)

    if status_code == 200:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_notify_transport",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="transport_notified"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_notify_transport", anomalies, critical)
        report.add_step("wf_08", "hutingting", "发送运输通知", "PASS")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_notify_transport",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="transport_notified"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_notify_transport", anomalies, critical)
        report.add_step("wf_08", "hutingting", "发送运输通知", "FAIL",
                       details=f"status={status_code}, error={body}")

    # -------------------------------------------------------------------------
    # 步骤 10-12: 冯亮 - 执行运输
    # -------------------------------------------------------------------------
    print("\n--- Phase 2C: Transport Execution (fengliang) ---")

    if orchestrator:
        orchestrator.set_user_context("fengliang", "PRODUCTION_PREP", "ORG001")
        orchestrator.snapshot_before(None)

    token_fl, user_id_fl, _ = login_user("fengliang", "test123")

    if orchestrator:
        snap, anomalies, checks = orchestrator.snapshot_after(
            None,
            operation="wf_login_fengliang",
            api_response={"status_code": 200 if token_fl else 401},
            expected_next_status="logged_in"
        )
        critical = sum(1 for a in anomalies if a.severity == "critical")
        _sensing_advance(orchestrator, "wf_login_fengliang", anomalies, critical)

    if not token_fl:
        report.add_step("wf_09", "fengliang", "登录", "FAIL", "Login failed")
        return

    report.add_step("wf_09", "fengliang", "登录", "PASS", f"user_id={user_id_fl}")
    TEST_USERS["fengliang"]["token"] = token_fl
    TEST_USERS["fengliang"]["user_id"] = user_id_fl

    # 获取预运输列表
    if orchestrator:
        orchestrator.set_user_context("fengliang", "PRODUCTION_PREP", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_get("/tool-io-orders/pre-transport", token=token_fl)
    if status_code == 200:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_get_pre_transport",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="pre_transport_viewed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_get_pre_transport", anomalies, critical)
        report.add_step("wf_10", "fengliang", "获取预运输列表", "PASS",
                       details=f"count={len(body.get('data', []))}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_get_pre_transport",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="pre_transport_viewed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_get_pre_transport", anomalies, critical)
        report.add_step("wf_10", "fengliang", "获取预运输列表", "FAIL",
                       details=f"status={status_code}")

    # 开始运输
    if orchestrator:
        orchestrator.set_user_context("fengliang", "PRODUCTION_PREP", "ORG001")
        orchestrator.set_order_context(order_no, "transport_notified", "outbound")
        orchestrator.snapshot_before(None)

    status_code, body = api_post(f"/tool-io-orders/{order_no}/transport-start", {
        "operator_id": user_id_fl,
        "operator_name": "冯亮",
        "operator_role": "production_prep"
    }, token=token_fl)

    if status_code == 200 and body.get("success"):
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_transport_start",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="transport_in_progress"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_transport_start", anomalies, critical)
        report.add_step("wf_11", "fengliang", "开始运输", "PASS")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_transport_start",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="transport_in_progress"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_transport_start", anomalies, critical)
        report.add_step("wf_11", "fengliang", "开始运输", "FAIL",
                       details=f"status={status_code}, error={body}")
        print(f"   [ERROR] Transport start failed: {body}")
        return

    # 完成运输
    if orchestrator:
        orchestrator.set_user_context("fengliang", "PRODUCTION_PREP", "ORG001")
        orchestrator.snapshot_before(None)

    status_code, body = api_post(f"/tool-io-orders/{order_no}/transport-complete", {
        "operator_id": user_id_fl,
        "operator_name": "冯亮",
        "operator_role": "production_prep"
    }, token=token_fl)

    if status_code == 200 and body.get("success"):
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_transport_complete",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="transport_completed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_transport_complete", anomalies, critical)
        report.add_step("wf_12", "fengliang", "完成运输", "PASS")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_transport_complete",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="transport_completed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_transport_complete", anomalies, critical)
        report.add_step("wf_12", "fengliang", "完成运输", "FAIL",
                       details=f"status={status_code}, error={body}")

    # -------------------------------------------------------------------------
    # 步骤 13-14: 太东旭 - 最终确认
    # -------------------------------------------------------------------------
    print("\n--- Phase 2D: Final Confirmation (taidongxu) ---")

    # 最终确认（出库由班组长确认）
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.set_order_context(order_no, "transport_completed", "outbound")
        orchestrator.snapshot_before(None)

    status_code, body = api_post(f"/tool-io-orders/{order_no}/final-confirm", {
        "operator_id": user_id_td,
        "operator_name": "太东旭",
        "operator_role": "team_leader"
    }, token=token_td)

    if status_code == 200 and body.get("success"):
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_final_confirm",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="completed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_final_confirm", anomalies, critical)
        report.add_step("wf_13", "taidongxu", "最终确认", "PASS",
                       details=f"after_status={body.get('after_status')}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_final_confirm",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="completed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_final_confirm", anomalies, critical)
        report.add_step("wf_13", "taidongxu", "最终确认", "FAIL",
                       details=f"status={status_code}, error={body}")
        print(f"   [ERROR] Final confirm failed: {body}")
        return

    # 验证订单状态变为 completed
    if orchestrator:
        orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
        orchestrator.set_order_context(order_no, "completed", "outbound")
        orchestrator.snapshot_before(None)

    status_code, body = api_get(f"/tool-io-orders/{order_no}", token=token_td)
    if status_code == 200:
        order_data = body.get("data", {})
        current_status = order_data.get("order_status", "")
        if current_status in ["completed", "已完成"]:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    None,
                    operation="wf_verify_completed",
                    api_response={"status_code": status_code, "body": body},
                    expected_next_status="completed"
                )
                critical = sum(1 for a in anomalies if a.severity == "critical")
                _sensing_advance(orchestrator, "wf_verify_completed", anomalies, critical)
            report.add_step("wf_14", "taidongxu", "验证订单完成", "PASS",
                           details=f"status={current_status}")
        else:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    None,
                    operation="wf_verify_completed",
                    api_response={"status_code": status_code, "body": body},
                    expected_next_status="completed"
                )
                critical = sum(1 for a in anomalies if a.severity == "critical")
                _sensing_advance(orchestrator, "wf_verify_completed", anomalies, critical)
            report.add_step("wf_14", "taidongxu", "验证订单完成", "FAIL",
                           details=f"expected=completed, actual={current_status}")
    else:
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="wf_verify_completed",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="completed"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "wf_verify_completed", anomalies, critical)
        report.add_step("wf_14", "taidongxu", "验证订单完成", "FAIL",
                       details=f"status={status_code}")

    # -------------------------------------------------------------------------
    # 清理：删除测试订单
    # -------------------------------------------------------------------------
    print("\n--- Cleanup: Delete test order ---")

    if orchestrator:
        orchestrator.set_user_context("admin", "SYS_ADMIN", "ORG001")
        orchestrator.snapshot_before(None)

    token_admin, user_id_admin, _ = login_user("admin", "admin123")
    if token_admin:
        status_code, body = api_delete(f"/tool-io-orders/{order_no}", {
            "operator_id": user_id_admin,
            "operator_name": "管理员",
            "operator_role": "admin"
        }, token=token_admin)
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation="cleanup_delete_order",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="deleted"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, "cleanup_delete_order", anomalies, critical)
        if status_code == 200:
            report.add_step("cleanup", "admin", "删除测试订单", "PASS",
                           details=f"order_no={order_no}")
        else:
            report.add_step("cleanup", "admin", "删除测试订单", "FAIL",
                           details=f"status={status_code}, error={body}")
        TEST_USERS["admin"]["token"] = token_admin
        TEST_USERS["admin"]["user_id"] = user_id_admin

    print(f"\n[DONE] Workflow test completed, order_no={order_no}")


# =============================================================================
# PHASE 3: RBAC 权限测试
# =============================================================================

# RBAC 测试矩阵 - 基于 docs/RBAC_PERMISSION_MATRIX.md
# 格式: (role, endpoint, method, expected_status_code, permission, expected_result, description)
# expected_result: "ALLOW" (期望200/201) 或 "DENY" (期望403)
RBAC_TEST_MATRIX = [
    # SYS_ADMIN 权限测试 (18个权限点的代表)
    ("SYS_ADMIN", "/tool-io-orders", "GET", 200, "order:list", "ALLOW", "系统管理员可查看订单列表"),
    ("SYS_ADMIN", "/tool-io-orders", "POST", 201, "order:create", "ALLOW", "系统管理员可创建订单"),
    ("SYS_ADMIN", "/admin/users", "GET", 200, "admin:user_manage", "ALLOW", "系统管理员可查看用户列表"),
    ("SYS_ADMIN", "/tool-io-orders/TEST001/keeper-confirm", "POST", 404, "order:keeper_confirm", "ALLOW", "系统管理员可执行保管员确认(订单不存在时返回404非权限问题)"),
    ("SYS_ADMIN", "/tool-io-orders/TEST001/final-confirm", "POST", 404, "order:final_confirm", "ALLOW", "系统管理员可执行最终确认(订单不存在时返回404非权限问题)"),
    ("SYS_ADMIN", "/tool-io-orders/TEST001", "DELETE", 200, "order:delete", "ALLOW", "系统管理员可删除订单"),

    # TEAM_LEADER 权限测试
    ("TEAM_LEADER", "/tool-io-orders", "GET", 200, "order:list", "ALLOW", "班组长可查看订单列表"),
    ("TEAM_LEADER", "/tool-io-orders", "POST", 201, "order:create", "ALLOW", "班组长可创建订单"),
    ("TEAM_LEADER", "/tool-io-orders/TEST001/submit", "POST", 404, "order:submit", "DENY", "班组长不能提交不存在的订单"),
    ("TEAM_LEADER", "/tool-io-orders/TEST001/keeper-confirm", "POST", 403, "order:keeper_confirm", "DENY", "班组长无权执行保管员确认"),
    ("TEAM_LEADER", "/tool-io-orders/TEST001/final-confirm", "POST", 404, "order:final_confirm", "DENY", "班组长不能确认不存在的订单"),
    ("TEAM_LEADER", "/tool-io-orders/TEST001", "DELETE", 403, "order:delete", "DENY", "班组长无权删除订单"),
    ("TEAM_LEADER", "/tool-io-orders/TEST001/reject", "POST", 404, "order:cancel", "DENY", "班组长不能拒绝不存在的订单"),

    # KEEPER 权限测试
    ("KEEPER", "/tool-io-orders", "GET", 200, "order:list", "ALLOW", "保管员可查看订单列表"),
    ("KEEPER", "/tool-io-orders", "POST", 403, "order:create", "DENY", "保管员无权创建订单"),
    ("KEEPER", "/tool-io-orders/TEST001/submit", "POST", 403, "order:submit", "DENY", "保管员无权提交订单"),
    ("KEEPER", "/tool-io-orders/pending-keeper", "GET", 200, "order:keeper_confirm", "ALLOW", "保管员可查看待确认列表"),
    ("KEEPER", "/tool-io-orders/TEST001/keeper-confirm", "POST", 404, "order:keeper_confirm", "DENY", "保管员不能确认不存在的订单"),
    ("KEEPER", "/tool-io-orders/TEST001/final-confirm", "POST", 404, "order:final_confirm", "DENY", "保管员不能确认不存在的订单"),

    # PRODUCTION_PREP 权限测试
    ("PRODUCTION_PREP", "/tool-io-orders", "GET", 403, "order:list", "DENY", "运输工无权查看订单列表"),
    ("PRODUCTION_PREP", "/tool-io-orders", "POST", 403, "order:create", "DENY", "运输工无权创建订单"),
    ("PRODUCTION_PREP", "/tool-io-orders/pre-transport", "GET", 200, "order:transport_execute", "ALLOW", "运输工可查看预运输列表"),
    ("PRODUCTION_PREP", "/tool-io-orders/TEST001/transport-start", "POST", 404, "order:transport_execute", "DENY", "运输工不能启动不存在的运输任务"),
    ("PRODUCTION_PREP", "/tool-io-orders/TEST001/keeper-confirm", "POST", 403, "order:keeper_confirm", "DENY", "运输工无权执行保管员确认"),
]


def record_rbac_result(role: str, permission: str, expected: str, actual: str,
                       status: str, description: str = "", endpoint: str = "",
                       method: str = "", actual_status_code: int = None,
                       details: str = "", orchestrator=None):
    """
    记录 RBAC 测试结果到感知数据库

    Args:
        role: 角色名称
        permission: 权限名称
        expected: 期望结果 (ALLOW/DENY)
        actual: 实际结果 (ALLOW/DENY)
        status: 测试状态 (PASS/FAIL)
        description: 人类可读的测试描述
        endpoint: API 端点
        method: HTTP 方法
        actual_status_code: 实际 HTTP 状态码
        details: 详细信息
        orchestrator: 感知协调器
    """
    if not orchestrator:
        return

    try:
        result = RbacResultRecord(
            rbac_id=f"rbac_{uuid.uuid4().hex[:12]}",
            run_id=orchestrator.run_id,
            created_at=datetime.now().isoformat(),
            role=role,
            permission=permission,
            expected=expected,
            actual=actual,
            status=status,
            description=description,
            endpoint=endpoint,
            method=method,
            actual_status_code=actual_status_code,
            details=details,
        )
        orchestrator.storage.insert_rbac_result(result)
    except Exception as e:
        print(f"   [WARN] Failed to record RBAC result: {e}")


def run_rbac_test(report: TestReport, orchestrator=None):
    """
    RBAC 权限测试 - 使用前置数据 + 明确预期响应模式

    基于 RBAC_TEST_MATRIX 执行测试，每个测试用例包含：
    1. 前置数据准备
    2. 以指定角色登录
    3. 执行操作
    4. 验证预期响应
    5. 记录到感知数据库
    """
    print("\n" + "=" * 50)
    print("[PHASE 3] RBAC Permission Test")
    print("=" * 50)

    # 1. 前置数据准备 - 确保所有用户都已登录
    print("\n[Step 1] Precondition: Login all test users")
    for username, info in TEST_USERS.items():
        if orchestrator:
            role = info.get("role", "UNKNOWN")
            orchestrator.set_user_context(username, role, "ORG001")
            orchestrator.snapshot_before(None)

        token, user_id, _ = login_user(username, info["password"])

        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation=f"rbac_login_{username}",
                api_response={"status_code": 200 if token else 401},
                expected_next_status="logged_in"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, f"rbac_login_{username}", anomalies, critical)

        if token:
            info["token"] = token
            info["user_id"] = user_id
            print(f"   [OK] Logged in {username} as {info.get('role')} (user_id={user_id})")
        else:
            print(f"   [FAIL] Failed to login {username}")

    # 2. 遍历 RBAC 测试矩阵执行测试
    print(f"\n[Step 2] Executing RBAC test matrix ({len(RBAC_TEST_MATRIX)} test cases)")

    # 映射角色到用户名
    role_to_username = {
        "SYS_ADMIN": "admin",
        "TEAM_LEADER": "taidongxu",
        "KEEPER": "hutingting",
        "PRODUCTION_PREP": "fengliang",
    }

    passed_count = 0
    failed_count = 0

    for idx, (role, endpoint, method, expected_status, permission, expected_result, description) in enumerate(RBAC_TEST_MATRIX):
        test_index = idx + 1
        username = role_to_username.get(role)
        info = TEST_USERS.get(username)

        # 跳过未登录的用户
        if not info or not info.get("token"):
            report.add_step(f"rbac_{test_index}", username or role, f"{method} {endpoint}", "SKIP",
                           details=f"User not logged in")
            continue

        token = info.get("token")

        # 3. 执行操作
        if orchestrator:
            orchestrator.set_user_context(username, role, "ORG001")
            orchestrator.snapshot_before(None)

        if method == "GET":
            status_code, body = api_get(endpoint, token=token)
        elif method == "POST":
            status_code, body = api_post(endpoint, {}, token=token)
        elif method == "DELETE":
            status_code, body = api_delete(endpoint, {}, token=token)
        else:
            status_code = 0
            body = {"error": "Unknown method"}

        # 4. 验证预期响应
        # ALLOW: 期望 200/201
        # DENY: 期望 403
        if expected_result == "ALLOW":
            actual_result = "ALLOW" if status_code in [200, 201] else "DENY"
        else:  # DENY
            actual_result = "DENY" if status_code == 403 else "ALLOW"

        test_passed = (actual_result == expected_result)
        test_status = "PASS" if test_passed else "FAIL"

        # 5. 记录到感知数据库
        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                None,
                operation=f"rbac_test_{test_index}",
                api_response={"status_code": status_code, "body": body},
                expected_next_status="rbac_checked"
            )
            critical = sum(1 for a in anomalies if a.severity == "critical")
            _sensing_advance(orchestrator, f"rbac_test_{test_index}", anomalies, critical)

            # 记录 RBAC 结果
            record_rbac_result(
                role=role,
                permission=permission,
                expected=expected_result,
                actual=actual_result,
                status=test_status,
                description=description,
                endpoint=endpoint,
                method=method,
                actual_status_code=status_code,
                details=f"expected_status={expected_status}",
                orchestrator=orchestrator
            )

        # 更新报告
        details = f"{description} | permission={permission}, expected={expected_result}({expected_status}), actual={actual_result}({status_code})"
        report.add_step(f"rbac_{test_index}", role, f"{method} {endpoint}", test_status,
                       details=details, http_status=status_code)

        if test_passed:
            passed_count += 1
            print(f"   [PASS] {test_index:2d}. {role} -> {permission}: {actual_result}")
        else:
            failed_count += 1
            print(f"   [FAIL] {test_index:2d}. {role} -> {permission}: expected={expected_result}, actual={actual_result} (status={status_code})")

    print(f"\n   RBAC Matrix Summary: {passed_count} passed, {failed_count} failed, {len(RBAC_TEST_MATRIX)} total")
    print("[DONE] RBAC test completed")


# =============================================================================
# 主执行入口
# =============================================================================

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("[TEST] Human E2E Tester - API Automation Test")
    print("=" * 70)
    print(f"Backend API: {BACKEND_URL}")
    print(f"Run Prefix: {RUN_PREFIX}")

    # 验证后端服务
    try:
        resp = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if resp.status_code == 200:
            print("[OK] Backend service is healthy")
        else:
            print(f"[WARN] Backend service returned status {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Cannot connect to backend: {e}")
        print("Please ensure backend is running on port 8151")
        return 1

    report = TestReport()

    # P1-2: 初始化感知协调器
    orchestrator = None
    if SENSING_AVAILABLE:
        try:
            orchestrator = SensingOrchestrator(
                db_path=str(E2E_SENSING_DB),
                test_type="full_workflow",
                checkpoint_interval=10,
            )
            print(f"[OK] Sensing orchestrator initialized (run_id={orchestrator.run_id})")
        except Exception as e:
            print(f"[WARN] Failed to init orchestrator: {e}")
            orchestrator = None

    # P1-2: 通知 agent 测试开始
    try:
        start_result = start(test_type="full_workflow")
        print(f"   Agent start: {start_result.get('message', '')}")
    except Exception as e:
        print(f"[WARN] Failed to start agent: {e}")

    # 初始化测试数据管理器
    global _test_data_manager
    dm = TestDataManager(RUN_PREFIX)
    _test_data_manager = dm

    try:
        # setup - 清理旧数据
        dm.setup()

        # PHASE 1: 快速冒烟测试
        run_quick_smoke_test(report, orchestrator)
        # P1-2: 推进 agent 状态
        try:
            advance("phase_1_quick_smoke", report.anomalies.__len__(),
                   len([a for a in report.anomalies if "critical" in str(a)]))
        except Exception as e:
            print(f"[WARN] Failed to advance after phase 1: {e}")

        # PHASE 2: 完整工作流测试
        run_full_workflow_test(report, orchestrator)
        # P1-2: 推进 agent 状态
        try:
            advance("phase_2_full_workflow", report.anomalies.__len__(),
                   len([a for a in report.anomalies if "critical" in str(a)]))
        except Exception as e:
            print(f"[WARN] Failed to advance after phase 2: {e}")

        # PHASE 3: RBAC 权限测试
        run_rbac_test(report, orchestrator)
        # P1-2: 推进 agent 状态
        try:
            advance("phase_3_rbac", report.anomalies.__len__(),
                   len([a for a in report.anomalies if "critical" in str(a)]))
        except Exception as e:
            print(f"[WARN] Failed to advance after phase 3: {e}")

    finally:
        # teardown - 清理测试数据
        dm.teardown()

        # P1-2: 确保 agent 状态推进即使失败
        try:
            advance("test_completed", report.anomalies.__len__(),
                   len([a for a in report.anomalies if "critical" in str(a)]))
        except Exception as e:
            print(f"[WARN] Failed to final advance: {e}")

        # P1-2: 停止 agent
        try:
            stop("Test completed")
        except Exception as e:
            print(f"[WARN] Failed to stop agent: {e}")

        # P1-2: 关闭感知协调器
        if orchestrator:
            try:
                orchestrator.finalize("completed")
            except Exception as e:
                print(f"[WARN] Failed to finalize orchestrator: {e}")

    # 输出报告
    success = report.print_summary()

    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] All tests passed!")
    else:
        print("[WARNING] Some tests failed - see details above")
    print("=" * 70)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
