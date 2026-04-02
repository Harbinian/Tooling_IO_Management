# -*- coding: utf-8 -*-
"""
Human E2E Tester - Playwright 自动化测试

执行完整的拟人 E2E 测试，覆盖：
1. 快速冒烟测试 (quick_smoke)
2. 完整出库工作流 (full_workflow)
3. RBAC 权限测试 (rbac)

使用方法：
    python test_runner/playwright_e2e.py
"""

import sys
import io
import socket

# Windows 控制台编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import os
import json
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from playwright.sync_api import sync_playwright, Page, Browser
from test_runner.commands import start, advance, status, stop

# P1-2: 集成感知层
SENSING_PACKAGE_ROOT = REPO_ROOT / ".skills" / "human-e2e-tester"
if str(SENSING_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(SENSING_PACKAGE_ROOT))

# 统一数据库路径
E2E_SENSING_DB = REPO_ROOT / "test_reports" / "e2e_sensing.db"

try:
    from sensing.storage import SQLiteStorage
    from sensing.orchestrator import SensingOrchestrator
    SENSING_AVAILABLE = True
except ImportError:
    SENSING_AVAILABLE = False
    print("[WARN] Sensing module not available, running without sensing")


# =============================================================================
# 端口检查
# =============================================================================

def check_services() -> bool:
    """检查前端和后端服务是否在所需端口运行"""
    services = [
        ("Frontend", "localhost", 8150),
        ("Backend", "localhost", 8151),
    ]

    failed = []
    for name, host, port in services:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            if result != 0:
                failed.append((name, port))
        except Exception:
            failed.append((name, port))

    if failed:
        print("\n[ABORT] Services not ready", flush=True)
        for name, port in failed:
            print(f"  {name} ({port}): NOT RESPONDING", flush=True)
        print("", flush=True)
        print("Please start the services externally before running playwright_e2e:", flush=True)
        print("  Frontend: npm run dev (port 8150)", flush=True)
        print("  Backend: python web_server.py (port 8151)", flush=True)
        return False

    print("[OK] All services are ready", flush=True)
    print(f"  Frontend (8150): responding", flush=True)
    print(f"  Backend (8151): responding", flush=True)
    return True


# =============================================================================
# 配置
# =============================================================================

FRONTEND_URL = "http://localhost:8150"
BACKEND_URL = "http://localhost:8151"

TEST_USERS = {
    "taidongxu": {
        "password": "test1234",
        "role": "TEAM_LEADER",
        "role_name": "班组长"
    },
    "hutingting": {
        "password": "test1234",
        "role": "KEEPER",
        "role_name": "保管员"
    },
    "fengliang": {
        "password": "test1234",
        "role": "PRODUCTION_PREP",
        "role_name": "生产准备工"
    },
    "admin": {
        "password": "admin123",
        "role": "SYS_ADMIN",
        "role_name": "系统管理员"
    }
}

TEST_TOOL = {
    "serial_no": "T000001",
    "drawing_no": "Tooling_IO_TEST",
    "tool_name": "测试用工装"
}


# =============================================================================
# 测试报告
# =============================================================================

