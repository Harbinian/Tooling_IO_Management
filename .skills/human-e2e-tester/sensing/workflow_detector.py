# -*- coding: utf-8 -*-
"""
WorkflowStateDetector - 工作流感知层

根据 PageSnapshot 推断订单当前状态，检查可用操作按钮是否与状态匹配，
检测状态转换是否合法。输出 WorkflowPosition。
"""

from typing import Optional
from .snapshot import (
    PageSnapshot,
    WorkflowPosition,
    WORKFLOW_TRANSITIONS,
    STATE_AVAILABLE_ACTIONS,
    STATE_FORBIDDEN_ACTIONS,
    STATUS_LABEL_MAP,
    LABEL_TO_STATUS,
    AnomalyReport,
    TestContext,
)


def infer_workflow_state(snapshot: PageSnapshot) -> tuple[Optional[str], Optional[str]]:
    """
    根据页面快照推断工作流状态

    推断逻辑（按优先级）：
    1. 直接从 snapshot.order_status_raw 获取（如果有）
    2. 从 snapshot.order_status（中文标签）转换
    3. 从页面 URL 或其他上下文推断
    4. 从页面上的状态标签文字匹配

    Returns:
        (状态值英文, 状态标签中文) 或 (None, None)
    """
    # 优先使用原始状态值
    if snapshot.order_status_raw:
        label = STATUS_LABEL_MAP.get(snapshot.order_status_raw, snapshot.order_status_raw)
        return snapshot.order_status_raw, label

    # 从中文标签转换
    if snapshot.order_status:
        status_value = LABEL_TO_STATUS.get(snapshot.order_status)
        if status_value:
            return status_value, snapshot.order_status

    # 尝试从 URL 或其他上下文推断
    url = snapshot.url.lower()
    if "draft" in url:
        return "draft", "草稿"
    if "completed" in url:
        return "completed", "已完成"

    # 尝试从页面内容匹配
    page_text = snapshot.raw_text
    for status_value, label in STATUS_LABEL_MAP.items():
        if label in page_text:
            return status_value, label

    return None, None


def get_expected_buttons_for_state(state: str, order_type: str) -> tuple[list[str], list[str]]:
    """
    获取某个状态下应该出现和不应该出现的按钮

    Args:
        state: 状态值（英文）
        order_type: 订单类型（outbound/inbound）

    Returns:
        (应该可见的按钮列表, 不应该出现的按钮列表)
    """
    available = STATE_AVAILABLE_ACTIONS.get(state, [])

    # 出库特殊处理：final_confirm 由班组长执行
    if order_type == "outbound" and "final_confirm" in available:
        # final_confirm 在出库流程中是班组长执行
        pass

    # 入库特殊处理：final_confirm 由保管员执行
    if order_type == "inbound" and "final_confirm" in available:
        pass

    forbidden = STATE_FORBIDDEN_ACTIONS.get(state, [])

    return available, forbidden


def verify_button_visibility(
    snapshot: PageSnapshot,
    expected_available: list[str],
    expected_forbidden: list[str]
) -> tuple[bool, list[str], list[str]]:
    """
    验证按钮可见性是否符合预期

    Args:
        snapshot: 页面快照
        expected_available: 预期可见的按钮
        expected_forbidden: 预期不可见的按钮

    Returns:
        (是否匹配, 多余出现的按钮, 缺失的按钮)
    """
    visible_lower = [b.lower() for b in snapshot.visible_buttons]
    disabled_lower = [b.lower() for b in snapshot.disabled_buttons]

    extra_buttons = []      # 不应该出现但出现的按钮
    missing_buttons = []    # 应该出现但不存在的按钮

    # 检查预期可见的按钮
    button_text_mapping = {
        "submit": ["提交", "submit"],
        "delete": ["删除", "delete"],
        "edit": ["编辑", "edit", "修改"],
        "keeper_confirm": ["确认", "保管员确认", "keeper"],
        "cancel": ["取消", "cancel"],
        "notify_transport": ["通知运输", "发送通知", "notify"],
        "transport_start": ["开始运输", "运输开始", "start"],
        "transport_complete": ["完成运输", "运输完成", "complete"],
        "final_confirm": ["最终确认", "确认完成", "final"],
        "resubmit": ["重新提交", "重提", "resubmit"],
        "report_issue": ["上报异常", "问题上报", "issue"],
    }

    for action in expected_available:
        # 找到这个 action 对应的按钮文本变体
        variants = button_text_mapping.get(action, [action])
        found = any(v.lower() in visible_lower for v in variants)

        if not found:
            # 检查是否在 disabled 中
            is_disabled = any(v.lower() in disabled_lower for v in variants)
            if not is_disabled:
                missing_buttons.append(action)

    # 检查预期不应该出现的按钮
    for action in expected_forbidden:
        variants = button_text_mapping.get(action, [action])
        found = any(v.lower() in visible_lower for v in variants)
        if found:
            extra_buttons.append(action)

    matches = len(extra_buttons) == 0 and len(missing_buttons) == 0
    return matches, extra_buttons, missing_buttons


