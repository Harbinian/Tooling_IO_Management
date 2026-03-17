# Human E2E 8分达标 - 步骤5：修正 RBAC 用例假阳性

## 任务编号
- **执行顺序号**: 00166
- **类型编号**: 30105
- **任务类型**: 测试任务

## 任务目标
RBAC 用例改为"前置数据 + 明确预期响应"，使 RBAC 报告可解释、可复现。

## 修改范围
仅限以下文件：
- `test_runner/api_e2e.py`

## 前置依赖
- 步骤4（30104）必须已完成并验收通过

## 步骤5 具体修改要求

### 5.1 重构 RBAC 测试用例结构
将 RBAC 用例从"尝试访问 -> 检查是否拒绝"模式改为：

```python
def test_rbac_permission(role: str, permission: str, expected_response: str):
    """
    RBAC 测试用例

    Args:
        role: 角色名称 (e.g., 'TEAM_LEADER', 'KEEPER')
        permission: 权限名称 (e.g., 'order:create', 'order:delete')
        expected_response: 期望响应 ('ALLOW' 或 'DENY')
    """
    # 1. 前置数据准备
    setup_test_data(role, permission)

    # 2. 以指定角色登录
    login_as(role)

    # 3. 执行操作
    response = execute_permission_action(permission)

    # 4. 验证预期响应
    actual = 'ALLOW' if response.status == 200 else 'DENY'
    assert actual == expected_response, f"RBAC Violation: {role} -> {permission} expected {expected_response} but got {actual}"

    # 5. 记录到感知数据库
    record_rbac_result(role, permission, expected_response, actual)
```

### 5.2 定义 RBAC 测试矩阵
```python
RBAC_TEST_MATRIX = [
    # (role, permission, expected)
    ('TEAM_LEADER', 'order:create', 'ALLOW'),
    ('TEAM_LEADER', 'order:delete', 'DENY'),
    ('TEAM_LEADER', 'order:keeper_confirm', 'DENY'),
    ('KEEPER', 'order:create', 'DENY'),
    ('KEEPER', 'order:keeper_confirm', 'ALLOW'),
    ('KEEPER', 'order:delete', 'DENY'),
    ('PRODUCTION_PREP', 'order:create', 'DENY'),
    ('PRODUCTION_PREP', 'order:transport_execute', 'ALLOW'),
    ('SYS_ADMIN', 'order:delete', 'ALLOW'),
    # ... 完整矩阵见 docs/RBAC_PERMISSION_MATRIX.md
]
```

### 5.3 消除假阳性
问题：原有用例可能存在：
- 测试数据未正确隔离
- 预期响应定义模糊
- 缺少前置条件检查

修改后：
- 每个用例有明确的 `expected_response`
- 前置数据确保测试可重复
- 响应码精确匹配（200=ALLOW, 403=DENY）

### 5.4 语法检查
```powershell
python -m py_compile test_runner/api_e2e.py
```

### 5.5 验证命令
```bash
# 运行 RBAC 测试
python test_runner/test_runner_agent.py --command start --test-type rbac
python test_runner/test_runner_agent.py --command status
python test_runner/test_runner_agent.py --command report

# 查询 RBAC 结果
python -c "
import sqlite3
conn = sqlite3.connect('test_reports/e2e_sensing.db')
cursor = conn.cursor()

# 查询 RBAC 相关记录
cursor.execute('''
    SELECT role, permission, expected, actual, status
    FROM rbac_results
    ORDER BY created_at DESC
''')
results = cursor.fetchall()
print(f'Total RBAC tests: {len(results)}')

passed = sum(1 for r in results if r[4] == 'PASS')
failed = sum(1 for r in results if r[4] == 'FAIL')
print(f'Passed: {passed}, Failed: {failed}')

for r in results:
    print(f'{r[0]} -> {r[1]}: expected={r[2]}, actual={r[3]}, status={r[4]}')
conn.close()
"
```

### 5.6 验收门槛
- RBAC 测试用例有明确的 `expected` 字段
- 报告可解释（每条记录有人类可读的说明）
- 报告可复现（相同条件下运行结果一致）

## 约束
- 不得顺手改其他步骤（步骤1-4、6-10）的内容
- 只做最小改动，聚焦于 RBAC 用例修正

## 输出要求
1. 代码改动清单
2. RBAC 测试矩阵（至少覆盖20个用例）
3. 验证命令执行结果
4. 风险评估
5. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP5_REPORT_YYYYMMDD_HHMMSS.md`