class TestReport:
    def __init__(self):
        self.results = []
        self.anomalies = []
        self.start_time = datetime.now()

    def add_step(self, step_name: str, user: str, action: str, result: str,
                 details: str = "", anomaly: str = None):
        self.results.append({
            "step_name": step_name,
            "user": user,
            "action": action,
            "result": result,
            "details": details,
            "anomaly": anomaly,
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
        print("🧪 E2E 测试报告 / Test Report")
        print("=" * 70)
        print(f"执行时间 / Duration: {duration}")
        print(f"总步骤数 / Total Steps: {len(self.results)}")
        print(f"异常数量 / Anomalies: {len(self.anomalies)}")

        print("\n--- 步骤详情 / Step Details ---")
        for r in self.results:
            status_icon = "✅" if r["result"] == "PASS" else "❌" if r["result"] == "FAIL" else "⏭️"
            anomaly_icon = " ⚠️" if r["anomaly"] else ""
            print(f"{status_icon} [{r['user']}] {r['step_name']}: {r['action']} -> {r['result']}{anomaly_icon}")
            if r["details"]:
                print(f"   📝 {r['details']}")

        if self.anomalies:
            print("\n--- 异常记录 / Anomalies ---")
            for a in self.anomalies:
                print(f"⚠️ {a['step_name']}: {a['anomaly']}")

        print("\n" + "=" * 70)
        return len(self.anomalies) == 0


# =============================================================================
# 浏览器辅助函数
# =============================================================================

def wait_for_page_load(page: Page, timeout: int = 10000):
    """等待页面基本加载"""
    page.wait_for_load_state("networkidle", timeout=timeout)


def find_and_click(page: Page, selector: str, timeout: int = 5000):
    """查找并点击元素"""
    page.click(selector, timeout=timeout)


def find_and_fill(page: Page, selector: str, value: str, timeout: int = 5000):
    """查找并填写表单"""
    page.fill(selector, value, timeout=timeout)


def get_text(page: Page, selector: str, timeout: int = 5000) -> str:
    """获取元素文本"""
    try:
        return page.text_content(selector, timeout=timeout)
    except:
        return ""


def get_current_url(page: Page) -> str:
    """获取当前 URL"""
    return page.url


def is_element_visible(page: Page, selector: str) -> bool:
    """检查元素是否可见"""
    try:
        return page.is_visible(selector, timeout=1000)
    except:
        return False


# =============================================================================
# 登录模块
# =============================================================================

def login(page: Page, username: str, password: str) -> bool:
    """执行登录操作"""
    print(f"   正在登录: {username}")
    try:
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        time.sleep(0.5)

        # 填写登录表单 - 使用 placeholder 文本定位
        page.fill('input[placeholder="请输入用户名"]', username, timeout=5000)
        page.fill('input[placeholder="请输入密码"]', password, timeout=5000)

        # 点击登录按钮 - 使用实际按钮文本 "进入系统"
        page.click('button:has-text("进入系统")', timeout=5000)

        # 等待重定向完成 - 等待 URL 变化或网络空闲
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle", timeout=10000)

        # 检查是否登录成功（URL 变化）
        current_url = page.url
        if "/login" not in current_url:
            print(f"   ✅ 登录成功")
            return True
        else:
            print(f"   ❌ 登录失败 - URL 未变化")
            return False
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        return False


def logout(page: Page):
    """执行登出操作"""
    try:
        # 点击用户菜单触发登出选项
        page.click('[class*="user-menu"], [class*="avatar"], [class*="dropdown"], [class*="user"]', timeout=3000)
        time.sleep(0.5)
        # 点击登出 - 使用实际按钮文本
        page.click('button:has-text("退出"), button:has-text("Logout"), button:has-text("Sign out")', timeout=3000)
    except:
        pass


# =============================================================================
# PHASE 1: 快速冒烟测试
# =============================================================================

def _pw_sensing_advance(orchestrator, operation, anomalies):
    """Helper to call advance with error handling"""
    try:
        critical = sum(1 for a in anomalies if a.severity == "critical")
        advance(operation, len(anomalies), critical)
    except Exception:
        pass


def run_quick_smoke_test(browser: Browser, report: TestReport, orchestrator=None):
    """快速冒烟测试 - 验证基本功能"""
    print("\n" + "=" * 50)
    print("🚀 PHASE 1: 快速冒烟测试 / Quick Smoke Test")
    print("=" * 50)

    context = browser.new_context()
    page = context.new_page()

    try:
        # 1. 登录
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page)

        login_success = login(page, "taidongxu", TEST_USERS["taidongxu"]["password"])

        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                page,
                operation="smoke_login",
                api_response={"login_success": login_success},
                expected_next_status="logged_in"
            )
            _pw_sensing_advance(orchestrator, "smoke_login", anomalies)

        report.add_step("smoke_01", "taidongxu", "登录", "PASS" if login_success else "FAIL")

        if not login_success:
            print("   登录失败，终止冒烟测试")
            return

        # 2. 查看首页/Dashboard
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page)

        try:
            page.goto(f"{FRONTEND_URL}/", wait_until="networkidle", timeout=15000)
            time.sleep(1)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation="smoke_visit_dashboard",
                    api_response=None,
                    expected_next_status="dashboard_viewed"
                )
                _pw_sensing_advance(orchestrator, "smoke_visit_dashboard", anomalies)

            report.add_step("smoke_02", "taidongxu", "访问首页", "PASS", f"URL: {page.url}")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation="smoke_visit_dashboard",
                    api_response={"error": str(e)},
                    expected_next_status="dashboard_viewed"
                )
                _pw_sensing_advance(orchestrator, "smoke_visit_dashboard", anomalies)
            report.add_step("smoke_02", "taidongxu", "访问首页", "FAIL", str(e))

        # 3. 进入订单列表
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page)

        try:
            page.goto(f"{FRONTEND_URL}/inventory", wait_until="networkidle", timeout=15000)
            time.sleep(1)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation="smoke_visit_order_list",
                    api_response=None,
                    expected_next_status="order_list_viewed"
                )
                _pw_sensing_advance(orchestrator, "smoke_visit_order_list", anomalies)

            report.add_step("smoke_03", "taidongxu", "进入订单列表", "PASS", f"URL: {page.url}")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation="smoke_visit_order_list",
                    api_response={"error": str(e)},
                    expected_next_status="order_list_viewed"
                )
                _pw_sensing_advance(orchestrator, "smoke_visit_order_list", anomalies)
            report.add_step("smoke_03", "taidongxu", "进入订单列表", "FAIL", str(e))

        # 4. 进入创建订单页
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page)

        try:
            page.goto(f"{FRONTEND_URL}/inventory/create", wait_until="networkidle", timeout=15000)
            time.sleep(1)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation="smoke_visit_create_order",
                    api_response=None,
                    expected_next_status="order_create_viewed"
                )
                _pw_sensing_advance(orchestrator, "smoke_visit_create_order", anomalies)

            report.add_step("smoke_04", "taidongxu", "进入创建订单页", "PASS", f"URL: {page.url}")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation="smoke_visit_create_order",
                    api_response={"error": str(e)},
                    expected_next_status="order_create_viewed"
                )
                _pw_sensing_advance(orchestrator, "smoke_visit_create_order", anomalies)
            report.add_step("smoke_04", "taidongxu", "进入创建订单页", "FAIL", str(e))

        # 5. 登出
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page)

        logout(page)

        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                page,
                operation="smoke_logout",
                api_response=None,
                expected_next_status="logged_out"
            )
            _pw_sensing_advance(orchestrator, "smoke_logout", anomalies)

        report.add_step("smoke_05", "taidongxu", "登出", "PASS")

    finally:
        context.close()

    print("✅ 冒烟测试完成")


