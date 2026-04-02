Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 10187
Goal: Fix test scripts so inbound workflow final confirm uses KEEPER role, not TEAM_LEADER
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 发现的问题

通过检查 `test_runner/api_e2e.py`、`test_runner/playwright_e2e.py` 和 `docs/PRD.md`，发现测试脚本与实际业务逻辑存在以下不一致：

#### 问题 1: 入库最终确认角色错误（核心 Bug）

**文件**: `test_runner/api_e2e.py`

在 `step_final_confirm()` 函数中，最终确认的角色由调用者传入，没有根据订单类型（出库/入库）区分：

```python
def step_final_confirm(order_no: str, token: str, user_id: int,
                        operator_role: str, orchestrator=None):
    return api_post(f"/tool-io-orders/{order_no}/final-confirm", {
        "operator_role": operator_role  # 传入什么就是什么
    })
```

**PRD 规定**（`docs/PRD.md` 第 3.2 节）:
- 出库完成条件：班组长点击"确认收到"按钮
- 入库完成条件：**保管员点击"确认入库"按钮**

**实际业务**：入库最终确认必须由 KEEPER 角色完成，不是 TEAM_LEADER。

#### 问题 2: 入库工作流测试缺失

`test_runner/api_e2e.py` 的 `run_full_workflow_test()` 函数只有出库工作流测试（`run_outbound_workflow_test`），**没有入库工作流测试**。

根据 PRD 第 3.2 节，入库流程与出库流程的关键区别在于：
- 出库：TEAM_LEADER 最终确认
- 入库：**KEEPER 最终确认**

---

## Required References / 必需参考

- `docs/PRD.md` - 产品需求文档，特别是第 3.1（出库流程）、3.2（入库流程）、4（完成条件）节
- `docs/API_SPEC.md` - API 规范，/final-confirm 端点说明
- `backend/services/tool_io_service.py` - 最终确认服务逻辑
- `backend/routes/order_routes.py` - /final-confirm 路由实现
- `test_runner/api_e2e.py` - 需要修复的测试脚本
- `test_runner/playwright_e2e.py` - Playwright E2E 测试脚本

---

## Core Task / 核心任务

### 修复 api_e2e.py 的入库最终确认 Bug

1. 在 `step_final_confirm()` 函数中增加订单类型判断
2. 出库订单：使用 TEAM_LEADER 角色
3. 入库订单：**必须使用 KEEPER 角色**
4. 确保 `run_inbound_workflow_test()` 正确使用 keeper token 进行最终确认

### 确保测试数据隔离

- 入库工作流测试使用 `order_type: "inbound"`
- 清理逻辑需要正确处理入库订单

---

## Required Work / 必需工作

### Step 1: 检查代码实现

在动手修改前，必须验证：

1. 读取 `backend/routes/order_routes.py` 中 `/final-confirm` 路由实现
2. 读取 `backend/services/tool_io_service.py` 中最终确认逻辑
3. 确认是否在后端已经做了角色校验（可能后端已经校验了 keeper 角色但测试没反映）

### Step 2: 修复 api_e2e.py

#### 2.1 修改 step_final_confirm 函数签名

增加 `order_type` 参数，根据订单类型决定最终确认角色：

```python
def step_final_confirm(order_no: str, token: str, user_id: int,
                        operator_role: str, order_type: str = "outbound",
                        orchestrator=None) -> tuple:
    """
    步骤: final_confirm - 最终确认

    Args:
        order_type: "outbound" 或 "inbound"
        - outbound: TEAM_LEADER 最终确认
        - inbound: KEEPER 最终确认
    """
```

#### 2.2 添加角色验证逻辑

```python
# 入库必须由 KEEPER 最终确认
if order_type == "inbound":
    expected_role = "keeper"
    if operator_role.lower() != "keeper":
        # 记录警告但仍然执行（以后端校验为准）
        print(f"[WARN] Inbound final_confirm should use KEEPER role, got {operator_role}")
```

#### 2.3 创建 run_inbound_workflow_test 函数

参考现有的 `run_outbound_workflow_test()`，创建入库工作流测试：

```
入库流程:
1. 太东旭创建入库订单 (order_type=inbound)
2. 太东旭提交订单
3. 胡婷婷(KEEPER)确认工装明细
4. 胡婷婷发送运输通知 (notify_transport)
5. 冯亮(PRODUCTION_PREP)开始运输
6. 冯亮完成运输
7. 胡婷婷(KEEPER)最终确认 ← 关键差异
```

### Step 3: 验证修复

语法检查：
```powershell
python -m py_compile test_runner/api_e2e.py
```

### Step 4: 更新 playwright_e2e.py（如有必要）

如果 Playwright 测试中也涉及最终确认，需要同步修改。

---

## Constraints / 约束条件

1. **禁止修改后端业务逻辑**：本次只修复测试脚本，不修改生产代码
2. **保持向后兼容**：修改后的 `step_final_confirm` 必须仍然支持现有调用
3. **测试数据隔离**：入库测试订单使用 `order_type=inbound`，清理时正确处理
4. **零退化**：不破坏现有的出库工作流测试

---

## Completion Criteria / 完成标准

- [ ] `step_final_confirm()` 支持 `order_type` 参数
- [ ] 入库工作流测试使用 KEEPER 角色进行最终确认
- [ ] 出库工作流测试仍然使用 TEAM_LEADER 角色进行最终确认
- [ ] `python -m py_compile test_runner/api_e2e.py` 通过
- [ ] 如果添加了 `run_inbound_workflow_test()`，测试逻辑完整可执行
