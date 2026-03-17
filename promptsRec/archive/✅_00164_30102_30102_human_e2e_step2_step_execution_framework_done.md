# Human E2E 8分达标 - 步骤2：固化步骤执行框架

## 任务编号
- **执行顺序号**: 00163
- **类型编号**: 30102
- **任务类型**: 测试任务

## 任务目标
统一步骤函数 `before -> action -> after -> advance` 模式，至少5个关键步骤接入。

## 修改范围
仅限以下文件：
- `test_runner/api_e2e.py`

## 前置依赖
- 步骤1（30101）必须已完成并验收通过

## 步骤2 具体修改要求

### 2.1 定义步骤执行框架
在 `api_e2e.py` 中实现统一的步骤函数模式：

```python
def execute_step(step_name: str, before_action: callable, action: callable,
                 after_action: callable, expected_next_state: str = None):
    """
    统一步骤执行框架: before -> action -> after -> advance

    Args:
        step_name: 步骤名称
        before_action: 执行前的准备操作（如快照）
        action: 主要操作
        after_action: 执行后的验证操作
        expected_next_state: 期望的下一步状态
    """
    # before
    before_snapshot = before_action() if before_action else None

    # action
    result = action()

    # after
    after_snapshot = after_action() if after_action else None

    # advance - 推进 agent 状态
    advance(step_name, anomalies_count=0, critical_count=0)

    return result
```

### 2.2 接入关键步骤（至少5个）
为以下步骤实现统一的 `execute_step` 模式：

1. `login` - 登录操作
2. `create_order` - 创建订单
3. `submit_order` - 提交订单
4. `keeper_confirm` - 保管员确认
5. `transport_execute` - 运输执行
6. `final_confirm` - 最终确认

### 2.3 语法检查
```powershell
python -m py_compile test_runner/api_e2e.py
```

### 2.4 验证命令
```bash
# 启动测试并检查步骤接入
python test_runner/test_runner_agent.py --command start --test-type quick_smoke
python test_runner/test_runner_agent.py --command status
python test_runner/test_runner_agent.py --command stop --reason "step2-check"
```

## 约束
- 不得顺手改其他步骤（步骤1、3-10）的内容
- 只做最小改动，聚焦于步骤框架统一

## 输出要求
1. 代码改动清单
2. 验证命令执行结果
3. 接入 `execute_step` 的步骤列表
4. 风险评估
5. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP2_REPORT_YYYYMMDD_HHMMSS.md`
