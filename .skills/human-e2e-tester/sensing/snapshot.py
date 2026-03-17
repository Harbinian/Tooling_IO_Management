# -*- coding: utf-8 -*-
"""
核心数据结构 - 拟人 E2E 测试感知模块

定义页面快照、工作流位置、异常报告、数据一致性检查等核心数据结构。
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum


class Severity(Enum):
    """异常严重等级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AnomalyType(Enum):
    """异常类型枚举"""
    # API 相关
    API_500 = "api_500"
    API_403 = "api_403"
    API_400 = "api_400"
    SILENT_FAIL = "silent_fail"

    # 页面状态相关
    STATUS_MISMATCH = "status_mismatch"
    BLANK_PAGE = "blank_page"
    BUTTON_GONE = "button_gone"
    BUTTON_SHOULD_BE_DISABLED = "button_should_be_disabled"
    BUTTON_SHOULD_BE_VISIBLE = "button_should_be_visible"

    # 数据相关
    MISSING_FIELD = "missing_field"
    FIELD_VALUE_MISMATCH = "field_value_mismatch"
    REJECT_REASON_MISSING = "reject_reason_missing"
    TOOL_COUNT_MISMATCH = "tool_count_mismatch"
    INCONSISTENT_DATA = "inconsistent_data"

    # 工作流相关
    ILLEGAL_STATE_TRANSITION = "illegal_state_transition"
    WORKFLOW_BLOCKED = "workflow_blocked"

    # 布局相关
    LAYOUT_BROKEN = "layout_broken"
    TEXT_GIBBERISH = "text_gibberish"


# 订单状态标签映射 (来自 OrderList.vue orderStatusMap)
STATUS_LABEL_MAP = {
    "draft": "草稿",
    "submitted": "已提交",
    "keeper_confirmed": "保管员已确认",
    "partially_confirmed": "部分确认",
    "transport_notified": "已通知运输",
    "transport_in_progress": "运输中",
    "transport_completed": "运输已完成",
    "final_confirmation_pending": "待最终确认",
    "completed": "已完成",
    "rejected": "已驳回",
    "cancelled": "已取消",
}

# 反向映射：标签到状态值
LABEL_TO_STATUS = {v: k for k, v in STATUS_LABEL_MAP.items()}

# 工装系统工作流状态转换规则
WORKFLOW_TRANSITIONS = {
    "outbound": {
        "draft": ["submitted", "cancelled"],
        "submitted": ["keeper_confirmed", "rejected", "cancelled"],
        "keeper_confirmed": ["transport_notified", "rejected", "cancelled"],
        "transport_notified": ["transport_in_progress", "rejected"],
        "transport_in_progress": ["transport_completed"],
        "transport_completed": ["final_confirmation_pending"],
        "final_confirmation_pending": ["completed"],
        "completed": [],
        "rejected": ["submitted", "cancelled"],  # 可以重提或取消
        "cancelled": [],
    },
    "inbound": {
        "draft": ["submitted", "cancelled"],
        "submitted": ["keeper_confirmed", "rejected", "cancelled"],
        "keeper_confirmed": ["transport_notified", "rejected", "cancelled"],
        "transport_notified": ["transport_in_progress", "rejected"],
        "transport_in_progress": ["transport_completed"],
        "transport_completed": ["final_confirmation_pending"],
        "final_confirmation_pending": ["completed"],
        "completed": [],
        "rejected": ["submitted", "cancelled"],
        "cancelled": [],
    },
}

# 各状态下应该可见/可点击的按钮
STATE_AVAILABLE_ACTIONS = {
    "draft": ["submit", "delete", "edit"],
    "submitted": ["keeper_confirm", "cancel"],
    "keeper_confirmed": ["notify_transport", "cancel"],
    "transport_notified": ["transport_start", "cancel"],
    "transport_in_progress": ["transport_complete", "report_issue"],
    "transport_completed": ["final_confirm"],
    "final_confirmation_pending": ["final_confirm"],
    "completed": [],
    "rejected": ["resubmit", "cancel"],
    "cancelled": [],
}

# 各状态不应该出现的按钮
STATE_FORBIDDEN_ACTIONS = {
    "draft": ["keeper_confirm", "final_confirm", "transport_start", "notify_transport"],
    "submitted": ["final_confirm", "transport_start"],
    "completed": ["submit", "cancel", "delete", "keeper_confirm", "final_confirm"],
    "rejected": ["keeper_confirm", "final_confirm", "transport_start", "notify_transport"],
}

# 乱码特征字符检测
GIBBERISH_PATTERNS = [
    "鍒涘缓", "宸ヨ", "鎼滅储", "鍗曟", "涓氬姟", "涓嶅彲",
    "\u934f\u93c7", "\u92c7\u92c5", "\u93dd\u9389",
]


