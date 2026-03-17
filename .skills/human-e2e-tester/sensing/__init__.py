# -*- coding: utf-8 -*-
"""
Human E2E Tester - 感知模块

拟人 E2E 测试的核心感知框架，赋予测试者"眼睛"和"判断力"。

核心组件：
- snapshot: 核心数据结构定义
- page_observer: 页面感知层
- workflow_detector: 工作流感知层
- anomaly_detector: 异常感知层
- consistency_verifier: 数据一致性验证层
"""

from .snapshot import (
    PageSnapshot,
    WorkflowPosition,
    AnomalyReport,
    ConsistencyCheck,
    TestContext,
    Severity,
    AnomalyType,
    STATUS_LABEL_MAP,
    WORKFLOW_TRANSITIONS,
)

from .page_observer import (
    sense_page,
    detect_page_type,
    extract_order_no_from_url,
)

from .workflow_detector import (
    detect_workflow_position,
    detect_workflow_anomalies,
    detect_illegal_transition,
)

from .anomaly_detector import (
    detect_all_anomalies,
    ANOMALY_PATTERNS,
)

from .consistency_verifier import (
    verify_all_consistency,
    verify_list_detail_consistency,
    verify_tool_quantity_logic,
    verify_rejection_reason,
)

from .storage import (
    SQLiteStorage,
    TestRun,
    Checkpoint,
    get_db_path,
)


__all__ = [
    # 核心数据结构
    "PageSnapshot",
    "WorkflowPosition",
    "AnomalyReport",
    "ConsistencyCheck",
    "TestContext",
    "Severity",
    "AnomalyType",

    # 感知函数
    "sense_page",
    "detect_page_type",
    "extract_order_no_from_url",

    # 工作流感知
    "detect_workflow_position",
    "detect_workflow_anomalies",
    "detect_illegal_transition",

    # 异常检测
    "detect_all_anomalies",
    "ANOMALY_PATTERNS",

    # 数据一致性
    "verify_all_consistency",
    "verify_list_detail_consistency",
    "verify_tool_quantity_logic",
    "verify_rejection_reason",

    # 协调器
    "SensingOrchestrator",

    # 存储层
    "SQLiteStorage",
    "TestRun",
    "Checkpoint",
    "get_db_path",

    # 常量
    "STATUS_LABEL_MAP",
    "WORKFLOW_TRANSITIONS",
]
