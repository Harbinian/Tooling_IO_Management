# 提示词任务编号约定 / Prompt Task Numbering Convention

---

## 目的 / Purpose

定义提示词文件的编号规则和归档命名格式。本规则替代 `docs/AI_DEVOPS_SYSTEM_ARCHITECTURE.md` 中的编号约定。

---

## 编号体系 / Numbering System

**统一使用5位类型编号，贯穿 active 和 archive 全流程：**

### active 目录格式

```
<类型编号>_<描述>.md
```

| 范围 | 类型 | 示例 |
|------|------|------|
| 00001-09999 | 功能任务 | `00017_order_list_ui_migration.md` |
| 10101-19999 | Bug修复任务 | `10101_bug_tool_search_routing.md` |
| 20101-29999 | 重构任务 | `20101_refactor_split_tool_io_service.md` |
| 30101-39999 | 测试任务 | `30101_workflow_state_machine_tests.md` |

### archive 目录格式

```
✅_<执行顺序号>_<类型编号>_<描述>_done.md
```

| 字段 | 说明 | 示例 |
|------|------|------|
| `✅_` | 完成标记 | `✅_` |
| 执行顺序号 | 00001-00113，按执行顺序自增 | `00001`, `00015`, `00113` |
| 类型编号 | 与 active 目录一致 | `00017`, `10101`, `20101` |
| 描述 | 任务描述（下划线分隔） | `order_list_ui_migration` |
| `_done.md` | 固定后缀 | `_done.md` |

---

## 类型编号范围 / Type Number Ranges

| 类型编号范围 | 类型 | 说明 |
|-------------|------|------|
| `00001-09999` | 功能任务 | 功能开发、UI迁移等 |
| `10101-19999` | Bug修复任务 | Bug修复 |
| `20101-29999` | 重构任务 | 代码重构 |
| `30101-39999` | 测试任务 | 自动化测试 |

---

## 类型编号分配规则 / Type Number Allocation Rules

### 功能任务 (00001-09999)

功能任务按类型内顺序自增分配：

| 执行顺序号 | 类型编号 | 示例 |
|-----------|----------|------|
| 00001 | 00001 | `✅_00001_00001_bootstrap_project_pipeline_done.md` |
| 00002 | 00002 | `✅_00002_00002_first_phase_sqlserver_done.md` |
| 00003 | 00003 | `✅_00003_00003_technical_design_done.md` |
| ... | ... | ... |

### Bug修复任务 (10101-19999)

Bug任务按发现顺序自增分配（101开头）：

| 执行顺序号 | 类型编号 | 示例 |
|-----------|----------|------|
| 00015 | 10101 | `✅_00015_10101_bug_tool_search_routing_done.md` |
| 00016 | 10102 | `✅_00016_10102_bug_vite_entry_compile_done.md` |
| 00029 | 10105 | `✅_00029_10105_bug_transport_notification_done.md` |
| ... | ... | ... |

### 重构任务 (20101-29999)

重构任务按执行顺序自增分配（201开头）：

| 执行顺序号 | 类型编号 | 示例 |
|-----------|----------|------|
| 00067 | 20101 | `✅_00067_20101_refactor_resolve_ui_library_conflict_done.md` |
| 00072 | 20102 | `✅_00072_20102_refactor_split_tool_io_service_done.md` |
| ... | ... | ... |

### 测试任务 (30101-39999)

测试任务按执行顺序自增分配（301开头）：

| 执行顺序号 | 类型编号 | 示例 |
|-----------|----------|------|
| 00073 | 30101 | `✅_00073_30101_workflow_state_machine_tests_done.md` |
| 00074 | 30102 | `✅_00074_30102_rbac_permission_enforcement_tests_done.md` |

---

## 归档命名格式 / Archive Naming Format

### 标准格式

```
✅_<执行顺序号>_<类型编号>_<描述>_done.md
```

### 格式字段说明

| 字段 | 位置 | 说明 |
|------|------|------|
| `✅_` | 前缀 | 完成标记 |
| `<执行顺序号>` | 第1个5位 | 执行顺序，自增 |
| `<类型编号>` | 第2个5位 | 与 active 目录一致 |
| `<描述>` | 变长 | 任务描述（下划线分隔） |
| `_done.md` | 后缀 | 固定后缀 |

### 示例

```
✅_00001_00001_bootstrap_project_pipeline_done.md
✅_00015_10101_bug_tool_search_routing_done.md
✅_00067_20101_refactor_resolve_ui_library_conflict_done.md
✅_00073_30101_workflow_state_machine_tests_done.md
```

---

## 禁止事项 / Prohibitions

1. **禁止重复执行顺序号**：每个归档文件必须有唯一的执行顺序号
2. **禁止缺少后缀**：所有归档文件必须包含 `_done.md` 后缀
3. **禁止使用3位编号**：active 和 archive 目录统一使用5位类型编号

---

## 编号对照表 / Number Reference Table

### 功能任务