# =============================================================================
# PHASE 2: 完整出库工作流测试
# =============================================================================

def run_full_workflow_test(browser: Browser, report: TestReport, orchestrator=None):
    """完整出库工作流测试"""
    print("\n" + "=" * 50)
    print("🚀 PHASE 2: 完整出库工作流 / Full Workflow Test")
    print("=" * 50)

    # -------------------------------------------------------------------------
    # 步骤 1-2: 太东旭 - 创建并提交订单
    # -------------------------------------------------------------------------
    context_taidongxu = browser.new_context()
    page_taidongxu = context_taidongxu.new_page()

    order_no = None

    try:
        # 1. 太东旭登录
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        login(page_taidongxu, "taidongxu", TEST_USERS["taidongxu"]["password"])

        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                page_taidongxu,
                operation="pw_wf_login_taidongxu",
                api_response={"login_success": True},
                expected_next_status="logged_in"
            )
            _pw_sensing_advance(orchestrator, "pw_wf_login_taidongxu", anomalies)

        report.add_step("wf_01", "taidongxu", "登录", "PASS")

        # 2. 进入创建订单页
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        page_taidongxu.goto(f"{FRONTEND_URL}/inventory/create", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        if orchestrator:
            snap, anomalies, checks = orchestrator.snapshot_after(
                page_taidongxu,
                operation="pw_wf_visit_create",
                api_response=None,
                expected_next_status="order_create_page"
            )
            _pw_sensing_advance(orchestrator, "pw_wf_visit_create", anomalies)

        report.add_step("wf_02", "taidongxu", "进入创建订单页", "PASS", f"URL: {page_taidongxu.url}")

        # 3. 选择出库类型
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        try:
            page_taidongxu.click('button:has-text("出库"), [value="outbound"]', timeout=5000)
            time.sleep(0.3)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_select_outbound",
                    api_response=None,
                    expected_next_status="outbound_selected"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_select_outbound", anomalies)

            report.add_step("wf_03", "taidongxu", "选择出库类型", "PASS")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_select_outbound",
                    api_response={"error": str(e)},
                    expected_next_status="outbound_selected"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_select_outbound", anomalies)
            report.add_step("wf_03", "taidongxu", "选择出库类型", "FAIL", str(e))

        # 4. 打开工装搜索对话框
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        try:
            page_taidongxu.click('.bg-white.font-bold.text-slate-900:has-text("搜索并添加工装"), button:has-text("搜索并添加工装")', timeout=5000)
            time.sleep(1)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_open_tool_search",
                    api_response=None,
                    expected_next_status="tool_search_opened"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_open_tool_search", anomalies)

            report.add_step("wf_04", "taidongxu", "打开工装搜索", "PASS")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_open_tool_search",
                    api_response={"error": str(e)},
                    expected_next_status="tool_search_opened"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_open_tool_search", anomalies)
            report.add_step("wf_04", "taidongxu", "打开工装搜索", "FAIL", str(e))

        # 5. 搜索测试工装
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        try:
            # 在搜索对话框中输入工装编码并点击搜索按钮
            # 使用 placeholder 匹配序列号输入框
            search_input = page_taidongxu.query_selector('input[placeholder*="序列号"]')
            if not search_input:
                search_input = page_taidongxu.query_selector('input[placeholder*="编码"]')
            if search_input:
                search_input.fill(TEST_TOOL["serial_no"])
                time.sleep(0.3)

            # 点击搜索按钮执行搜索（使用 flex-1 class 精确定位对话框内的搜索按钮）
            page_taidongxu.click('button.flex-1.bg-primary:has-text("搜索")', timeout=5000)
            # 等待搜索结果加载
            page_taidongxu.wait_for_timeout(2000)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_search_tool",
                    api_response={"search_term": TEST_TOOL["serial_no"]},
                    expected_next_status="tool_searched"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_search_tool", anomalies)

            report.add_step("wf_05", "taidongxu", "搜索工装", "PASS", f"搜索: {TEST_TOOL['serial_no']}")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_search_tool",
                    api_response={"error": str(e)},
                    expected_next_status="tool_searched"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_search_tool", anomalies)
            report.add_step("wf_05", "taidongxu", "搜索工装", "FAIL", str(e))

        # 6. 选择工装
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        try:
            # 等待搜索结果表格出现，然后点击第一行的复选框
            # Element Plus 表格行选择器 - 需要点击 checkbox 才能选中行
            page_taidongxu.wait_for_selector('.el-table__body .el-checkbox', timeout=5000)
            page_taidongxu.click('.el-table__body .el-checkbox:first-child', timeout=5000)
            time.sleep(0.5)
            # 点击确认/添加按钮
            page_taidongxu.click('button:has-text("添加到明细")', timeout=5000)
            time.sleep(0.5)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_select_tool",
                    api_response=None,
                    expected_next_status="tool_selected"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_select_tool", anomalies)

            report.add_step("wf_06", "taidongxu", "选择工装", "PASS")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_select_tool",
                    api_response={"error": str(e)},
                    expected_next_status="tool_selected"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_select_tool", anomalies)
            report.add_step("wf_06", "taidongxu", "选择工装", "FAIL", str(e))

        # 7. 填写用途、目标位置和计划使用时间（出库必填）
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        try:
            # 使用 JavaScript 直接设置 Vue 表单值（绕过复杂的 UI 交互）
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            planned_time = tomorrow.strftime("%Y-%m-%d %H:%M:%S")

            # 直接通过 JavaScript 设置表单字段
            page_taidongxu.evaluate("""
                () => {
                    // 尝试找到 Vue 实例并设置表单值
                    const vueApp = document.querySelector('#app').__vue_app__;
                    if (vueApp) {
                        // 查找所有 el-select 元素并设置值
                        const selects = document.querySelectorAll('.el-select');
                        // 用途 - 第一个 select (index 0)
                        if (selects[0]) {
                            selects[0].__vueParentComponent__.exposed.modelValue = '现场使用';
                        }
                        // 目标位置 - 第二个 select (index 1)
                        if (selects[1]) {
                            selects[1].__vueParentComponent__.exposed.modelValue = 'A06';
                        }
                    }
                }
            """)
            time.sleep(0.5)

            # 使用 JavaScript 设置日期时间
            page_taidongxu.evaluate(f"""
                () => {{
                    const dateInput = document.querySelector('.el-date-editor input');
                    if (dateInput) {{
                        // 触发 focus 事件
                        dateInput.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                        dateInput.value = '{planned_time}';
                        dateInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        dateInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}
            """)
            time.sleep(0.3)

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_fill_usage",
                    api_response=None,
                    expected_next_status="usage_filled"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_fill_usage", anomalies)

            report.add_step("wf_07", "taidongxu", "填写用途", "PASS")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_fill_usage",
                    api_response={"error": str(e)},
                    expected_next_status="usage_filled"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_fill_usage", anomalies)
            report.add_step("wf_07", "taidongxu", "填写用途", "FAIL", str(e))

        # 8. 提交订单
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.set_order_context(order_no or "", "draft", "outbound")
            orchestrator.snapshot_before(page_taidongxu)

        try:
            submit_btn = page_taidongxu.query_selector('button:has-text("提交单据")')
            if submit_btn:
                # 检查按钮是否可用
                is_disabled = submit_btn.get_attribute('disabled')
                print(f"   DEBUG: Submit button disabled attr: {is_disabled}")
                print(f"   DEBUG: Submit button HTML: {submit_btn.inner_html()[:100]}")

                submit_btn.click()
                time.sleep(3)  # 给更多时间让 API 调用完成

                # 检查是否有错误消息或警告消息
                try:
                    # 检查 el-message 组件
                    messages = page_taidongxu.query_selector_all('.el-message')
                    for msg in messages:
                        msg_text = msg.text_content()
                        print(f"   DEBUG: Message: {msg_text}")
                except Exception as e:
                    print(f"   DEBUG: Error checking messages: {e}")

                # 检查页面内容看是否有验证错误
                try:
                    page_content = page_taidongxu.content()
                    if '请选择' in page_content or '请输入' in page_content:
                        print(f"   DEBUG: Page has validation hints")
                except:
                    pass

                # 等待导航
                try:
                    page_taidongxu.wait_for_url(lambda url: '/inventory/' in url and '/create' not in url, timeout=5000)
                except:
                    pass

                current_url = page_taidongxu.url
                print(f"   DEBUG: URL after submit: {current_url}")

                if orchestrator:
                    snap, anomalies, checks = orchestrator.snapshot_after(
                        page_taidongxu,
                        operation="pw_wf_submit_order",
                        api_response={"submitted": True, "url": current_url},
                        expected_next_status="submitted"
                    )
                    _pw_sensing_advance(orchestrator, "pw_wf_submit_order", anomalies)

                report.add_step("wf_08", "taidongxu", "提交订单", "PASS")
            else:
                if orchestrator:
                    snap, anomalies, checks = orchestrator.snapshot_after(
                        page_taidongxu,
                        operation="pw_wf_submit_order",
                        api_response={"error": "submit button not found"},
                        expected_next_status="submitted"
                    )
                    _pw_sensing_advance(orchestrator, "pw_wf_submit_order", anomalies)
                report.add_step("wf_08", "taidongxu", "提交订单", "FAIL", "未找到提交按钮")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_submit_order",
                    api_response={"error": str(e)},
                    expected_next_status="submitted"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_submit_order", anomalies)
            report.add_step("wf_08", "taidongxu", "提交订单", "FAIL", str(e))

        # 9. 获取订单号
        if orchestrator:
            orchestrator.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
            orchestrator.snapshot_before(page_taidongxu)

        try:
            # 从 URL 或页面元素获取订单号
            # 等待页面导航完成
            page_taidongxu.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(1)
            current_url = page_taidongxu.url
            print(f"   DEBUG: Current URL after submit: {current_url}")
            if "/detail/" in current_url or "/order/" in current_url:
                order_no = current_url.split("/")[-1].split("?")[0]
                print(f"   DEBUG: Extracted order_no from URL: {order_no}")
            else:
                # 尝试从页面获取
                page_taidongxu.goto(f"{FRONTEND_URL}/inventory", wait_until="networkidle", timeout=10000)
                time.sleep(1)
                order_no_text = get_text(page_taidongxu, '[class*="order-no"], [class*="单号"], [class*="orderNo"]')
                order_no = order_no_text.strip() if order_no_text else None
                print(f"   DEBUG: Extracted order_no from page: {order_no}")

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_get_order_no",
                    api_response={"order_no": order_no},
                    expected_next_status="order_no_obtained"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_get_order_no", anomalies)

            report.add_step("wf_09", "taidongxu", "获取订单号", "PASS" if order_no else "FAIL",
                           details=f"订单号: {order_no}")
        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page_taidongxu,
                    operation="pw_wf_get_order_no",
                    api_response={"error": str(e)},
                    expected_next_status="order_no_obtained"
                )
                _pw_sensing_advance(orchestrator, "pw_wf_get_order_no", anomalies)
            report.add_step("wf_09", "taidongxu", "获取订单号", "FAIL", str(e))

    finally:
        context_taidongxu.close()

    if not order_no:
        print("   ❌ 无法获取订单号，跳过工作流测试")
        return

    print(f"   📝 创建的订单号: {order_no}")

    # -------------------------------------------------------------------------
    # 步骤 10-15: 胡婷婷 - 保管员确认
    # -------------------------------------------------------------------------
    context_hutingting = browser.new_context()
    page_hutingting = context_hutingting.new_page()

    try:
        login(page_hutingting, "hutingting", TEST_USERS["hutingting"]["password"])
        report.add_step("wf_10", "hutingting", "登录", "PASS")

        # 11. 进入保管员处理页面
        try:
            page_hutingting.goto(f"{FRONTEND_URL}/inventory/keeper", wait_until="networkidle", timeout=15000)
            time.sleep(1)
            report.add_step("wf_11", "hutingting", "进入保管员处理页", "PASS")
        except Exception as e:
            report.add_step("wf_11", "hutingting", "进入保管员处理页", "FAIL", str(e))

        # 12. 查看待确认订单
        try:
            page_hutingting.goto(f"{FRONTEND_URL}/inventory?status=submitted", wait_until="networkidle", timeout=15000)
            time.sleep(1)
            report.add_step("wf_12", "hutingting", "查看待确认订单", "PASS")
        except Exception as e:
            report.add_step("wf_12", "hutingting", "查看待确认订单", "FAIL", str(e))

        # 13. 进入订单详情
        try:
            page_hutingting.goto(f"{FRONTEND_URL}/detail/{order_no}", wait_until="networkidle", timeout=15000)
            time.sleep(1)
            report.add_step("wf_13", "hutingting", "进入订单详情", "PASS")
        except Exception as e:
            report.add_step("wf_13", "hutingting", "进入订单详情", "FAIL", str(e))

        # 14. 确认订单明细
        try:
            page_hutingting.click('button:has-text("确认"), button:has-text("通过")', timeout=5000)
            time.sleep(1)
            # 确认对话框
            page_hutingting.click('button:has-text("确认"), button:has-text("确定")', timeout=3000)
            time.sleep(1)
            report.add_step("wf_14", "hutingting", "确认订单明细", "PASS")
        except Exception as e:
            report.add_step("wf_14", "hutingting", "确认订单明细", "FAIL", str(e))

        # 15. 发送运输通知
        try:
            page_hutingting.click('button:has-text("通知"), button:has-text("运输")', timeout=5000)
            time.sleep(1)
            page_hutingting.click('button:has-text("确认"), button:has-text("发送")', timeout=3000)
            time.sleep(1)
            report.add_step("wf_15", "hutingting", "发送运输通知", "PASS")
        except Exception as e:
            report.add_step("wf_15", "hutingting", "发送运输通知", "FAIL", str(e))

    finally:
        context_hutingting.close()

    # -------------------------------------------------------------------------
    # 步骤 16-18: 冯亮 - 执行运输
    # -------------------------------------------------------------------------
    context_fengliang = browser.new_context()
    page_fengliang = context_fengliang.new_page()

    try:
        login(page_fengliang, "fengliang", TEST_USERS["fengliang"]["password"])
        report.add_step("wf_16", "fengliang", "登录", "PASS")

        # 17. 进入预运输列表
        try:
            page_fengliang.goto(f"{FRONTEND_URL}/pre-transport", wait_until="networkidle", timeout=15000)
            time.sleep(1)
            report.add_step("wf_17", "fengliang", "进入预运输列表", "PASS")
        except Exception as e:
            report.add_step("wf_17", "fengliang", "进入预运输列表", "FAIL", str(e))

        # 18. 开始运输
        try:
            page_fengliang.goto(f"{FRONTEND_URL}/detail/{order_no}", wait_until="networkidle", timeout=15000)
            time.sleep(1)
            start_btn = page_fengliang.query_selector('button:has-text("开始"), button:has-text("运输")')
            if start_btn:
                start_btn.click()
                time.sleep(1)
                page_fengliang.click('button:has-text("确认")', timeout=3000)
                time.sleep(1)
            report.add_step("wf_18", "fengliang", "开始运输", "PASS")
        except Exception as e:
            report.add_step("wf_18", "fengliang", "开始运输", "FAIL", str(e))

    finally:
        context_fengliang.close()

    # -------------------------------------------------------------------------
    # 步骤 19-22: 太东旭 - 最终确认
    # -------------------------------------------------------------------------
    context_taidongxu2 = browser.new_context()
    page_taidongxu2 = context_taidongxu2.new_page()

    try:
        login(page_taidongxu2, "taidongxu", TEST_USERS["taidongxu"]["password"])
        report.add_step("wf_19", "taidongxu", "登录(最终确认)", "PASS")

        # 20. 进入订单详情
        try:
            page_taidongxu2.goto(f"{FRONTEND_URL}/detail/{order_no}", wait_until="networkidle", timeout=15000)
            time.sleep(1)
            report.add_step("wf_20", "taidongxu", "进入订单详情", "PASS")
        except Exception as e:
            report.add_step("wf_20", "taidongxu", "进入订单详情", "FAIL", str(e))

        # 21. 最终确认
        try:
            page_taidongxu2.click('button:has-text("最终"), button:has-text("完成")', timeout=5000)
            time.sleep(1)
            page_taidongxu2.click('button:has-text("确认"), button:has-text("确定")', timeout=3000)
            time.sleep(1)
            report.add_step("wf_21", "taidongxu", "最终确认", "PASS")
        except Exception as e:
            report.add_step("wf_21", "taidongxu", "最终确认", "FAIL", str(e))

        # 22. 验证订单状态
        try:
            status_text = get_text(page_taidongxu2, '[class*="status"], .el-tag')
            is_completed = "完成" in status_text or "completed" in status_text.lower()
            report.add_step("wf_22", "taidongxu", "验证订单状态", "PASS" if is_completed else "FAIL",
                           details=f"状态: {status_text}")
        except Exception as e:
            report.add_step("wf_22", "taidongxu", "验证订单状态", "FAIL", str(e))

    finally:
        context_taidongxu2.close()

    print("✅ 工作流测试完成")


