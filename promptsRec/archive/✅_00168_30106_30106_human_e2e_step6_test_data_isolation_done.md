# Human E2E 8分达标 - 步骤6：测试数据隔离

## 任务编号
- **执行顺序号**: 00167
- **类型编号**: 30106
- **任务类型**: 测试任务

## 任务目标
run 级唯一前缀 + setup/teardown，确保连续3次执行不因脏数据冲突失败。

## 修改范围
仅限以下文件：
- `test_runner/api_e2e.py`

## 前置依赖
- 步骤5（30105）必须已完成并验收通过

## 步骤6 具体修改要求

### 6.1 实现 run 级唯一前缀
```python
import uuid
from datetime import datetime

def generate_run_prefix():
    """生成唯一的测试数据前缀"""
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%m%d%H%M")
    return f"AUTO_{timestamp}_{run_id}"

RUN_PREFIX = generate_run_prefix()  # 例如: AUTO_03271930_a1b2c3d4
```

### 6.2 实现 setup/teardown 机制
```python
class TestDataManager:
    def __init__(self, run_prefix: str):
        self.run_prefix = run_prefix
        self.created_orders = []
        self.created_tools = []

    def setup(self):
        """测试前准备"""
        # 清理上次的残留数据（同一前缀）
        self.cleanup_old_data(self.run_prefix)

        # 创建测试所需的工装数据
        self.create_test_tools()

    def teardown(self):
        """测试后清理"""
        # 删除本次创建的测试数据
        for order_no in self.created_orders:
            self.delete_order(order_no)

        for tool_code in self.created_tools:
            self.delete_test_tool(tool_code)

    def cleanup_old_data(self, prefix: str):
        """清理旧数据（同一前缀但已过期的）"""
        # 清理超过24小时的旧数据
        pass
```

### 6.3 在测试流程中使用
```python
def run_e2e_test():
    # 初始化数据管理器
    dm = TestDataManager(RUN_PREFIX)

    try:
        # setup
        dm.setup()

        # 执行测试步骤
        execute_workflow()

    finally:
        # teardown
        dm.teardown()
```

### 6.4 修改工装搜索为使用唯一前缀
```python
def create_test_order():
    """创建测试订单，使用唯一前缀避免冲突"""
    order_no = f"IO_{RUN_PREFIX}_{seq}"
    # ... 创建订单逻辑
    return order_no
```

### 6.5 语法检查
```powershell
python -m py_compile test_runner/api_e2e.py
```

### 6.6 验证命令
```bash
# 连续运行3次测试，验证数据隔离
for i in 1 2 3; do
    echo "=== Run $i ==="
    python test_runner/test_runner_agent.py --command start --test-type quick_smoke
    python test_runner/test_runner_agent.py --command status
    python test_runner/test_runner_agent.py --command stop --reason "run_$i"
done

# 检查数据库中是否有前缀为 AUTO_ 的订单
python -c "
import sqlite3
conn = sqlite3.connect('test_reports/e2e_sensing.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT DISTINCT run_id
    FROM snapshots
    WHERE run_id LIKE 'AUTO_%'
    ORDER BY created_at DESC
    LIMIT 5
''')
runs = cursor.fetchall()
print(f'Unique runs with AUTO_ prefix: {len(runs)}')
for run in runs:
    print(f'  - {run[0]}')
conn.close()
"
```

### 6.7 验收门槛
- 连续3次执行无脏数据冲突
- 每次 run 有唯一的 `run_prefix`
- teardown 正确清理本次创建的数据

## 约束
- 不得顺手改其他步骤（步骤1-5、7-10）的内容
- 只做最小改动，聚焦于数据隔离

## 输出要求
1. 代码改动清单
2. 连续3次运行结果
3. 脏数据冲突统计（应为0）
4. 风险评估
5. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP6_REPORT_YYYYMMDD_HHMMSS.md`