| 执行顺序号 | 类型编号 | 描述 |
|-----------|----------|------|
| 00001 | 00001 | bootstrap_project_pipeline |
| 00002 | 00002 | first_phase_sqlserver |
| 00003 | 00003 | technical_design |
| 00004 | 00004 | sqlserver_schema_revision |
| 00005 | 00005 | fix_database_schema |
| 00006 | 00006 | backend_implementation |
| 00007 | 00007 | backend_review |
| 00008 | 00008 | frontend_design |
| 00009 | 00009 | frontend_implementation |
| 00010 | 00010 | release_precheck |
| 00011 | 00011 | tool_search_dialog |
| 00012 | 00012 | tool_master_field_audit |
| 00013 | 00013 | database_settings_compatibility |
| 00014 | 00014 | submit_order_workflow |
| 00015 | 00015 | keeper_confirmation_workflow |
| 00016 | 00016 | frontend_style_migration |
| 00017 | 00017 | frontend_ui_system_migration |
| 00018 | 00018 | order_list_ui_migration |
| 00019 | 00019 | order_detail_ui_migration |
| 00020 | 00020 | keeper_process_ui_migration |
| 00021 | 00021 | order_create_ui_migration |
| 00022 | 00022 | structured_message_preview_ui |
| 00023 | 00023 | final_confirmation_workflow |
| 00024 | 00024 | notification_record_usage |
| 00025 | 00025 | feishu_integration |
| 00026 | 00026 | pipeline_dashboard_upgrade |
| 00027 | 00027 | create_architecture_index |
| 00028 | 00028 | 028 | user_authentication_system |
| 00029 | 00029 | 029 | organization_structure_module |
| 00030 | 00030 | 030 | rbac_permission_enforcement |
| 00031 | 00031 | 031 | frontend_permission_visibility |
| 00032 | 00032 | 032 | org_scoped_order_data_access |
| 00033 | 00033 | 033 | login_page_auth_flow_ui |
| 00034 | 00034 | 034 | end_to_end_rbac_workflow_validation |
| 00035 | 00035 | 035 | review_reports_and_fix_tasks |
| 00036 | 00036 | 036 | refactor_backend_core_files |
| 00037 | 00037 | 046 | trae_ignore_token_optimization |
| 00038 | 00038 | 037 | api_contract_snapshot_and_regression_baseline |
| 00039 | 00039 | 038 | operation_audit_log_system |
| 00040 | 00040 | 044 | release_preparation_and_go_live_checklist |
| 00041 | 00041 | 039 | notification_service_framework |
| 00042 | 00042 | 045 | system_observability_and_runtime_monitoring |
| 00043 | 00043 | 040 | feishu_notification_adapter |
| 00044 | 00044 | 047 | bug_sweep_and_stability_pass |
| 00045 | 00045 | 041 | transport_workflow_state |
| 00046 | 00046 | 048 | repo_weight_analysis_script |
| 00047 | 00047 | 042 | tool_location_management |
| 00048 | 00048 | 043 | dashboard_real_time_metrics |
| 00049 | 00049 | 049 | safe_repo_context_slimming |
| 00050 | 00050 | 050 | frontend_debug_id_overlay_admin_only_enhanced |
| 00051 | 00051 | 051 | order_create_dynamic_fields |
| 00052 | 00052 | 052 | rbac_role_assignment_and_account_admin_page |
| 00053 | 00053 | 055 | unify_frontend_api_layer |
| 00054 | 00054 | 053 | tool_locking_mechanism |
| 00055 | 00055 | 054 | generate_ai_auditable_codebase_documentation |
| 00056 | 00056 | 056 | backend_admin_order_delete_cascade |
| 00057 | 00057 | 057 | frontend_order_detail_delete_button |
| 00058 | 00058 | 058 | password_change_backend |
| 00059 | 00059 | 059 | feedback_persistence_backend |
| 00060 | 00060 | 060 | dark_mode_css_support |
| 00061 | 00061 | 063 | admin_feedback_management_backend |
| 00062 | 00062 | 064 | admin_feedback_management_frontend |
| 00063 | 00063 | 082 | keeper_batch_tool_status_backend |
| 00064 | 00064 | 083 | keeper_batch_tool_status_frontend |
| 00065 | 00065 | 110 | bug_keeper_cannot_see_submitted_orders |
| 00066 | 00066 | 111 | bug_login_500_on_first_attempt |
| 00067 | 00067 | 131 | dev_server_launcher_gui |

### Bug修复任务

