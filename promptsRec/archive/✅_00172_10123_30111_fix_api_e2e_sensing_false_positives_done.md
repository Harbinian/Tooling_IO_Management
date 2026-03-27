# BUG 修复: API E2E 测试的感知系统误报

## 任务编号
- **执行顺序号**: 00172
- **类型编号**: 10123
- **任务类型**: Bug修复任务 (10101-19999)

## 问题描述

### 症状
E2E回归测试发现大量误报异常：
- `silent_fail` x39
- `status_mismatch` x34
- `workflow_blocked` x39
- `illegal_state_transition` x30

导致测试评分只有 4/10，未达到 8/10 标准。

### 根本原因
`SensingOrchestrator` 是为 Playwright 浏览器测试设计的（需要 `driver` 参数），但 `api_e2e.py` 调用时传递了 `driver=None`（因为是纯API测试，没有浏览器）。

当 `sense_page(None)` 被调用时：
1. 返回的页面状态为 `unknown`
2. 所有后续的异常检测（`detect_all_anomalies`, `detect_workflow_anomalies` 等）都以这个 unknown 状态进行判断
3. 导致大量"工作流阻塞"、"状态不匹配"、"非法状态转换"等误报

## 修复方案

### 修改文件: `test_runner/api_e2e.py`

**找到以下代码** (约第36-43行):
```python
try:
    from sensing.storage import SQLiteStorage, RbacResultRecord
    from sensing.orchestrator import SensingOrchestrator
    SENSING_AVAILABLE = True
except ImportError:
    SENSING_AVAILABLE = False
    print("[WARN] Sensing module not available, running without sensing")
```

**修改为**:
```python
# API E2E 测试不使用感知系统，因为没有浏览器页面可以观察
# SensingOrchestrator 依赖 Playwright/Selenium driver 来获取页面状态
# API 测试只有 HTTP 响应，没有页面状态可言
SENSING_AVAILABLE = False
print("[INFO] API E2E mode: sensing disabled (no browser available)")
```

### 修改文件: `test_runner/playwright_e2e.py`

**保持不变** - Playwright测试应该继续使用感知系统。

## 修改范围

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `test_runner/api_e2e.py` | Bug修复 | 禁用API测试的感知系统，避免误报 |

## 前置条件

无（此修改不影响其他功能）

## 验证步骤

1. 修改代码后，运行一轮API E2E测试:
   ```bash
   cd E:/CA001/Tooling_IO_Management
   python test_runner/api_e2e.py
   ```

2. 检查输出中不再出现:
   - `[OK] Sensing orchestrator initialized`
   - `sensing_integration` 相关警告

3. 检查数据库中异常数应大幅下降:
   ```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('test_reports/e2e_sensing.db')
   c = conn.cursor()
   c.execute('SELECT COUNT(*) FROM anomalies WHERE run_id = (SELECT run_id FROM test_runs ORDER BY started_at DESC LIMIT 1)')
   print('Anomalies:', c.fetchone()[0])
   conn.close()
   "
   ```

4. 期望结果: 异常数接近 0

## 约束

- 只修改指定的文件
- 不添加新文件
- 不删除任何文件
- 不修改 `playwright_e2e.py`（保持Playwright测试的感知能力）