def verify_state_transition(
    current_state: str,
    target_state: str,
    order_type: str
) -> tuple[bool, str]:
    """
    验证状态转换是否合法

    Args:
        current_state: 当前状态
        target_state: 目标状态
        order_type: 订单类型

    Returns:
        (是否合法, 错误消息)
    """
    transitions = WORKFLOW_TRANSITIONS.get(order_type, {})

    if current_state not in transitions:
        return False, f"未知状态: {current_state}"

    allowed = transitions.get(current_state, [])
    if target_state not in allowed:
        return False, f"状态 {current_state} 不能转换到 {target_state}，允许的转换: {allowed}"

    return True, ""


def detect_workflow_position(
    snapshot: PageSnapshot,
    context: Optional[TestContext] = None
) -> WorkflowPosition:
    """
    检测工作流位置

    这是 WorkflowStateDetector 的核心函数，综合分析页面快照，
    推断订单当前的工作流位置。

    Args:
        snapshot: 页面快照
        context: 测试上下文

    Returns:
        WorkflowPosition: 工作流位置对象
    """
    order_no = snapshot.order_no or (context.current_order_no if context else None)
    order_type = snapshot.order_type or (context.current_order_type if context else "outbound")

    # 推断当前状态
    current_state, current_label = infer_workflow_state(snapshot)

    if current_state is None:
        # 无法推断状态，返回未知位置
        return WorkflowPosition(
            order_no=order_no or "",
            order_type=order_type,
            current_state="unknown",
            current_state_label="未知",
            available_actions=[],
            forbidden_actions=[],
            expected_next_states=[],
            actual_buttons_match=False,
        )

    # 获取预期按钮
    expected_available, expected_forbidden = get_expected_buttons_for_state(
        current_state, order_type
    )

    # 验证按钮可见性
    matches, extra_buttons, missing_buttons = verify_button_visibility(
        snapshot, expected_available, expected_forbidden
    )

    # 获取允许的下一状态
    transitions = WORKFLOW_TRANSITIONS.get(order_type, {})
    expected_next = transitions.get(current_state, [])

    position = WorkflowPosition(
        order_no=order_no or "",
        order_type=order_type,
        current_state=current_state,
        current_state_label=current_label,
        available_actions=expected_available,
        forbidden_actions=expected_forbidden,
        expected_next_states=expected_next,
        actual_buttons_match=matches,
    )

    if extra_buttons or missing_buttons:
        position.button_mismatches = {
            "extra": extra_buttons,
            "missing": missing_buttons,
        }

    return position


def detect_workflow_anomalies(
    snapshot: PageSnapshot,
    position: WorkflowPosition,
    context: Optional[TestContext] = None
) -> list[AnomalyReport]:
    """
    检测工作流异常

    Args:
        snapshot: 页面快照
        position: 工作流位置
        context: 测试上下文

    Returns:
        异常报告列表
    """
    anomalies = []

    # 1. 按钮可见性不匹配
    if not position.actual_buttons_match and position.button_mismatches:
        mismatches = position.button_mismatches

        # 缺失的按钮（严重）
        for missing in mismatches.get("missing", []):
            anomalies.append(AnomalyReport(
                anomaly_type="button_should_be_visible",
                severity="high",
                description=f"状态为'{position.current_state_label}'时，按钮'{missing}'应该可见但不存在的",
                page_name=snapshot.page_name,
                order_no=position.order_no,
                expected_value=f"按钮 '{missing}' 可见",
                actual_value="按钮不存在或被禁用",
            ))

        # 多余的按钮（中等）
        for extra in mismatches.get("extra", []):
            anomalies.append(AnomalyReport(
                anomaly_type="button_gone",
                severity="medium",
                description=f"状态为'{position.current_state_label}'时，按钮'{extra}'不应该出现但存在的",
                page_name=snapshot.page_name,
                order_no=position.order_no,
                expected_value=f"按钮 '{extra}' 不存在",
                actual_value="按钮可见",
            ))

    # 2. 未知状态
    if position.current_state == "unknown":
        anomalies.append(AnomalyReport(
            anomaly_type="workflow_blocked",
            severity="critical",
            description="无法识别订单当前状态",
            page_name=snapshot.page_name,
            order_no=position.order_no,
            evidence={"url": snapshot.url, "page_text": snapshot.raw_text[:500]},
        ))

    # 3. 终态但仍有操作按钮
    if position.is_terminal() and position.actual_buttons_match is False:
        if snapshot.visible_buttons:
            anomalies.append(AnomalyReport(
                anomaly_type="workflow_blocked",
                severity="medium",
                description=f"订单已完成/取消，但仍有操作按钮: {snapshot.visible_buttons}",
                page_name=snapshot.page_name,
                order_no=position.order_no,
            ))

    return anomalies


def detect_illegal_transition(
    before_state: str,
    after_state: str,
    order_type: str,
    context: Optional[TestContext] = None
) -> Optional[AnomalyReport]:
    """
    检测非法状态转换

    Args:
        before_state: 转换前状态
        after_state: 转换后状态
        order_type: 订单类型
        context: 测试上下文

    Returns:
        异常报告（如果有的话）
    """
    is_valid, error_msg = verify_state_transition(before_state, after_state, order_type)

    if not is_valid:
        return AnomalyReport(
            anomaly_type="illegal_state_transition",
            severity="critical",
            description=f"状态转换非法: {error_msg}",
            order_no=context.current_order_no if context else None,
            expected_value=f"合法状态转换到 {after_state}",
            actual_value=f"{before_state} -> {after_state} ({error_msg})",
            evidence={
                "before_state": before_state,
                "after_state": after_state,
                "order_type": order_type,
            },
        )

    return None
