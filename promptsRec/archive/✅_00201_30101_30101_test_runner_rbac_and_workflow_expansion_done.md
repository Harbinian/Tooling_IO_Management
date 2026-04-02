# test_runner 测试覆盖率扩展

Primary Executor: Codex
Task Type: Testing
Priority: P1
Stage: 30101
Goal: 扩展 api_e2e.py RBAC 矩阵至完整覆盖，添加入库和驳回重提工作流测试
Dependencies: None
Execution: RUNPROMPT

---

## Context

根据 `human-e2e-tester/skill.md` 的定义，当前 test_runner 的测试覆盖率严重不足：

| 维度 | 要求 | 当前 | 差距 |
|------|------|------|------|
| RBAC 权限覆盖 | 19-20个 | ~9个 | 47% |
| 角色覆盖 | 6个 | 4个 | 67% |
| 工作流 | 入库+驳回重提 | 仅出库 | 0% |

已有本地修改（未提交）：
- `api_e2e.py`: 密码改用 TEST_USERS、RBAC DENY 判断增加 404、`spec_model` 字段
- `playwright_e2e.py`: 5处硬编码密码改用 TEST_USERS

---

## Required References

- `.skills/human-e2e-tester/skill.md` - 测试要求和完整权限矩阵
- `docs/RBAC_PERMISSION_MATRIX.md` - RBAC 权限矩阵定义
- `test_runner/api_e2e.py` - 当前 API E2E 测试实现
- `promptsRec/.sequence` - 计数器文件

---

## Core Task

扩展 `test_runner/api_e2e.py` 的测试覆盖率，包括：
1. 补全 RBAC 测试矩阵
2. 添加入库工作流测试
3. 添加驳回重提工作流测试
4. 添加命令行工作流选择参数

---

## Required Work

### 1. 提交已有的本地修复

```bash
git add test_runner/api_e2e.py test_runner/playwright_e2e.py
git commit -m "fix: standardize test credentials and RBAC deny logic"
```

### 2. 扩展 RBAC_TEST_MATRIX (api_e2e.py 第1492行附近)

根据 skill.md 第94-116行的权限目录，补全缺失的权限测试点：

| 权限 | API 端点 | 方法 | 补充角色 |
|------|----------|------|----------|
| `dashboard:view` | `/api/dashboard` | GET | 全部角色 |
| `tool:search` | `/api/tools/search` | GET | 全部角色 |
| `tool:view` | `/api/tools/<id>` | GET | 全部角色 |
| `notification:view` | `/api/notifications` | GET | 全部角色 |
| `notification:create` | `/api/notifications` | POST | 部分角色 |
| `log:view` | `/api/logs` | GET | KEEPER |
| `admin:role_manage` | `/api/admin/roles` | GET | SYS_ADMIN |

注意：
- PLANNER 和 AUDITOR 角色当前无测试用户，对应条目标记为 SKIP
- 复用 `login_user()` 函数获取各角色 token
- 复用 `api_get()`, `api_post()` 发送请求

### 3. 添加入库工作流测试函数

文件: `test_runner/api_e2e.py`

新增函数 `run_inbound_workflow_test(report, orchestrator)`:

```
入库流程 (14步骤):
1. taidongxu 登录
2. taidongxu 创建入库订单 (order_type: "inbound")
3. taidongxu 提交订单
4. hutingting 登录
5. hutingting 获取待确认订单
6. hutingting 保管员确认
7. hutingting 发送运输通知
8. fengliang 登录
9. fengliang 开始运输
10. fengliang 完成运输
11. hutingting 最终确认 (入库由KEEPER确认)
12. 验证订单状态
13. admin 清理测试订单
```

关键差异：
- `order_type: "inbound"` 而非 `"outbound"`
- 最终确认由 `hutingting` 而非 `taidongxu`
- 调用 `/final-confirm` 时 `operator_role: "keeper"`

### 4. 添加驳回重提工作流测试函数

文件: `test_runner/api_e2e.py`

新增函数 `run_reject_resubmit_workflow_test(report, orchestrator)`:

```
驳回重提流程 (18步骤):
1. taidongxu 登录
2. taidongxu 创建订单
3. taidongxu 提交订单
4. hutingting 登录
5. hutingting 驳回订单 (POST /cancel) + 填写原因
6. 验证订单状态变为 rejected
7. taidongxu 查看被驳回订单
8. taidongxu 修改订单 (PUT /<order_no>)
9. taidongxu 重新提交
10. hutingting 再次确认
11. hutingting 发送运输通知
12. fengliang 登录
13. fengliang 开始运输
14. fengliang 完成运输
15. taidongxu 最终确认
16. 验证完成状态
17. admin 清理
```

关键 API：
- 驳回: `POST /tool-io-orders/<order_no>/cancel` body: `{"reason": "测试驳回原因", ...}`
- 修改: `PUT /tool-io-orders/<order_no>` body: `{"items": [...]}`

### 5. 修改 main() 函数支持工作流选择

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="API E2E Test Runner")
    parser.add_argument("--workflows", default="all",
                       choices=["all", "smoke", "workflow", "rbac", "inbound", "reject"])
    args = parser.parse_args()

    # 根据 args.workflows 执行对应测试
    if args.workflows in ["all", "smoke"]:
        run_quick_smoke_test(...)
    if args.workflows in ["all", "workflow"]:
        run_full_workflow_test(...)
    if args.workflows in ["all", "rbac"]:
        run_rbac_test(...)
    if args.workflows in ["all", "inbound"]:
        run_inbound_workflow_test(...)
    if args.workflows in ["all", "reject"]:
        run_reject_resubmit_workflow_test(...)
```

---

## Constraints

1. **编码规范**: 所有文件使用 UTF-8 (无 BOM)
2. **命名规范**: snake_case 函数/变量，PascalCase 类
3. **测试隔离**: 使用 `TestDataManager` 追踪创建的订单，teardown 时清理
4. **异常处理**: 关键 I/O 操作使用 try-except
5. **复用现有函数**: 优先复用 `login_user()`, `api_get()`, `api_post()`, `api_delete()`, `execute_step()`
6. **不重复造轮子**: 直接复用 `step_keeper_confirm()`, `step_transport_start()` 等封装函数
7. **数据一致性**: TEST_TOOL 使用统一常量 (`api_e2e.py` 第217行)

---

## Completion Criteria

1. **RBAC 矩阵覆盖率**: `RBAC_TEST_MATRIX` 条目数从 ~24 增加到 50+
2. **工作流测试**: 新增 `run_inbound_workflow_test()` 和 `run_reject_resubmit_workflow_test()` 两个完整函数
3. **命令行接口**: `--workflows` 参数正确路由到对应测试函数
4. **语法检查通过**: `python -m py_compile test_runner/api_e2e.py` 无错误
5. **测试隔离**: 每个工作流使用独立的 `TestDataManager` 实例进行 setup/teardown

---

## Verification Plan

1. 语法检查:
   ```bash
   python -m py_compile test_runner/api_e2e.py
   ```

2. 验证 RBAC 矩阵条目数:
   ```bash
   grep -c "RBAC_TEST_MATRIX = \[" test_runner/api_e2e.py
   # 期望: 1 (整个矩阵)
   grep "^\s*(" test_runner/api_e2e.py | grep -c "RBAC_TEST_MATRIX"
   # 期望: > 50 条测试用例
   ```

3. 验证函数存在:
   ```bash
   grep -c "def run_inbound_workflow_test" test_runner/api_e2e.py
   grep -c "def run_reject_resubmit_workflow_test" test_runner/api_e2e.py
   # 期望: 各为 1
   ```
