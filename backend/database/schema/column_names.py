# -*- coding: utf-8 -*-
"""
Unified column name constants for SQL queries.
This module centralizes all column names used in SQL queries to:
1. Prevent typos and encoding corruption
2. Enable global search and replace
3. Ensure consistency across all SQL statements

USAGE:
    from backend.database.schema.column_names import ORDER_COLUMNS, ITEM_COLUMNS

    # New English mode (recommended):
    sql = f"SELECT {ORDER_COLUMNS['order_no']} FROM tool_io_order"

    # Legacy Chinese mode (deprecated, for backward compatibility):
    sql = f"SELECT {ORDER_CHINESE_COLUMNS['order_no']} FROM 工装出入库单_主表"

DO NOT:
    - Use Chinese column names directly in SQL strings without using these constants
    - Copy-paste Chinese characters without using these constants
    - Use Unicode escapes like \\u5f5e instead of these constants
"""

# =============================================================================
# English table names (use these in SQL FROM clauses)
# =============================================================================
TABLE_NAMES = {
    'ORDER': 'tool_io_order',
    'ORDER_ITEM': 'tool_io_order_item',
    'ORDER_LOG': 'tool_io_operation_log',
    'ORDER_NOTIFICATION': 'tool_io_notification',
    'ORDER_LOCATION': 'tool_io_location',
    'TRANSPORT_ISSUE': 'tool_io_transport_issue',
    'MPL': 'tool_io_mpl',
    'SYSTEM_CONFIG': 'sys_system_config',
}

# =============================================================================
# 工装出入库单_主表 (ToolIOOrder) - English keys/values (recommended)
# =============================================================================
ORDER_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'order_type': 'order_type',
    'order_status': 'order_status',
    'initiator_id': 'initiator_id',
    'initiator_name': 'initiator_name',
    'initiator_role': 'initiator_role',
    'department': 'department',
    'project_code': 'project_code',
    'usage_purpose': 'usage_purpose',
    'planned_use_time': 'planned_use_time',
    'planned_return_time': 'planned_return_time',
    'target_location_id': 'target_location_id',
    'target_location_text': 'target_location_text',
    'keeper_id': 'keeper_id',
    'keeper_name': 'keeper_name',
    'transport_type': 'transport_type',
    'transport_operator_id': 'transport_operator_id',
    'transport_operator_name': 'transport_operator_name',
    # Aliases for transport_assignee_* used in API layer (maps to transport_operator_*)
    'transport_assignee_id': 'transport_operator_id',
    'transport_assignee_name': 'transport_operator_name',
    # Notification text fields (used in notify_transport)
    'transport_notify_text': 'transport_notify_text',
    'wechat_copy_text': 'wechat_copy_text',
    'keeper_confirm_time': 'keeper_confirm_time',
    'transport_notify_time': 'transport_notify_time',
    'final_confirm_time': 'final_confirm_time',
    'tool_quantity': 'tool_quantity',
    'confirmed_count': 'confirmed_count',
    'final_confirm_by': 'final_confirm_by',
    'reject_reason': 'reject_reason',
    'cancel_reason': 'cancel_reason',
    'remark': 'remark',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    'created_by': 'created_by',
    'updated_by': 'updated_by',
    'is_deleted': 'is_deleted',
    'org_id': 'org_id',
}

# =============================================================================
# Legacy Chinese column mappings (for backward compatibility with views)
# Deprecated: Use ORDER_COLUMNS with English table names instead
# =============================================================================
ORDER_CHINESE_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'order_type': 'order_type',
    'order_status': 'order_status',
    'initiator_id': 'initiator_id',
    'initiator_name': 'initiator_name',
    'initiator_role': 'initiator_role',
    'department': 'department',
    'project_code': 'project_code',
    'usage_purpose': 'usage_purpose',
    'planned_use_time': 'planned_use_time',
    'planned_return_time': 'planned_return_time',
    'target_location_id': 'target_location_id',
    'target_location_text': 'target_location_text',
    'keeper_id': 'keeper_id',
    'keeper_name': 'keeper_name',
    'transport_type': 'transport_type',
    'transport_operator_id': 'transport_operator_id',
    'transport_operator_name': 'transport_operator_name',
    'keeper_confirm_time': 'keeper_confirm_time',
    'transport_notify_time': 'transport_notify_time',
    'final_confirm_time': 'final_confirm_time',
    'tool_quantity': 'tool_quantity',
    'confirmed_count': 'confirmed_count',
    'final_confirm_by': 'final_confirm_by',
    'reject_reason': 'reject_reason',
    'cancel_reason': 'cancel_reason',
    'remark': 'remark',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    'created_by': 'created_by',
    'updated_by': 'updated_by',
    'is_deleted': 'is_deleted',
    'org_id': 'org_id',
}

