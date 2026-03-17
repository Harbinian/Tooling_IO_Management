# Human E2E 8分达标 - 步骤4：完成失败分支闭环

## 任务编号
- **执行顺序号**: 00165
- **类型编号**: 30104
- **任务类型**: 测试任务

## 任务目标
异常时仍执行 `snapshot_after` 与 `advance/stop`，确保失败 run 也有完整状态与感知数据。

## 修改范围
仅限以下文件：
- `test_runner/api_e2e.py`

## 前置依赖
- 步骤3（30103）必须已完成并验收通过

## 步骤4 具体修改要求

### 4.1 在 execute_step 中添加异常处理
```python
def execute_step(step_name: str, before_action: callable, action: callable,
                 after_action: callable, expected_next_state: str = None):
    try:
        # before
        before_snapshot = before_action() if before_action else None

        # action
        result = action()

        # after
        after_snapshot = after_action() if after_action else None

        # advance - 正常推进
        advance(step_name, anomalies_count=0, critical_count=0)

        return result
    except Exception as e:
        # 即使失败，也要执行 snapshot_after
        if after_action:
            try:
                after_snapshot = after_action()
            except:
                pass

        # 记录异常
        anomalies_count = 1
        critical_count = 1 if is_critical_error(e) else 0

        # 仍要 advance 或 stop
        if is_recoverable_error(e):
            advance(step_name, anomalies_count=anomalies_count, critical_count=critical_count)
        else:
            stop(f"step_failed: {step_name}, error: {str(e)}")

        raise  # 重新抛出异常
```

### 4.2 定义错误分类函数
```python
def is_critical_error(e: Exception) -> bool:
    """判断是否为关键错误"""
    critical_types = (API500Error, DatabaseConnectionError, PermissionDeniedError)
    return isinstance(e, critical_types)

def is_recoverable_error(e: Exception) -> bool:
    """判断是否为可恢复错误"""
    recoverable_types = (ValidationError, TimeoutError, NetworkError)
    return isinstance(e, recoverable_types)
```

### 4.3 验证异常分支
模拟一个失败的 API 调用，验证：
- `snapshot_after` 仍被调用
- 异常被正确记录
- `advance` 或 `stop` 被调用

### 4.4 语法检查
```powershell
python -m py_compile test_runner/api_e2e.py
```

### 4.5 验证命令
```bash
# 检查失败 run 的数据完整性
python -c "
import sqlite3
conn = sqlite3.connect('test_reports/e2e_sensing.db')
cursor = conn.cursor()

# 查询最新的 run
cursor.execute('SELECT DISTINCT run_id FROM snapshots ORDER BY created_at DESC LIMIT 1')
run_id = cursor.fetchone()
if run_id:
    run_id = run_id[0]
    print(f'Run ID: {run_id}')

    # 查询该 run 的数据
    for table in ['snapshots', 'workflow_positions', 'consistency_checks', 'anomalies']:
        cursor.execute(f'SELECT COUNT(*) FROM {table} WHERE run_id = ?', (run_id,))
        count = cursor.fetchone()[0]
        print(f'{table}: {count}')
conn.close()
"
```

### 4.6 验收门槛
- 失败 run 的 `snapshots` 表有数据
- 失败 run 的 `anomalies` 表有异常记录
- 失败 run 的 `workflow_positions` 有最后位置

## 约束
- 不得顺手改其他步骤（步骤1-3、5-10）的内容
- 只做最小改动，聚焦于异常分支闭环

## 输出要求
1. 代码改动清单
2. 异常处理逻辑说明
3. 验证命令执行结果
4. 风险评估
5. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP4_REPORT_YYYYMMDD_HHMMSS.md`