| 执行顺序号 | 类型编号 | 描述 |
|-----------|----------|---------|------|
| 00015 | 10101 | 101 | bug_tool_search_routing |
| 00016 | 10102 | 102 | bug_vite_entry_compile |
| 00017 | 10103 | 103 | bug_order_list_api_500 |
| 00018 | 10104 | 104 | bug_workflow_followup |
| 00029 | 10105 | 105 | bug_transport_notification |
| 00032 | 10106 | 106 | bug_duplicate_sidebar_layout |
| 00043 | 10107 | 107 | bug_rbac_data_scope_violation |
| 00044 | 10108 | 108 | bug_order_missing_org_ownership |
| 00045 | 10109 | 109 | bug_archive_sequence_collision |
| 00058 | 10110 | 110 | bug_blank_main_pages_after_auth_layout_integration |
| 00062 | 10111 | 111 | bug_tool_search_spec_field_mapping |
| 00063 | 10112 | 112 | bug_debug_id_overlay_missing_on_dialog_inner_elements |
| 00068 | 10113 | 113 | bug_frontend_english_locale |
| 00070 | 10114 | 114 | bug_transport_role_permission_gap |
| 00071 | 10115 | 115 | fix_order_detail_missing_fields |
| 00076 | 10116 | 116 | bug_database_refactor_regression_cleanup |
| 00077 | 10117 | 117 | bug_order_api_parameter_mismatch |
| 00078 | 10118 | 118 | bug_rbac_team_leader_order_view_permission |
| 00081 | 10119 | 119 | bug_admin_delete_order_403 |
| 00082 | 10120 | 120 | bug_notification_records_api_500 |
| 00083 | 10121 | 121 | fix_transport_preview_400_error |
| 00084 | 10122 | 122 | fix_org_id_schema_missing |
| 00088 | 10123 | 123 | bug_settings_chinese_encoding |
| 00090 | 10124 | 124 | bug_textarea_rows_prop |
| 00091 | 10125 | 125 | bug_hardcoded_role_checks_order_detail |
| 00094 | 10126 | 127 | bug_scrollbar_hardcoded_colors |
| 00095 | 10127 | 128 | fix_order_list_multiple_ui_issues |
| 00096 | 10128 | 129 | bug_theme_toggle_system_sync |
| 00098 | 10129 | 126 | bug_keeper_notification_permission_gap |
| 00099 | 10130 | 131 | bug_submit_confirmation_dialog_order_detail |
| 00100 | 10131 | 132 | bug_keeper_batch_status_payload_mismatch |
| 00102 | 10132 | 130 | bug_order_api_missing_tool_count_fields |
| 00103 | 10133 | 133 | bug_password_validation_policy_mismatch |
| 00107 | 10134 | 131 | bug_ordercreate_vue_encoding_corruption |
| 00109 | 10135 | 110 | bug_keeper_cannot_see_submitted_orders |
| 00110 | 10136 | 111 | bug_login_500_on_first_attempt |
| 00111 | 10137 | 131 | bug_order_create_400_encoding_corruption |
| 00112 | 10138 | 131 | bug_sql_field_name_mismatch |

### 重构任务

| 执行顺序号 | 类型编号 | 描述 |
|-----------|----------|---------|------|
| 00067 | 20101 | 202 | refactor_resolve_ui_library_conflict |
| 00072 | 20102 | 201 | refactor_split_tool_io_service |
| 00075 | 20103 | 201 | refactor_database_module_split |
| 00089 | 20104 | 203 | refactor_repo_chinese_copy_encoding_normalization |
| 00101 | 20105 | 204 | refactor_inline_workflow_stepper |
| 00097 | 20106 | 205 | fix_outdated_docs_framework_and_states |

### 测试任务

| 执行顺序号 | 类型编号 | 描述 |
|-----------|----------|---------|------|
| 00073 | 30101 | 301 | workflow_state_machine_tests |
| 00074 | 30102 | 302 | rbac_permission_enforcement_tests |

---

## 10 执行者分配规则 / Executor Assignment Rules

### 10.1 统一执行规则 / Unified Execution Rule

为提升自动化效率，除非任务涉及以下情况，否则统一由 Claude Code 执行：

| 任务类型 | 例外条件 | 执行者 |
|---------|---------|--------|
| 功能任务 (00001-09999) | 前端设计大改 | Claude Code |
| Bug 修复 (10001-19999) | P0/P1 恶性bug | Claude Code |
| 重构任务 (20001-29999) | 始终 | Claude Code |
| 测试任务 (30001-39999) | 始终 | Claude Code |

### 10.2 简化任务标准 / Simple Task Criteria

以下任务视为"简化任务"，由 Claude Code 直接执行：

1. **参数问题**：类型不匹配、参数传递错误
2. **调用错误**：函数/方法调用参数提取不正确
3. **签名修正**：函数签名与实现不一致
4. **文档更新**：docstring、注释同步
5. **单点修复**：不涉及架构变更的单文件/单函数修改

### 10.3 恶性 Bug 定义 / Malignant Bug Definition

以下情况视为"恶性 Bug"：
- P0 级别：系统无法运行、数据损坏风险
- P1 级别：核心功能损坏、API 不可用、工作流阻塞

### 10.4 简化任务示例 / Simple Task Examples

| 任务类型 | 示例 |
|---------|------|
| 参数不匹配 | `location: Optional[str]` 传给了 `location_id: int` 参数 |
| 调用错误 | `search_tools(filters)` 传字典但函数期望关键字参数 |
| 签名修正 | 函数定义与调用方式不一致 |
| 文档同步 | docstring 未反映新增参数 |
