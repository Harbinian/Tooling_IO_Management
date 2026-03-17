# 工作流状态机测试 / Workflow State Machine Tests

Primary Executor: Codex
Task Type: Testing
Priority: P0
Stage: 301
Goal: Create comprehensive state machine transition tests for order workflow
Dependencies: None
Execution: RUNPROMPT

---

## Context

The workflow state machine is the core business logic of the system. Code review found that:
- `transport_start` allows entry from both `keeper_confirmed` and `transport_notified`, potentially skipping the notification step
- `final_confirm` allows entry from 3 different states, making transport effectively optional
- No automated tests verify these transition rules

Without tests, any future change to the state machine risks silent breakage.

## Required References

- `backend/services/tool_io_service.py` — state transition logic
- `AI_WORKFLOW_STATE_MACHINE.md` — documented state flow
- `tests/` — existing test patterns
- `backend/database/tool_io_queries.py` — database queries used by workflow

## Core Task

Write comprehensive pytest tests covering every valid and invalid state transition for both outbound (出库) and inbound (入库) order types.

## Required Work

1. Inspect `tool_io_service.py` to identify all state transition functions and their guard conditions
2. Create `tests/test_workflow_state_machine.py`
3. Test all VALID transitions for outbound flow:
   - draft → submitted → keeper_confirmed → transport_notified → transport_in_progress → transport_completed → final_confirmed → completed
4. Test all VALID transitions for inbound flow:
   - draft → submitted → keeper_confirmed → transport_notified → transport_in_progress → transport_completed → keeper_final_confirmed → completed
5. Test all INVALID transitions (should raise error or return failure):
   - draft → keeper_confirmed (skip submitted)
   - submitted → final_confirmed (skip middle steps)
   - completed → any state (terminal state)
   - rejected → any state (terminal state)
   - cancelled → any state (terminal state)
6. Test edge cases:
   - Can `transport_start` be called from `keeper_confirmed` directly? Document actual behavior.
   - Can `final_confirm` be called without transport completion? Document actual behavior.
7. Test role-based guards on transitions (e.g., only keeper can call keeper_confirm)

## Constraints

- Use pytest framework (consistent with existing tests)
- Use actual database if existing tests do so, or mock if that's the pattern
- Do NOT modify any production code
- Test file must be runnable with `pytest tests/test_workflow_state_machine.py -v`

## Acceptance Tests

- All valid transition paths pass
- All invalid transition attempts are properly rejected
- Edge cases are documented with comments explaining actual vs expected behavior
- Test output clearly shows which transitions are tested

## Completion Criteria

- [x] `tests/test_workflow_state_machine.py` created
- [x] All outbound valid transitions tested
- [x] All inbound valid transitions tested
- [x] At least 10 invalid transition cases tested
- [x] Edge cases for transport-skip and final-confirm-skip documented
- [x] All tests pass with `pytest -v`

---

## 后续工作 / Follow-up Work

### 2026-03-17 测试完成

测试文件已创建，包含 24 个测试用例:

1. **工作流状态定义验证** - 验证所有状态正确识别
2. **出库工作流路径** - 完整 8 步路径测试
3. **入库工作流路径** - 完整 8 步路径测试
4. **无效转换测试** - 验证跳过步骤被拒绝
5. **角色权限测试** - 验证基于角色的访问控制
6. **边界情况测试**:
   - transport_start 可从 keeper_confirmed 直接调用
   - final_confirm 可在未完成运输时调用（可选运输）
7. **运输跳过行为测试** - 记录可选的运输步骤
8. **API 端点映射** - 验证每个转换映射到正确的 API

测试结果: **24 passed**

### 边界情况发现

根据代码审查，发现以下潜在问题:

1. **transport_start 可以跳过 transport_notified**
   - 从 keeper_confirmed 可以直接开始运输，跳过通知步骤

2. **final_confirm 可以跳过运输完成**
   - 出库订单的 final_confirm 可以从 transport_notified 调用
   - 这意味着运输步骤实际上是可选的

这些发现需要在文档中明确说明，并考虑是否需要工作流修正。

## 验证更新 / Verification Update

- ✅ 测试文件创建完成
- ✅ 所有 24 个测试通过
- ✅ 边界情况已文档化
- ✅ 完成标准全部满足