@dataclass
class PageSnapshot:
    """
    页面快照 - 某一时刻的页面状态

    拟人测试者"看到"页面的方式，类似于 Selenium/Playwright 的页面源码分析。
    """
    page_name: str                              # e.g. "OrderList", "OrderDetail", "OrderCreate"
    url: str                                    # 当前 URL
    order_no: Optional[str] = None              # 如果是订单相关页，记录订单号
    order_status: Optional[str] = None          # 状态标签显示的值（中文）
    order_status_raw: Optional[str] = None     # 状态原始值（英文）
    order_type: Optional[str] = None            # 订单类型 outbound/inbound

    # 表格数据
    table_rows: int = 0                        # 表格行数
    table_data: list[dict] = field(default_factory=list)  # 表格原始数据

    # 按钮状态
    visible_buttons: list[str] = field(default_factory=list)   # 当前可见且可点的按钮
    disabled_buttons: list[str] = field(default_factory=list) # 灰掉的按钮
    absent_buttons: list[str] = field(default_factory=list)   # 应该存在但不存在的按钮

    # 错误和警告
    error_message: Optional[str] = None         # 当前页面的错误提示
    warning_message: Optional[str] = None       # 当前页面的警告提示
    success_message: Optional[str] = None      # 成功提示

    # 关键字段
    fields: dict[str, Any] = field(default_factory=dict)      # 页面关键字段名→值
    items_count: int = 0                       # 明细项数量
    tool_count: int = 0                        # 工装总数
    approved_count: int = 0                     # 已确认数

    # 驳回相关
    reject_reason: Optional[str] = None        # 驳回原因

    # 运输相关
    transport_operator: Optional[str] = None    # 运输操作员

    # 原始内容（用于深度检查）
    raw_text: str = ""                          # 页面文本内容
    raw_html: str = ""                          # 原始 HTML

    def has_errors(self) -> bool:
        """是否有错误"""
        return self.error_message is not None

    def has_warnings(self) -> bool:
        """是否有警告"""
        return self.warning_message is not None

    def get_status_value(self) -> Optional[str]:
        """获取状态值（从中文标签转为英文）"""
        if self.order_status:
            return LABEL_TO_STATUS.get(self.order_status)
        return self.order_status_raw


@dataclass
class WorkflowPosition:
    """
    工作流位置 - 根据页面快照推断出的工作流状态
    """
    order_no: str
    order_type: str                             # outbound / inbound
    current_state: str                          # 推断出的状态（英文）
    current_state_label: str                    # 状态中文标签

    available_actions: list[str] = field(default_factory=list)   # 可执行的操作
    forbidden_actions: list[str] = field(default_factory=list)   # 不应该出现的操作

    expected_next_states: list[str] = field(default_factory=list)  # 理论上应该能到达的状态

    actual_buttons_match: bool = True          # 实际按钮与预期是否匹配
    button_mismatches: list[str] = field(default_factory=list)  # 按钮不匹配详情

    def is_terminal(self) -> bool:
        """是否是终态"""
        return self.current_state in ("completed", "cancelled")

    def can_proceed_to(self, target_state: str) -> bool:
        """能否转换到目标状态"""
        transitions = WORKFLOW_TRANSITIONS.get(self.order_type, {})
        allowed = transitions.get(self.current_state, [])
        return target_state in allowed


@dataclass
class AnomalyReport:
    """
    异常报告 - 感知到的异常情况
    """
    anomaly_type: str                          # e.g. "api_500", "status_mismatch"
    severity: str                              # "critical" / "high" / "medium" / "low"

    description: str                           # 人类可读的异常描述
    evidence: dict = field(default_factory=dict)   # 证据：截图、API 响应等

    # 位置信息
    page_name: str = ""                         # 发生在哪个页面
    order_no: Optional[str] = None              # 关联的订单号

    # 初步诊断
    suspected_cause: str = ""                   # 初步判断的原因

    # 上下文
    expected_value: Any = None                  # 期望值
    actual_value: Any = None                   # 实际值

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "type": self.anomaly_type,
            "severity": self.severity,
            "description": self.description,
            "page": self.page_name,
            "order_no": self.order_no,
            "evidence": self.evidence,
            "suspected_cause": self.suspected_cause,
            "expected": self.expected_value,
            "actual": self.actual_value,
        }


@dataclass
class ConsistencyCheck:
    """
    一致性检查结果
    """
    check_name: str                             # 检查项名称
    passed: bool                                # 是否通过
    expected: Any                               # 期望值
    actual: Any                                 # 实际值
    details: str = ""                          # 详细说明

    order_no: Optional[str] = None             # 关联的订单号

    def to_dict(self) -> dict:
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "expected": self.expected,
            "actual": self.actual,
            "details": self.details,
            "order_no": self.order_no,
        }


@dataclass
class TestContext:
    """
    测试上下文 - 维护测试过程中的状态
    """
    # 当前用户
    current_user: str = ""
    current_role: str = ""
    current_org: str = ""

    # 当前订单
    current_order_no: Optional[str] = None
    current_order_status: Optional[str] = None
    current_order_type: Optional[str] = None

    # 最近的操作
    last_operation: Optional[str] = None       # 上一步执行了什么操作
    last_api_response: Optional[Any] = None    # 上一次 API 响应
    last_api_called: bool = False              # 上一步是否调用了 API

    # 操作历史（用于检测循环）
    operation_history: list[str] = field(default_factory=list)

    # 已发现的异常
    anomalies: list[AnomalyReport] = field(default_factory=list)

    # 已执行的一致性检查
    consistency_checks: list[ConsistencyCheck] = field(default_factory=list)

    def add_anomaly(self, anomaly: AnomalyReport):
        """添加异常"""
        self.anomalies.append(anomaly)

    def add_consistency_check(self, check: ConsistencyCheck):
        """添加一致性检查"""
        self.consistency_checks.append(check)

    def record_operation(self, operation: str):
        """记录操作"""
        self.last_operation = operation
        self.operation_history.append(operation)
        self.last_api_called = False
        self.last_api_response = None

    def record_api_call(self, response: Any):
        """记录 API 调用"""
        self.last_api_called = True
        self.last_api_response = response


class SensingError(Exception):
    """感知模块异常"""
    pass
