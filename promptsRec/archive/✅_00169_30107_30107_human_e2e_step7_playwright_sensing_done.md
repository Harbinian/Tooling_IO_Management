# Human E2E 8分达标 - 步骤7：Playwright 路径同框架接入

## 任务编号
- **执行顺序号**: 00168
- **类型编号**: 30107
- **任务类型**: 测试任务

## 任务目标
Playwright 执行也触发同级感知落库，验证 Playwright 跑后关键表有增量。

## 修改范围
仅限以下文件：
1. `test_runner/playwright_e2e.py`
2. `.skills/human-e2e-tester/sensing/page_observer.py`

## 前置依赖
- 步骤1（30101）必须已完成并验收通过
- 步骤3（30103）必须已完成并验收通过（感知采集基础）

## 步骤7 具体修改要求

### 7.1 在 playwright_e2e.py 中集成 SensingOrchestrator
参考 human-e2e-tester 技能文档：

```python
import sys
sys.path.insert(0, ".skills/human-e2e-tester")

from sensing import SensingOrchestrator

# 初始化 orchestrator（与 api_e2e.py 相同）
orch = SensingOrchestrator(
    db_path="test_reports/e2e_sensing.db",
    run_id="<from agent status>",
    test_type="playwright_workflow",
)

# 设置用户上下文
orch.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")
```

### 7.2 在 Playwright 操作中调用感知
```python
async def execute_playwright_step(page, step_name: str, operation: callable):
    """
    Playwright 步骤执行 + 感知采集
    """
    # before snapshot
    snap_before = orch.snapshot_before(page)

    # execute operation
    await operation()

    # after snapshot
    snap_after = orch.snapshot_after(page, operation=step_name)

    # advance
    advance(step_name, anomalies_count=len(orch.anomalies), critical_count=orch.critical_count)
```

### 7.3 修改 page_observer.py 支持 Playwright
检查 `.skills/human-e2e-tester/sensing/page_observer.py`，确认：
- `snapshot_before` 支持 Playwright page 对象
- `snapshot_after` 支持 Playwright page 对象
- 返回格式与 api_e2e.py 一致

### 7.4 验证 Playwright 集成
```python
# 在 playwright_e2e.py 中测试
async def test_playwright_sensing():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        orch = SensingOrchestrator(db_path="test_reports/e2e_sensing.db", run_id="test", test_type="playwright")

        # 登录
        page.goto("http://localhost:8150")
        orch.snapshot_before(page)

        page.fill("#username", "taidongxu")
        page.fill("#password", "test123")
        page.click("button[type='submit']")

        snap, anomalies, checks = orch.snapshot_after(page, operation="login")
        print(f"Anomalies: {len(anomalies)}, Checks: {len(checks)}")

        browser.close()
```

### 7.5 语法检查
```powershell
python -m py_compile test_runner/playwright_e2e.py
```

### 7.6 验证命令
```bash
# 运行 Playwright E2E
python test_runner/playwright_e2e.py

# 检查数据库
python -c "
import sqlite3
conn = sqlite3.connect('test_reports/e2e_sensing.db')
cursor = conn.cursor()

tables = ['snapshots', 'workflow_positions', 'consistency_checks', 'anomalies']
for t in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {t}')
    count = cursor.fetchone()[0]
    print(f'{t}: {count}')

    # 查询是否有 Playwright 相关的 run
    cursor.execute(f'''
        SELECT COUNT(*) FROM {t}
        WHERE run_id LIKE '%playwright%' OR test_type = 'playwright'
    ''')
    pw_count = cursor.fetchone()[0]
    print(f'  Playwright entries: {pw_count}')
conn.close()
"
```

### 7.7 验收门槛
- `snapshots` 表有 Playwright 执行的记录
- `workflow_positions` 表有 Playwright 步骤的位置
- 关键表总计数 > 步骤6结束时的基数

## 约束
- 不得顺手改其他步骤（步骤1-6、8-10）的内容
- 只做最小改动，聚焦于 Playwright 感知集成

## 输出要求
1. 代码改动清单
2. Playwright 感知集成说明
3. 验证命令执行结果
4. 各关键表的数据计数
5. 风险评估
6. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP7_REPORT_YYYYMMDD_HHMMSS.md`