# =============================================================================
# 工装出入库单_明细 (ToolIOOrderItem) - English keys/values (recommended)
# =============================================================================
ITEM_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'tool_id': 'tool_id',
    'serial_no': 'serial_no',
    'tool_name': 'tool_name',
    'drawing_no': 'drawing_no',
    'spec_model': 'spec_model',
    'apply_qty': 'apply_qty',
    'confirmed_qty': 'confirmed_qty',
    'item_status': 'item_status',
    'tool_snapshot_status': 'tool_snapshot_status',
    'tool_snapshot_location_id': 'tool_snapshot_location_id',
    'tool_snapshot_location_text': 'tool_snapshot_location_text',
    'keeper_confirm_location_id': 'keeper_confirm_location_id',
    'keeper_confirm_location_text': 'keeper_confirm_location_text',
    'keeper_check_result': 'keeper_check_result',
    'keeper_check_remark': 'keeper_check_remark',
    'return_check_result': 'return_check_result',
    'return_check_remark': 'return_check_remark',
    'confirm_time': 'confirm_time',
    'io_complete_time': 'io_complete_time',
    'sort_order': 'sort_order',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    'confirm_by': 'confirm_by',
    'confirm_by_id': 'confirm_by_id',
    'confirm_by_name': 'confirm_by_name',
    'reject_reason': 'reject_reason',
}

# =============================================================================
# Legacy Chinese column mappings (for backward compatibility)
# =============================================================================
ITEM_CHINESE_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'tool_id': 'tool_id',
    'serial_no': 'serial_no',
    'tool_name': 'tool_name',
    'drawing_no': 'drawing_no',
    'spec_model': 'spec_model',
    'apply_qty': 'apply_qty',
    'confirmed_qty': 'confirmed_qty',
    'item_status': 'item_status',
    'tool_snapshot_status': 'tool_snapshot_status',
    'tool_snapshot_location_id': 'tool_snapshot_location_id',
    'tool_snapshot_location_text': 'tool_snapshot_location_text',
    'keeper_confirm_location_id': 'keeper_confirm_location_id',
    'keeper_confirm_location_text': 'keeper_confirm_location_text',
    'keeper_check_result': 'keeper_check_result',
    'keeper_check_remark': 'keeper_check_remark',
    'return_check_result': 'return_check_result',
    'return_check_remark': 'return_check_remark',
    'confirm_time': 'confirm_time',
    'io_complete_time': 'io_complete_time',
    'sort_order': 'sort_order',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    'confirm_by': 'confirm_by',
    'confirm_by_id': 'confirm_by_id',
    'confirm_by_name': 'confirm_by_name',
    'reject_reason': 'reject_reason',
}

# =============================================================================
# 工装出入库单_操作日志 (ToolIOLog) - English keys/values (recommended)
# =============================================================================
LOG_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'item_id': 'item_id',
    'operation_type': 'operation_type',
    'operator_id': 'operator_id',
    'operator_name': 'operator_name',
    'operator_role': 'operator_role',
    'from_status': 'from_status',
    'to_status': 'to_status',
    'operation_content': 'operation_content',
    'operation_time': 'operation_time',
}

LOG_CHINESE_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'item_id': 'item_id',
    'operation_type': 'operation_type',
    'operator_id': 'operator_id',
    'operator_name': 'operator_name',
    'operator_role': 'operator_role',
    'from_status': 'from_status',
    'to_status': 'to_status',
    'operation_content': 'operation_content',
    'operation_time': 'operation_time',
}

# =============================================================================
# 工装出入库单_通知记录 (ToolIONotify) - English keys/values (recommended)
# =============================================================================
NOTIFY_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'notify_type': 'notify_type',
    'notify_channel': 'notify_channel',
    'receiver': 'receiver',
    'notify_title': 'notify_title',
    'notify_content': 'notify_content',
    'copy_text': 'copy_text',
    'send_status': 'send_status',
    'send_time': 'send_time',
    'send_result': 'send_result',
    'retry_count': 'retry_count',
    'created_at': 'created_at',
}

NOTIFY_CHINESE_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'notify_type': 'notify_type',
    'notify_channel': 'notify_channel',
    'receiver': 'receiver',
    'notify_title': 'notify_title',
    'notify_content': 'notify_content',
    'copy_text': 'copy_text',
    'send_status': 'send_status',
    'send_time': 'send_time',
    'send_result': 'send_result',
    'retry_count': 'retry_count',
    'created_at': 'created_at',
}

