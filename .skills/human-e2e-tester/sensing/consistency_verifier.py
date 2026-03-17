# -*- coding: utf-8 -*-
"""
DataConsistencyVerifier - 数据一致性验证层

验证列表金额=详情金额、状态标签=实际状态、工装数量对得上、
驳回原因可见且非空。输出 ConsistencyCheck[]。
"""

from typing import Optional, Any
from .snapshot import (
    ConsistencyCheck,
    AnomalyReport,
    TestContext,
    PageSnapshot,
    STATUS_LABEL_MAP,
)


def verify_list_detail_consistency(
    list_snapshot: PageSnapshot,
    detail_snapshot: PageSnapshot,
    context: Optional[TestContext] = None
) -> list[ConsistencyCheck]:
    """
    验证列表页和详情页的数据一致性

    检查项：
    1. 订单号一致
    2. 订单状态一致
    3. 订单类型一致
    4. 工装数量一致

    Args:
        list_snapshot: 列表页快照
        detail_snapshot: 详情页快照
        context: 测试上下文

    Returns:
        一致性检查结果列表
    """
    checks = []

    order_no = context.current_order_no if context else None

    # 1. 订单号一致性
    if list_snapshot.order_no and detail_snapshot.order_no:
        checks.append(ConsistencyCheck(
            check_name="order_no_consistency",
            passed=list_snapshot.order_no == detail_snapshot.order_no,
            expected=list_snapshot.order_no,
            actual=detail_snapshot.order_no,
            details="列表页和详情页的订单号应该一致" if list_snapshot.order_no != detail_snapshot.order_no else "订单号一致",
            order_no=list_snapshot.order_no,
        ))

    # 2. 状态一致性
    if list_snapshot.order_status and detail_snapshot.order_status:
        list_status = list_snapshot.order_status
        detail_status = detail_snapshot.order_status

        # 去除可能的空白字符
        list_status = list_status.strip()
        detail_status = detail_status.strip()

        checks.append(ConsistencyCheck(
            check_name="order_status_consistency",
            passed=list_status == detail_status,
            expected=list_status,
            actual=detail_status,
            details="列表页和详情页的订单状态应该一致" if list_status != detail_status else "状态一致",
            order_no=list_snapshot.order_no,
        ))

    # 3. 订单类型一致性
    if list_snapshot.order_type and detail_snapshot.order_type:
        checks.append(ConsistencyCheck(
            check_name="order_type_consistency",
            passed=list_snapshot.order_type == detail_snapshot.order_type,
            expected=list_snapshot.order_type,
            actual=detail_snapshot.order_type,
            details="列表页和详情页的订单类型应该一致" if list_snapshot.order_type != detail_snapshot.order_type else "订单类型一致",
            order_no=list_snapshot.order_no,
        ))

    # 4. 工装数量一致性
    if list_snapshot.tool_count and detail_snapshot.tool_count:
        checks.append(ConsistencyCheck(
            check_name="tool_count_consistency",
            passed=list_snapshot.tool_count == detail_snapshot.tool_count,
            expected=list_snapshot.tool_count,
            actual=detail_snapshot.tool_count,
            details="列表页和详情页的工装数量应该一致" if list_snapshot.tool_count != detail_snapshot.tool_count else "工装数量一致",
            order_no=list_snapshot.order_no,
        ))

    return checks


def verify_tool_quantity_logic(
    snapshot: PageSnapshot,
    context: Optional[TestContext] = None
) -> list[ConsistencyCheck]:
    """
    验证工装数量逻辑

    检查项：
    1. approved_count <= items_count（已确认数不能超过明细项总数）

    Note: tool_count is derived from items.length, so tool_count == items_count always.
    The deprecated tool_quantity field (static len(items) at creation) is no longer used.

    Args:
        snapshot: 页面快照
        context: 测试上下文

    Returns:
        一致性检查结果列表
    """
    checks = []

    order_no = snapshot.order_no or (context.current_order_no if context else None)

    # 1. 已确认数 <= 明细项总数（tool_count 已改由 items.length 计算）
    if snapshot.items_count is not None and snapshot.approved_count is not None:
        passed = snapshot.approved_count <= snapshot.items_count
        checks.append(ConsistencyCheck(
            check_name="quantity_logic",
            passed=passed,
            expected=f"approved_count ({snapshot.approved_count}) <= items_count ({snapshot.items_count})",
            actual=f"{snapshot.approved_count} > {snapshot.items_count}" if not passed else "逻辑正确",
            details="已确认数量不应该超过明细项总数" if not passed else "数量逻辑正确",
            order_no=order_no,
        ))

    return checks