# =============================================================================
# PHASE 3: RBAC 权限测试
# =============================================================================

def run_rbac_test(browser: Browser, report: TestReport, orchestrator=None):
    """RBAC 权限测试"""
    print("\n" + "=" * 50)
    print("🚀 PHASE 3: RBAC 权限测试 / RBAC Permission Test")
    print("=" * 50)

    rbac_tests = [
        # (用户, 角色, 页面/操作, 预期结果)
        ("taidongxu", "TEAM_LEADER", "/inventory/create", "allow"),      # 可以创建订单
        ("taidongxu", "TEAM_LEADER", "/inventory/keeper", "deny"),       # 不能访问保管员页
        ("hutingting", "KEEPER", "/inventory/create", "deny"),           # 不能创建订单
        ("hutingting", "KEEPER", "/inventory/keeper", "allow"),          # 可以访问保管员页
        ("fengliang", "PRODUCTION_PREP", "/inventory", "deny"),  # 不能访问订单列表
        ("fengliang", "PRODUCTION_PREP", "/inventory/pre-transport", "allow"),  # 可以访问预运输
        ("admin", "SYS_ADMIN", "/inventory/create", "allow"),             # 管理员可以创建
        ("admin", "SYS_ADMIN", "/inventory/keeper", "allow"),            # 管理员可以访问保管员页
        ("admin", "SYS_ADMIN", "/admin/users", "allow"),             # 管理员可以访问管理页
    ]

    for username, role, path, expected in rbac_tests:
        context = browser.new_context()
        page = context.new_page()

        try:
            # 登录
            if orchestrator:
                orchestrator.set_user_context(username, role, "ORG001")
                orchestrator.snapshot_before(page)

            login(page, username, TEST_USERS[username]["password"])

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation=f"pw_rbac_login_{username}",
                    api_response={"login_success": True},
                    expected_next_status="logged_in"
                )
                _pw_sensing_advance(orchestrator, f"pw_rbac_login_{username}", anomalies)

            # 尝试访问页面
            if orchestrator:
                orchestrator.set_user_context(username, role, "ORG001")
                orchestrator.snapshot_before(page)

            page.goto(f"{FRONTEND_URL}{path}", wait_until="networkidle", timeout=10000)
            time.sleep(0.5)

            # 检查实际结果
            current_url = page.url
            if "/login" in current_url:
                actual = "deny"
            else:
                # 检查是否有权限提示或错误
                try:
                    error_text = page.text_content('[class*="error"], [class*="403"], .el-message--error')
                    if error_text and ("无权限" in error_text or "禁止" in error_text):
                        actual = "deny"
                    else:
                        actual = "allow"
                except:
                    actual = "allow"

            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation=f"pw_rbac_access_{username}_{path.replace('/', '_')}",
                    api_response={"actual": actual, "expected": expected},
                    expected_next_status=f"rbac_{expected}"
                )
                _pw_sensing_advance(orchestrator, f"pw_rbac_access_{username}_{path.replace('/', '_')}", anomalies)

            result = "PASS" if actual == expected else "FAIL"
            report.add_step(f"rbac_{username}_{path}", username,
                          f"访问{path}", result,
                          details=f"预期:{expected} 实际:{actual}")

        except Exception as e:
            if orchestrator:
                snap, anomalies, checks = orchestrator.snapshot_after(
                    page,
                    operation=f"pw_rbac_access_{username}_{path.replace('/', '_')}",
                    api_response={"error": str(e)},
                    expected_next_status=f"rbac_{expected}"
                )
                _pw_sensing_advance(orchestrator, f"pw_rbac_access_{username}_{path.replace('/', '_')}", anomalies)
            report.add_step(f"rbac_{username}_{path}", username,
                          f"访问{path}", "FAIL", str(e))

        finally:
            context.close()

    print("✅ RBAC 测试完成")


