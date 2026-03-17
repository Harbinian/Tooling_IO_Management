# Human E2E 8分达标 - 步骤1：建立单一事实库约束

## 任务编号
- **执行顺序号**: 00162
- **类型编号**: 30101
- **任务类型**: 测试任务

## 任务目标
全链路统一写 `test_reports/e2e_sensing.db`，消除分叉库数据增量。

## 修改范围
仅限以下文件：
1. `test_runner/test_runner_agent.py`
2. `test_runner/api_e2e.py`
3. `test_runner/playwright_e2e.py`
4. `test_runner/sensing_integration.py`
5. `.skills/human-e2e-tester/sensing/storage.py`

## 验收标准
- 不再出现分叉库数据增量
- 所有测试 runner 写入同一个 SQLite 数据库
- 查询 `test_reports/e2e_sensing.db` 关键表计数一致

## 统一数据库路径
```python
# 所有文件必须使用同一个 db_path
DB_PATH = "test_reports/e2e_sensing.db"
```

## 步骤1 具体修改要求

### 1.1 检查 storage.py 的 db_path 定义
读取 `.skills/human-e2e-tester/sensing/storage.py`，确认 `DB_PATH` 常量定义。

### 1.2 修改 test_runner_agent.py
- 导入 `from backend.database.schema.column_names import ...` 如有需要
- 确保使用统一的 `DB_PATH`

### 1.3 修改 api_e2e.py
- 确保使用与 storage.py 相同的 `DB_PATH`
- 检查是否有硬编码的 db 路径

### 1.4 修改 playwright_e2e.py
- 同上，统一 db 路径

### 1.5 修改 sensing_integration.py
- 同上，统一 db 路径

### 1.6 语法检查
```powershell
python -m py_compile test_runner/test_runner_agent.py test_runner/api_e2e.py test_runner/playwright_e2e.py test_runner/sensing_integration.py .skills/human-e2e-tester/sensing/storage.py
```

### 1.7 验证命令
```bash
# 启动测试并检查数据库
python test_runner/test_runner_agent.py --command start --test-type quick_smoke
python test_runner/test_runner_agent.py --command status
python test_runner/test_runner_agent.py --command stop --reason "step1-check"

# 查询数据库计数
python -c "
import sqlite3
conn = sqlite3.connect('test_reports/e2e_sensing.db')
cursor = conn.cursor()
tables = ['snapshots', 'workflow_positions', 'consistency_checks', 'anomalies']
for t in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {t}')
        print(f'{t}: {cursor.fetchone()[0]}')
    except: print(f'{t}: table not found or empty')
conn.close()
"
```

## 约束
- 不得顺手改其他步骤（步骤2-10）的内容
- 只做最小改动，聚焦于 db 路径统一

## 输出要求
1. 代码改动清单
2. 验证命令执行结果
3. 风险评估
4. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP1_REPORT_YYYYMMDD_HHMMSS.md`