# =============================================================================
# 工装出入库单_位置 (ToolLocation) - English keys/values (recommended)
# =============================================================================
LOCATION_COLUMNS = {
    'id': 'id',
    'location_code': 'location_code',
    'location_name': 'location_name',
    'location_desc': 'location_desc',
    'warehouse_area': 'warehouse_area',
    'storage_slot': 'storage_slot',
    'shelf': 'shelf',
    'remark': 'remark',
}

LOCATION_CHINESE_COLUMNS = {
    'id': 'id',
    'location_code': 'location_code',
    'location_name': 'location_name',
    'location_desc': 'location_desc',
    'warehouse_area': 'warehouse_area',
    'storage_slot': 'storage_slot',
    'shelf': 'shelf',
    'remark': 'remark',
}

# =============================================================================
# 工装身份卡_主表 (Tool ID Card Master)
# EXTERNAL TABLE - DO NOT MODIFY THIS TABLE'S SCHEMA!
# This table belongs to an external system and is read-only.
# The Chinese column names MUST be used when querying this table.
# =============================================================================
TOOL_MASTER_TABLE = 'Tooling_ID_Main'

TOOL_MASTER_COLUMNS = {
    'tool_name': '工装名称',
    'drawing_no': '工装图号',
    'tool_code': '序列号',
    'original_tool_serial_no': '原样工装序列号',
    'manufacturing_date': '制造日期',
    'manufacturing_version': '制造版次',
    'manufacturing_dispatch_no': '制造派工号',
    'manufacturer': '制造商',
    'inspection_category': '定检属性',
    'inspection_cycle': '定检周期',
    'weight_kg': '重量kg',
    'lifting_ring': '配备吊环',
    'fork_hole': '配备叉孔',
    'tool_sketch': '工装简图',
    'cardboard': '卡板',
    'drill_jig': '钻模',
    'bushing': '衬套',
    'pin': '销钉',
    'bolt': '螺栓',
    'other': '其它',
    'cardboard_component_no': '卡板组件号',
    'drill_jig_component_no': '钻模组件号',
    'bushing_component_no': '衬套组件号',
    'pin_component_no': '销钉组件号',
    'bolt_component_no': '螺栓组件号',
    'other_detachable_component_no': '其他可拆卸件组件号',
    'prepared_by': '编制',
    'prepared_date': '编制日期',
    'checked_by': '校对',
    'checked_date': '校对日期',
    'excel_server_rcid': 'ExcelServerRCID',
    'excel_server_rn': 'ExcelServerRN',
    'excel_server_cn': 'ExcelServerCN',
    'excel_server_rc1': 'ExcelServerRC1',
    'excel_server_wiid': 'ExcelServerWIID',
    'excel_server_rtid': 'ExcelServerRTID',
    'excel_server_chg': 'ExcelServerCHG',
    'main_material': '主体材质',
    'storage_location': '库位',
    'main_length': '主体长度',
    'main_width': '主体宽度',
    'main_height': '主体高度',
    'split_quantity': '分体数量',
    'current_version': '当前版次',
    'inspection_expiry_date': '定检有效截止',
    'inspection_tech_requirement': '定检技术要求',
    'application_history': '应用历史',
    'storage_method': '封存方式',
    'available_status': '可用状态',
    'tech_info_complete': '工艺信息完善',
    'tech_info_complete_date': '工艺信息完善日期',
    'spec_model': '机型',
    'checker_opinion': '校对意见',
    'division_status': '分工状态',
    'controlled_tool': '受控工装',
    'product_drawing_no': '产品图号',
    'inspection_remaining_days': '定检有效期剩余天',
    'inspection_dispatch_status': '定检派工状态',
    'transcribed_inspection_record': '已转录定检记录',
    'transcribed_repair_record': '已转录返修记录',
    'set_no': '套数号',
    'change_order_no': '变更单编号',
    'general_type': '通用类型',
    'property_rights': '产权所有',
    'tool_valid_status': '工装有效状态',
    'work_package': '工作包',
    'io_status': '出入库状态',
}

# =============================================================================
# tool_status_change_history
# =============================================================================
TOOL_STATUS_HISTORY_COLUMNS = {
    'id': 'id',
    'serial_no': 'serial_no',
    'old_status': 'old_status',
    'new_status': 'new_status',
    'remark': 'remark',
    'operator_id': 'operator_id',
    'operator_name': 'operator_name',
    'change_time': 'change_time',
    'client_ip': 'client_ip',
}

