# Bug Fix: 被拒绝的订单无法编辑和重新提交

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10161
Goal: 实现被拒绝订单的编辑和重新提交功能
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

E2E 测试报告 (test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260326_154000.md) 发现：

- **问题**: 订单被 keeper 拒绝后，team_leader 无法编辑和重新提交
- **当前行为**: 重新提交返回错误 "current status does not allow submit: rejected"
- **期望行为**: team_leader 应该能够编辑被拒绝的订单并重新提交

**工作流要求**：
- 被拒绝订单应允许状态转换：`rejected` -> `draft` 或 `rejected` -> `submitted`
- team_leader 应能够修改订单内容（工装列表、数量等）
- 修改后应允许重新提交

---

## Required References / 必需参考

1. `backend/routes/order_routes.py` - 现有订单端点
2. `backend/services/tool_io_service.py` - `submit_order`, `reject_order` 函数
3. `backend/database/repositories/order_repository.py` - 订单仓储
4. `docs/API_SPEC.md` - API 规范
5. `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵
6. `test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_20260326_154000.md` - 原始错误报告

---

## Core Task / 核心任务

实现被拒绝订单的重新提交功能。

**问题分析**：
1. 当前 `submit_order` 函数不允许 `rejected` 状态转换到 `submitted`
2. 缺少订单更新/编辑端点
3. 需要决定：是否允许直接重新提交，还是需要先编辑再提交

**建议方案**（二选一）：
- **方案 A**: 添加 `PUT /api/tool-io-orders/{order_no}` 更新端点，允许编辑订单内容并将状态改回 `draft`
- **方案 B**: 修改 `submit_order` 允许 `rejected` -> `submitted` 直接转换（如果业务允许）

---

## Required Work / 必需工作

1. **分析现有代码**：
   - 检查 `submit_order` 函数中的状态检查逻辑
   - 检查 `reject_order` 函数是否记录了拒绝原因
   - 确认订单状态机定义

2. **确定实现方案**：
   - 与架构文档对比确认正确的工作流
   - 确保权限检查正确（只有订单创建者/team_leader 可以编辑被拒绝订单）

3. **实现修改**：

   **方案 A（推荐）**：
   - 添加 `PUT /api/tool-io-orders/{order_no}` 端点
   - 允许更新订单内容和状态从 `rejected` 到 `draft`
   - 添加权限检查确保只有创建者可以编辑

   **方案 B**：
   - 修改 `submit_order` 状态转换规则
   - 允许 `rejected` -> `submitted` 转换
   - 添加 `reset_to_draft` 过渡状态

4. **更新权限矩阵**：
   - 如果添加新端点，更新 `docs/RBAC_PERMISSION_MATRIX.md`
   - 确保 `order:edit` 或 `order:update` 权限正确分配

5. **语法检查**：
   ```powershell
   python -m py_compile backend/services/tool_io_service.py backend/routes/order_routes.py
   ```

6. **E2E 测试验证**：
   - 创建订单 -> 提交 -> 拒绝 -> 编辑 -> 重新提交

---

## Constraints / 约束条件

- 不要破坏现有的其他状态转换
- 确保 RBAC 权限正确检查
- 使用 `column_names.py` 中的常量引用字段名
- 如果添加新 API，确保在 `docs/API_SPEC.md` 中记录

---

## Completion Criteria / 完成标准

1. 被拒绝订单可以被 team_leader 重新编辑
2. 编辑后订单状态变为 `draft` 或可以直接重新提交为 `submitted`
3. `python -m py_compile` 语法检查通过
4. 拒绝原因在编辑/重新提交后仍然可见（审计追踪）
5. RBAC 权限矩阵已更新（如添加新权限）
6. E2E 测试流程通过：创建 -> 提交 -> 拒绝 -> 编辑 -> 重新提交
