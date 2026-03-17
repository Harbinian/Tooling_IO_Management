# -*- coding: utf-8 -*-
"""
AnomalyDetector - 异常感知层

捕捉 API 错误响应(500/400/403)、检测空白页/空列表/数据缺失、
检测错误提示缺失/按钮无响应。输出 AnomalyReport[]。
"""

from typing import Optional, Any, Callable
from dataclasses import dataclass
from .snapshot import (
    AnomalyReport,
    Severity,
    TestContext,
    PageSnapshot,
)


# 异常模式库 - 定义各种异常类型的检测函数
ANOMALY_PATTERNS: dict[str, Callable[[Any, PageSnapshot, TestContext], Optional[AnomalyReport]]] = {}


def register_anomaly_pattern(name: str):
    """装饰器：注册异常检测模式"""
    def decorator(func: Callable):
        ANOMALY_PATTERNS[name] = func
        return func
    return decorator


@register_anomaly_pattern("api_500")
def detect_api_500(response: Any, snapshot: PageSnapshot, context: TestContext) -> Optional[AnomalyReport]:
    """检测 API 500 错误"""
    if hasattr(response, "status_code") and response.status_code == 500:
        return AnomalyReport(
            anomaly_type="api_500",
            severity="critical",
            description=f"API 返回服务器错误 (500): {get_error_message(response)}",
            page_name=snapshot.page_name,
            order_no=snapshot.order_no or context.current_order_no,
            evidence={"status_code": 500, "response": get_response_body(response)},
        )
    return None


@register_anomaly_pattern("api_403")
def detect_api_403(response: Any, snapshot: PageSnapshot, context: TestContext) -> Optional[AnomalyReport]:
    """检测 API 403 权限错误"""
    if hasattr(response, "status_code") and response.status_code == 403:
        return AnomalyReport(
            anomaly_type="api_403",
            severity="high",
            description=f"API 返回权限错误 (403): {get_error_message(response)}",
            page_name=snapshot.page_name,
            order_no=snapshot.order_no or context.current_order_no,
            evidence={"status_code": 403, "response": get_response_body(response)},
            suspected_cause="当前用户无权执行此操作，或 RBAC 配置错误",
        )
    return None


@register_anomaly_pattern("api_400")
def detect_api_400(response: Any, snapshot: PageSnapshot, context: TestContext) -> Optional[AnomalyReport]:
    """检测 API 400 参数错误"""
    if hasattr(response, "status_code") and response.status_code == 400:
        return AnomalyReport(
            anomaly_type="api_400",
            severity="high",
            description=f"API 返回参数错误 (400): {get_error_message(response)}",
            page_name=snapshot.page_name,
            order_no=snapshot.order_no or context.current_order_no,
            evidence={"status_code": 400, "response": get_response_body(response)},
            suspected_cause="前端参数与后端 API 期望不一致",
        )
    return None


@register_anomaly_pattern("silent_fail")
def detect_silent_fail(snapshot: PageSnapshot, context: TestContext) -> Optional[AnomalyReport]:
    """检测操作无反馈（静默失败）"""
    # 条件：执行了操作但页面无变化且无错误提示
    if context.last_operation and not context.last_api_called:
        return None  # API 没调用，不算静默失败

    if context.last_operation and context.last_api_called:
        # API 被调用了，但页面没有错误提示，且没有成功提示
        if not snapshot.error_message and not snapshot.success_message:
            return AnomalyReport(
                anomaly_type="silent_fail",
                severity="high",
                description=f"执行了'{context.last_operation}'后，API 可能有错误但页面未显示错误信息",
                page_name=snapshot.page_name,
                order_no=snapshot.order_no or context.current_order_no,
                evidence={"operation": context.last_operation},
            )
    return None


@register_anomaly_pattern("blank_page")
def detect_blank_page(snapshot: PageSnapshot, context: TestContext) -> Optional[AnomalyReport]:
    """检测空白页面（有数据但页面不显示）"""
    # 列表页应该有数据但显示为空
    if snapshot.page_name == "OrderList":
        if snapshot.table_rows == 0 and snapshot.raw_text.strip():
            # 有文本内容但表格为空，可能有渲染问题
            return AnomalyReport(
                anomaly_type="blank_page",
                severity="medium",
                description="订单列表页面有内容但表格为空，可能存在筛选逻辑错误或数据未正确渲染",
                page_name=snapshot.page_name,
                order_no=None,
                evidence={"raw_text_length": len(snapshot.raw_text)},
            )

    # 详情页应该是空的
    if snapshot.page_name == "OrderDetail":
        if not snapshot.fields and not snapshot.order_no:
            return AnomalyReport(
                anomaly_type="blank_page",
                severity="high",
                description="订单详情页面为空，无法获取订单信息",
                page_name=snapshot.page_name,
                order_no=snapshot.order_no,
            )

    return None