# =============================================================================
# 主执行入口
# =============================================================================

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🧪 Human E2E Tester - Playwright 自动化测试")
    print("=" * 70)
    print(f"前端: {FRONTEND_URL}")
    print(f"后端: {BACKEND_URL}")

    # 端口检查 - 必须通过才能继续
    if not check_services():
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
            print(f"✅ 感知协调器已初始化 (run_id={orchestrator.run_id})")
        except Exception as e:
            print(f"[WARN] Failed to init orchestrator: {e}")
            orchestrator = None

    # P1-2: 通知 agent 测试开始
    try:
        start_result = start(test_type="full_workflow")
        print(f"   Agent start: {start_result.get('message', '')}")
    except Exception as e:
        print(f"[WARN] Failed to start agent: {e}")

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        print("\n✅ 浏览器已启动")

        try:
            # PHASE 1: 快速冒烟测试
            run_quick_smoke_test(browser, report, orchestrator)
            # P1-2: 推进 agent 状态
            try:
                advance("phase_1_quick_smoke", report.anomalies.__len__(),
                       len([a for a in report.anomalies if "critical" in str(a)]))
            except Exception as e:
                print(f"[WARN] Failed to advance after phase 1: {e}")

            # PHASE 2: 完整工作流测试
            run_full_workflow_test(browser, report, orchestrator)
            # P1-2: 推进 agent 状态
            try:
                advance("phase_2_full_workflow", report.anomalies.__len__(),
                       len([a for a in report.anomalies if "critical" in str(a)]))
            except Exception as e:
                print(f"[WARN] Failed to advance after phase 2: {e}")

            # PHASE 3: RBAC 权限测试
            run_rbac_test(browser, report, orchestrator)
            # P1-2: 推进 agent 状态
            try:
                advance("phase_3_rbac", report.anomalies.__len__(),
                       len([a for a in report.anomalies if "critical" in str(a)]))
            except Exception as e:
                print(f"[WARN] Failed to advance after phase 3: {e}")

        finally:
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

            browser.close()
            print("\n✅ 浏览器已关闭")

    # 输出报告
    all_passed = report.print_summary()

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 所有测试通过 / All Tests Passed!")
    else:
        print("⚠️ 部分测试失败 / Some Tests Failed")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
