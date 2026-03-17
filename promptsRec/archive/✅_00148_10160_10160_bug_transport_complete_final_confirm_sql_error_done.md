# Bug Fix: transport-complete 和 final-confirm API 返回 SQL 语法错误

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10160
Goal: 修复 transport-complete 和 final-confirm API 返回 SQL 语法错误但操作实际成功的问题
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

E2E 测试报告 (test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260326_154000.md) 发现：

- **问题位置**: `/api/tool-io-orders/{no}/transport-complete` 和 `/api/tool-io-orders/{no}/final-confirm`
- **症状**: API 返回 SQL 语法错误 `"}" 附近有语法错误。(102)` 但操作实际完成成功
- **影响**: 客户端收到错误消息造成困惑，但工作流状态已正确更新

**Dev Inspector 分析**：
1. 错误 `"}"` 表明 ODBC 转义序列格式错误
2. 主操作成功，问题发生在后续查询
3. 在 `tool_io_service.py:1150` 发现乱码字段名（可能是相关编码问题的症状）

---

## Required References / 必需参考

1. `backend/services/tool_io_service.py` - `complete_transport` (line 519) 和 `final_confirm` (line 351)
2. `backend/services/tool_location_service.py` - `update_tool_location` (line 82) 和 `resolve_tool_master_location` (line 16)
3. `backend/database/schema/column_names.py` - 字段名常量
4. `database.py` - `final_confirm_order` (line 303)
5. `test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260326_154000.md` - 原始错误报告

---

## Core Task / 核心任务

诊断并修复 transport-complete 和 final-confirm API 返回 SQL 语法错误的问题。

**已知症状**：
- 操作实际成功完成（状态已更新）
- API 响应返回 SQL 错误
- 错误信息包含 `"}"` - ODBC 转义序列问题

**排查方向**：
1. 检查 `complete_transport` 函数中 `apply_order_location_updates` 调用的所有 SQL
2. 检查 `final_confirm` 函数中 `apply_order_location_updates` 调用的所有 SQL
3. 检查 `update_tool_location` 中的 SQL 字符串是否正确使用 f-string
4. 检查 `resolve_tool_master_location` 中的 SQL 字符串是否正确
5. 检查是否有其他地方在操作后执行查询

---

## Required Work / 必需工作

1. **语法检查**：
   ```powershell
   python -m py_compile backend/services/tool_io_service.py backend/services/tool_location_service.py database.py
   ```

2. **追踪 SQL 执行流程**：
   - 在 `complete_transport` 中追踪 `get_order_detail_runtime` 调用
   - 在 `final_confirm` 中追踪 `apply_order_location_updates` 调用
   - 确认每个 SQL 查询都正确使用 f-string 和参数化查询

3. **检查 `update_tool_location` SQL**：
   ```python
   # 检查是否有 f-string
   DatabaseManager().execute_query(
       f"""  # <-- 必须有 f 前缀！
       UPDATE [Tooling_ID_Main]
       SET [{TOOL_MASTER_COLUMNS['storage_location']}] = ?
       WHERE [{TOOL_MASTER_COLUMNS['tool_code']}] = ?
       """,
       (next_location, tool_code),
       fetch=False,
   )
   ```

4. **修复乱码问题**：
   - 检查 `tool_io_service.py:1150` 的乱码文本
   - 确认 `notify_transport` 函数的字段引用正确

5. **回归测试**：
   - 修复后使用测试用户执行完整的出库流程
   - 确认 transport-complete 和 final-confirm 不再返回 SQL 错误

---

## Constraints / 约束条件

- 只修复导致 SQL 错误的代码问题
- 不要改变 API 的业务逻辑或响应格式
- 保持操作的事务特性
- 使用 `column_names.py` 中的常量引用字段名

---

## Completion Criteria / 完成标准

1. `python -m py_compile` 所有修改的文件通过语法检查
2. transport-complete API 不再返回 SQL 错误
3. final-confirm API 不再返回 SQL 错误
4. 操作状态正确更新到数据库
5. 相关的 audit log 正确记录