@register_anomaly_pattern("missing_error_display")
def detect_missing_error_display(snapshot: PageSnapshot, context: TestContext) -> Optional[AnomalyReport]:
    """检测操作失败但页面没有显示错误"""
    if context.last_operation and context.last_api_called:
        response = context.last_api_response
        if response:
            # API 返回失败
            is_failed = False
            if hasattr(response, "status_code") and response.status_code >= 400:
                is_failed = True
            elif hasattr(response, "json"):
                try:
                    data = response.json()
                    if isinstance(data, dict) and data.get("success") is False:
                        is_failed = True
                except Exception:
                    pass

            if is_failed and not snapshot.error_message:
                return AnomalyReport(
                    anomaly_type="missing_error_display",
                    severity="high",
                    description=f"API 返回失败但页面未显示错误提示",
                    page_name=snapshot.page_name,
                    order_no=snapshot.order_no or context.current_order_no,
                    evidence={"operation": context.last_operation},
                    suspected_cause="前端未正确处理 API 错误响应",
                )
    return None


@register_anomaly_pattern("button_no_response")
def detect_button_no_response(snapshot: PageSnapshot, context: TestContext) -> Optional[AnomalyReport]:
    """检测按钮点击后无响应"""
    if context.last_operation and not context.last_api_called:
        # 用户点击了某个按钮，但没有任何 API 调用
        operation_keywords = {
            "submit": ["提交", "submit"],
            "confirm": ["确认", "confirm"],
            "delete": ["删除", "delete"],
            "cancel": ["取消", "cancel"],
        }

        for op, keywords in operation_keywords.items():
            if context.last_operation.lower() in [k.lower() for k in keywords]:
                # 这是一个应该触发 API 的操作，但没有 API 调用
                return AnomalyReport(
                    anomaly_type="button_no_response",
                    severity="high",
                    description=f"点击了'{context.last_operation}'但没有任何 API 请求发出",
                    page_name=snapshot.page_name,
                    order_no=snapshot.order_no or context.current_order_no,
                    suspected_cause="按钮点击事件未绑定或被阻止",
                )

    return None


def get_error_message(response: Any) -> str:
    """从响应中提取错误消息"""
    if hasattr(response, "text"):
        try:
            import json
            data = json.loads(response.text)
            if isinstance(data, dict):
                return data.get("error", data.get("message", response.text))
        except Exception:
            pass
        return response.text[:200]
    return str(response)


def get_response_body(response: Any) -> dict:
    """获取响应体"""
    if hasattr(response, "text"):
        try:
            import json
            return json.loads(response.text)
        except Exception:
            return {"raw": response.text[:500]}
    return {}


def detect_api_response_anomalies(
    snapshot: PageSnapshot,
    context: TestContext
) -> list[AnomalyReport]:
    """
    检测 API 响应异常

    Args:
        snapshot: 页面快照
        context: 测试上下文

    Returns:
        异常报告列表
    """
    anomalies = []
    response = context.last_api_response

    # 调用所有注册的 API 异常检测模式
    for pattern_name, detector in ANOMALY_PATTERNS.items():
        if "api_" in pattern_name and response:
            try:
                report = detector(response, snapshot, context)
                if report:
                    anomalies.append(report)
            except Exception:
                pass

    return anomalies


def detect_page_anomalies(
    snapshot: PageSnapshot,
    context: TestContext
) -> list[AnomalyReport]:
    """
    检测页面异常

    Args:
        snapshot: 页面快照
        context: 测试上下文

    Returns:
        异常报告列表
    """
    anomalies = []

    # 调用所有注册的页面异常检测模式
    for pattern_name, detector in ANOMALY_PATTERNS.items():
        if "api_" not in pattern_name:
            try:
                report = detector(snapshot, context)
                if report:
                    anomalies.append(report)
            except Exception:
                pass

    return anomalies


def detect_all_anomalies(
    snapshot: PageSnapshot,
    context: TestContext
) -> list[AnomalyReport]:
    """
    综合检测所有异常

    这是 AnomalyDetector 的核心入口函数。

    Args:
        snapshot: 页面快照
        context: 测试上下文

    Returns:
        异常报告列表
    """
    all_anomalies = []

    # 1. API 响应异常
    if context.last_api_called and context.last_api_response:
        api_anomalies = detect_api_response_anomalies(snapshot, context)
        all_anomalies.extend(api_anomalies)

    # 2. 页面异常
    page_anomalies = detect_page_anomalies(snapshot, context)
    all_anomalies.extend(page_anomalies)

    return all_anomalies