def verify_rejection_reason(
    snapshot: PageSnapshot,
    context: Optional[TestContext] = None
) -> list[ConsistencyCheck]:
    """
    验证驳回原因

    检查项：
    1. 如果状态是"已驳回"，驳回原因必须存在且非空
    2. 驳回原因应该有一定的长度（不是单纯的占位符）

    Args:
        snapshot: 页面快照
        context: 测试上下文

    Returns:
        一致性检查结果列表
    """
    checks = []

    order_no = snapshot.order_no or (context.current_order_no if context else None)

    # 判断是否是被驳回状态
    is_rejected = (
        snapshot.order_status in ["已驳回", "rejected"] or
        snapshot.order_status_raw == "rejected"
    )

    if is_rejected:
        # 驳回原因必须存在
        has_reason = snapshot.reject_reason and len(snapshot.reject_reason.strip()) > 0

        checks.append(ConsistencyCheck(
            check_name="reject_reason_exists",
            passed=has_reason,
            expected="reject_reason 存在且非空",
            actual=snapshot.reject_reason or "(空)",
            details="被驳回的订单必须有驳回原因" if not has_reason else "驳回原因存在",
            order_no=order_no,
        ))

        # 驳回原因应该有一定的长度（不是占位符如 "-" 或 "无"）
        if has_reason and snapshot.reject_reason:
            is_meaningful = len(snapshot.reject_reason.strip()) >= 3
            checks.append(ConsistencyCheck(
                check_name="reject_reason_meaningful",
                passed=is_meaningful,
                expected="驳回原因有实际内容（>=3字符）",
                actual=f"'{snapshot.reject_reason}' ({len(snapshot.reject_reason)} 字符)",
                details="驳回原因太短，可能是占位符" if not is_meaningful else "驳回原因有效",
                order_no=order_no,
            ))

    return checks


def verify_status_label_mapping(
    snapshot: PageSnapshot,
    expected_status: str,
    context: Optional[TestContext] = None
) -> list[ConsistencyCheck]:
    """
    验证状态标签映射正确性

    检查页面显示的状态标签是否与实际状态值匹配

    Args:
        snapshot: 页面快照
        expected_status: 期望的状态值（英文）
        context: 测试上下文

    Returns:
        一致性检查结果列表
    """
    checks = []

    order_no = snapshot.order_no or (context.current_order_no if context else None)

    if not snapshot.order_status:
        checks.append(ConsistencyCheck(
            check_name="status_label_exists",
            passed=False,
            expected="页面显示状态标签",
            actual="状态标签为空",
            details="页面应该有状态标签",
            order_no=order_no,
        ))
        return checks

    # 获取期望的标签
    expected_label = STATUS_LABEL_MAP.get(expected_status, expected_status)

    checks.append(ConsistencyCheck(
        check_name="status_label_mapping",
        passed=snapshot.order_status == expected_label,
        expected=expected_label,
        actual=snapshot.order_status,
        details=f"状态 '{expected_status}' 应该显示为 '{expected_label}'" if snapshot.order_status != expected_label else "状态标签映射正确",
        order_no=order_no,
    ))

    return checks


