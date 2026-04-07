# 测试任务规范 / Testing Task Protocol

---

## 目的 / Purpose

本规则为测试任务（30101-39999）定义标准化开发流程，确保测试质量、覆盖率和可维护性。

---

## 原则 / Principles

- **测试驱动开发 (TDD)**: 复杂逻辑先写测试，脱离 UI 验证
- **零假设验证**: 见 `00_core.md` — Zero-Assumption Policy。
- **可执行可重现**: 测试必须可重复执行，结果稳定

---

## 测试任务分类 / Test Task Categories

| 类型 | 描述 | 示例 |
|------|------|------|
| 单元测试 | 验证独立函数/方法 | `test_workflow_state_machine.py` |
| 集成测试 | 验证模块间交互 | API 与数据库集成 |
| E2E 测试 | 端到端用户流程 | `playwright_e2e.py` |
| 回归测试 | 防止已有功能破坏 | Bug 修复后的验证测试 |

---

## 测试任务章节 / Test Task Sections

### 1. Test Scope - 测试范围

必须包含：
- **测试目标**: 要验证什么
- **测试环境**: 数据库、API、网络要求
- **依赖项**: 被测试的代码文件

### 2. Test Strategy - 测试策略

必须包含：
- **测试类型**: 单元/集成/E2E
- **测试数据**: 如何准备测试数据
- **Mock/Stub 策略**: 是否使用 mock，如何使用

### 3. Test Cases - 测试用例

必须使用表格格式：

| ID | 场景 | 前置条件 | 操作 | 期望结果 | 优先级 |
|----|------|---------|------|---------|--------|
| T1 | 正常流程 | X | 执行 Y | 期望 Z | P0 |
| T2 | 异常流程 | A | 执行 B | 期望 C | P1 |

**优先级定义**：
- P0: 核心功能，必须通过
- P1: 重要功能，建议通过
- P2: 边界情况，辅助验证

### 4. Pass Criteria - 通过标准

必须包含：
- 最低覆盖率要求（如适用）
- 所有 P0 测试用例通过
- 无回归（现有测试不受影响）

### 覆盖率最低要求 / Minimum Coverage Requirements

| 测试类型 | 最低覆盖率 | 说明 |
|---------|-----------|------|
| 单元测试 | ≥ 80% | 针对新增/修改代码行 |
| 集成测试 | ≥ 60% | 针对模块间接口 |
| E2E 测试 | 覆盖全部 P0 路径 | 无覆盖率百分比要求 |

### 5. Test Artifacts - 测试产物

必须记录：
- 测试报告路径
- 覆盖率报告路径
- 日志输出位置

---

## Headless TDD 要求 / Headless TDD Requirements

对于后端复杂逻辑（状态机、工作流），必须先写单元测试：

```
1. 编写单元测试
2. 运行测试（预期失败）
3. 实现被测代码
4. 运行测试（预期通过）
5. 重构（如需要）
6. 重复
```

**禁止**：
- 先写实现后写测试（除非测试是回归防护）
- 不运行测试就声称通过
- Mock 真实数据库（集成测试除外）

---

## 测试代码规范 / Test Code Standards

### Python (pytest)

```python
import pytest
from backend.services.tool_io_service import submit_order

class TestWorkflowStateMachine:
    """工作流状态机测试套件"""

    @pytest.fixture
    def mock_db_connection(self):
        """数据库 mock fixture"""
        # setup
        yield connection
        # teardown

    def test_draft_to_submitted_transition(self, mock_db_connection):
        """出库草稿→已提交转换"""
        # Arrange
        order = create_test_order(status="draft")
        # Act
        result = submit_order(order.order_no)
        # Assert
        assert result.status == "submitted"

    @pytest.mark.parametrize("invalid_status", [
        "submitted",
        "keeper_confirmed",
        "completed"
    ])
    def test_draft_cannot_skip_to_final_confirm(self, invalid_status):
        """草稿不能跳过步骤直接最终确认"""
        # ...
```

### JavaScript (Vitest)

```javascript
import { describe, it, expect, vi } from 'vitest'

describe('Order Workflow', () => {
  it('should transition from draft to submitted', async () => {
    const order = createTestOrder({ status: 'draft' })
    const result = await submitOrder(order.orderNo)
    expect(result.status).toBe('submitted')
  })
})
```

---

## 约束条件 / Constraints

1. **不修改生产代码**: 测试文件不得修改被测代码
2. **独立性**: 每个测试用例必须独立，不依赖其他测试
3. **可重复**: 测试必须可重复执行，结果一致
4. **清晰的断言**: 断言消息必须描述期望行为
5. **UTF-8 编码**: 所有测试文件必须 UTF-8 编码

---

## 验证流程 / Verification Flow

| 阶段 | 内容 | 产出 |
|------|------|------|
| Test Scope | 定义测试边界 | 测试计划 |
| Test Strategy | 选择测试策略 | 策略文档 |
| Test Implementation | 编写测试代码 | 测试文件 |
| Test Execution | 运行测试 | 测试报告 |
| Coverage Analysis | 分析覆盖率 | 覆盖率报告 |

---

## 完成标准 / Completion Criteria

每个测试任务必须满足：

- [ ] 测试文件已创建（如 `tests/test_*.py`）
- [ ] 所有 P0 测试用例通过
- [ ] 关键路径有覆盖率记录
- [ ] 测试报告已生成
- [ ] 无新的回归（现有测试仍通过）

---

## 与其他规则的关系 / Relationship with Other Rules

| 规则 | 关系 |
|------|------|
| `01_workflow.md` | Phase 4 中的 Headless TDD 引用本规则 |
| `02_debug.md` | Bug 修复中的测试验证部分引用本规则 |
| `05_task_convention.md` | 编号范围 30101-39999 使用本规则 |

