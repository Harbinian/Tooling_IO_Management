# 事件监控报告 / Incident Monitor Report

## 扫描摘要 / Scan Summary

- **时间**: 2026-04-02
- **检查的来源**:
  - `incidents/` - 现有事件文件
  - `logs/prompt_task_runs/` - 最新任务执行报告
  - `logs/codex_rectification/` - 最新纠正日志
  - `incidents/gui_events/` - GUI 事件目录
- **新候选事件**: 1
- **现有类似事件**: 0
- **建议**: 运行 incident-capture

---

## 候选事件 / Candidate Incidents

### 1. serial_no 列名错误导致订单创建失败

**摘要**:
`serial_no` 列名在查询外部系统表 `Tooling_ID_Main` 时无效，导致工装查询失败，进而阻止订单创建。

**受影响区域**:
Backend - Database / API Layer

**严重性建议**:
**High** (核心功能不可用，出库/入库工作流受阻)

**证据**:
```
'error': '(\'42S22\', "[Microsoft][ODBC SQL Server Driver][SQL Server]���� \'serial_no\' ��Ч�� (207)"
```

**根因初步分析**:
- `tool_io_service.py` 中的 `load_tool_master_map` 或 `check_tools_available` 函数
- 查询 `Tooling_ID_Main` 表时使用了 `serial_no` 列名
- 该表的实际列名是 `工装编号` (通过 `TOOL_MASTER_COLUMNS['tool_code']` 引用)
- 根据 `column_names.py`，`serial_no` 应映射到 `tool_io_order_item` 表，而非 `Tooling_ID_Main`

**观察到的行为**:
- 用户尝试创建订单时 API 返回 400 错误
- 错误信息: `[42S22] invalid column name 'serial_no'`

**预期行为**:
- 订单创建应成功，工装主数据查询应使用正确的列名

**建议的下一步操作**:
1. 运行 `incident-capture` 捕获此事件
2. 检查 `tool_io_service.py` 中所有查询 `Tooling_ID_Main` 的函数
3. 确保使用 `TOOL_MASTER_COLUMNS['tool_code']` 而非 `serial_no`

---

## 重复或现有事件 / Duplicate or Existing Incidents

- **现有事件文件**: `incidents/INCIDENT_20260317_117_order_api_500.md`
- **被视为重复的原因**: 该事件是 API 500 错误，已解决；当前问题是 API 400 错误（列名错误），根因不同

---

## 最终建议 / Final Recommendation

**运行 incident-capture** 捕获 `serial_no` 列名错误事件。

此问题阻塞了订单创建功能，属于 High 严重性，需要在下次发布前修复。