# =============================================================================
# tool_io_feedback (already English)
# =============================================================================
FEEDBACK_COLUMNS = {
    'id': 'id',
    'category': 'category',
    'subject': 'subject',
    'content': 'content',
    'login_name': 'login_name',
    'user_name': 'user_name',
    'status': 'status',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
}

# =============================================================================
# tool_io_feedback_reply (already English)
# =============================================================================
FEEDBACK_REPLY_COLUMNS = {
    'id': 'id',
    'feedback_id': 'feedback_id',
    'reply_content': 'reply_content',
    'replier_login_name': 'replier_login_name',
    'replier_user_name': 'replier_user_name',
    'created_at': 'created_at',
}

# =============================================================================
# sys_org (already English)
# =============================================================================
ORG_COLUMNS = {
    'id': 'id',
    'org_id': 'org_id',
    'org_name': 'org_name',
    'org_code': 'org_code',
    'org_type': 'org_type',
    'parent_org_id': 'parent_org_id',
    'sort_no': 'sort_no',
    'status': 'status',
    'remark': 'remark',
    'created_at': 'created_at',
    'created_by': 'created_by',
    'updated_at': 'updated_at',
    'updated_by': 'updated_by',
}

# =============================================================================
# sys_user (already English)
# =============================================================================
SYS_USER_COLUMNS = {
    'id': 'id',
    'user_id': 'user_id',
    'login_name': 'login_name',
    'display_name': 'display_name',
    'password_hash': 'password_hash',
    'mobile': 'mobile',
    'email': 'email',
    'status': 'status',
    'default_org_id': 'default_org_id',
    'last_login_at': 'last_login_at',
    'remark': 'remark',
    'created_at': 'created_at',
    'created_by': 'created_by',
    'updated_at': 'updated_at',
    'updated_by': 'updated_by',
    'employee_no': 'employee_no',
}

# =============================================================================
# User Organization Relation (placeholder - table not found in DB)
# =============================================================================
USER_ORG_REL_COLUMNS = {
    'id': 'id',
    'user_id': 'user_id',
    'org_id': 'org_id',
    'is_primary': 'is_primary',
    'status': 'status',
    'created_at': 'created_at',
    'created_by': 'created_by',
    'updated_at': 'updated_at',
    'updated_by': 'updated_by',
}

# =============================================================================
# Password Change Log
# =============================================================================
PASSWORD_CHANGE_LOG_COLUMNS = {
    'id': 'id',
    'user_id': 'user_id',
    'changed_by': 'changed_by',
    'change_result': 'change_result',
    'remark': 'remark',
    'client_ip': 'client_ip',
    'changed_at': 'changed_at',
}

# =============================================================================
# 工装运输异常记录 (TransportIssue) - English keys/values (recommended)
# =============================================================================
TRANSPORT_ISSUE_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'issue_type': 'issue_type',
    'description': 'description',
    'image_urls': 'image_urls',
    'reporter_id': 'reporter_id',
    'reporter_name': 'reporter_name',
    'report_time': 'report_time',
    'status': 'status',
    'handler_id': 'handler_id',
    'handler_name': 'handler_name',
    'handle_time': 'handle_time',
    'handle_reply': 'handle_reply',
    'created_at': 'created_at',
}

TRANSPORT_ISSUE_CHINESE_COLUMNS = {
    'id': 'id',
    'order_no': 'order_no',
    'issue_type': 'issue_type',
    'description': 'description',
    'image_urls': 'image_urls',
    'reporter_id': 'reporter_id',
    'reporter_name': 'reporter_name',
    'report_time': 'report_time',
    'status': 'status',
    'handler_id': 'handler_id',
    'handler_name': 'handler_name',
    'handle_time': 'handle_time',
    'handle_reply': 'handle_reply',
    'created_at': 'created_at',
}

# =============================================================================
# tool_io_mpl
# =============================================================================
MPL_COLUMNS = {
    'id': 'id',
    'mpl_no': 'mpl_no',
    'tool_drawing_no': 'tool_drawing_no',
    'tool_revision': 'tool_revision',
    'component_no': 'component_no',
    'component_name': 'component_name',
    'quantity': 'quantity',
    'photo_data': 'photo_data',
    'created_by': 'created_by',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
}

# =============================================================================
# sys_system_config
# =============================================================================
SYSTEM_CONFIG_COLUMNS = {
    'config_key': 'config_key',
    'config_value': 'config_value',
    'description': 'description',
    'updated_by': 'updated_by',
    'updated_at': 'updated_at',
}