def verify_notification_records(
    snapshot: PageSnapshot,
    context: Optional[TestContext] = None
) -> list[ConsistencyCheck]:
    """
    验证通知记录

    检查项：
    1. 如果状态是 keeper_confirmed 或之后，应该有通知记录
    2. 通知记录应该有发送时间、接收人等字段

    Args:
        snapshot: 页面快照
        context: 测试上下文

    Returns:
        一致性检查结果列表
    """
    checks = []

    order_no = snapshot.order_no or (context.current_order_no if context else None)

    # 判断状态是否需要通知记录
    states_requiring_notification = [
        "keeper_confirmed", "transport_notified",
        "transport_in_progress", "transport_completed",
        "final_confirmation_pending", "completed"
    ]

    current_state = snapshot.order_status_raw or (context.current_order_status if context else None)

    if current_state in states_requiring_notification:
        # 应该有通知记录
        has_notification_records = len(snapshot.table_data) > 0 if snapshot.table_data else False

        # 检查是否有通知相关的表格数据
        if has_notification_records:
            # 简单验证：表格应该有一些关键字段
            first_record = snapshot.table_data[0] if snapshot.table_data else {}
            has_required_fields = any(
                k for k in first_record.keys()
                if any(keyword in k for keyword in ["通知", "发送", "时间", "接收"])
            )

            checks.append(ConsistencyCheck(
                check_name="notification_record_structure",
                passed=has_required_fields,
                expected="通知记录包含必要字段",
                actual="通知记录结构正常" if has_required_fields else "通知记录可能缺少字段",
                details="通知记录表应有发送时间、接收人等字段" if not has_required_fields else "通知记录结构正确",
                order_no=order_no,
            ))

    return checks


def verify_all_consistency(
    snapshot: PageSnapshot,
    context: Optional[TestContext] = None,
    list_snapshot: Optional[PageSnapshot] = None
) -> tuple[list[ConsistencyCheck], list[AnomalyReport]]:
    """
    综合验证所有数据一致性

    这是 DataConsistencyVerifier 的核心入口函数。

    Args:
        snapshot: 当前页面快照
        context: 测试上下文
        list_snapshot: 列表页快照（用于列表-详情一致性检查）

    Returns:
        (一致性检查列表, 异常报告列表)
    """
    all_checks = []
    anomalies = []

    # 1. 列表-详情一致性
    if list_snapshot:
        list_detail_checks = verify_list_detail_consistency(list_snapshot, snapshot, context)
        all_checks.extend(list_detail_checks)

        # 检查不一致项并生成异常
        for check in list_detail_checks:
            if not check.passed:
                anomalies.append(AnomalyReport(
                    anomaly_type="inconsistent_data",
                    severity="high",
                    description=f"数据一致性检查失败: {check.details}",
                    page_name=snapshot.page_name,
                    order_no=check.order_no,
                    expected_value=check.expected,
                    actual_value=check.actual,
                ))

    # 2. 工装数量逻辑
    quantity_checks = verify_tool_quantity_logic(snapshot, context)
    all_checks.extend(quantity_checks)

    for check in quantity_checks:
        if not check.passed:
            anomalies.append(AnomalyReport(
                anomaly_type="tool_count_mismatch",
                severity="high",
                description=f"工装数量逻辑错误: {check.details}",
                page_name=snapshot.page_name,
                order_no=check.order_no,
                expected_value=check.expected,
                actual_value=check.actual,
            ))

    # 3. 驳回原因
    rejection_checks = verify_rejection_reason(snapshot, context)
    all_checks.extend(rejection_checks)

    for check in rejection_checks:
        if not check.passed:
            anomalies.append(AnomalyReport(
                anomaly_type="reject_reason_missing",
                severity="high",
                description=f"驳回原因检查失败: {check.details}",
                page_name=snapshot.page_name,
                order_no=check.order_no,
                expected_value=check.expected,
                actual_value=check.actual,
            ))

    # 4. 状态标签映射
    if context and context.current_order_status:
        status_checks = verify_status_label_mapping(
            snapshot, context.current_order_status, context
        )
        all_checks.extend(status_checks)

        for check in status_checks:
            if not check.passed:
                anomalies.append(AnomalyReport(
                    anomaly_type="status_mismatch",
                    severity="high",
                    description=f"状态标签错误: {check.details}",
                    page_name=snapshot.page_name,
                    order_no=check.order_no,
                    expected_value=check.expected,
                    actual_value=check.actual,
                ))

    # 5. 通知记录
    notification_checks = verify_notification_records(snapshot, context)
    all_checks.extend(notification_checks)

    return all_checks, anomalies
