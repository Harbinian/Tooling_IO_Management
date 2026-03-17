# Human E2E 8分达标 - 步骤8：统一报告协议

## 任务编号
- **执行顺序号**: 00169
- **类型编号**: 30108
- **任务类型**: 测试任务

## 任务目标
`report` 输出稳定、结构化，确保 `start/status/advance/report/stop` 全可用且 JSON 稳定。

## 修改范围
仅限以下文件：
1. `test_runner/test_runner_agent.py`
2. `test_runner/commands.py`

## 前置依赖
- 步骤7（30107）必须已完成并验收通过

## 步骤8 具体修改要求

### 8.1 定义稳定的 JSON 报告格式
```python
REPORT_TEMPLATE = {
    "success": True,
    "report": {
        "metadata": {
            "run_id": str,
            "test_type": str,
            "status": str,  # RUNNING/PAUSED/COMPLETED/FAILED
            "started_at": str,
            "ended_at": str or None,
            "duration_seconds": int or None
        },
        "summary": {
            "total_operations": int,
            "completed_operations": int,
            "failed_operations": int,
            "anomalies_count": int,
            "critical_count": int,
            "high_count": int,
            "medium_count": int,
            "low_count": int
        },
        "operations": [
            {
                "index": int,
                "name": str,
                "status": str,  # SUCCESS/FAILED/PAUSED
                "started_at": str,
                "duration_ms": int,
                "anomalies": int,
                "critical": int
            }
        ],
        "sensing": {
            "snapshots_count": int,
            "workflow_positions_count": int,
            "consistency_checks_passed": int,
            "consistency_checks_failed": int,
            "anomalies": [
                {
                    "type": str,
                    "severity": str,
                    "description": str,
                    "order_no": str or None,
                    "operation": str
                }
            ]
        },
        "workflow_positions": [
            {
                "operation": str,
                "position": str,
                "available_actions": list,
                "forbidden_actions": list
            }
        ]
    }
}
```

### 8.2 实现 report 命令
```python
def cmd_report(args):
    """生成结构化报告"""
    status = get_status()

    if status.get("state") == "IDLE":
        return {"success": False, "error": "No test run found"}

    run_id = status.get("run_id")

    # 查询数据库获取完整数据
    report_data = build_report(run_id)

    return {
        "success": True,
        "report": report_data
    }
```

### 8.3 实现 build_report 函数
```python
def build_report(run_id: str) -> dict:
    """从数据库构建完整报告"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 元数据
    metadata = get_run_metadata(cursor, run_id)

    # 汇总数据
    summary = get_run_summary(cursor, run_id)

    # 操作列表
    operations = get_operations(cursor, run_id)

    # 感知数据
    sensing = get_sensing_summary(cursor, run_id)

    conn.close()

    return {
        "metadata": metadata,
        "summary": summary,
        "operations": operations,
        "sensing": sensing
    }
```

### 8.4 确保 JSON 稳定性
- 所有字段使用 snake_case
- 所有时间使用 ISO 8601 格式
- 所有枚举值使用大写
- 缺失字段返回 `null` 而非省略

### 8.5 验证命令
```bash
# 启动测试
python test_runner/test_runner_agent.py --command start --test-type quick_smoke

# 运行几步
python test_runner/test_runner_agent.py --command advance --current-operation "login" --anomalies-count 0 --critical-count 0

# 获取报告
python test_runner/test_runner_agent.py --command report

# 验证 JSON 结构
python -c "
import json
from test_runner.commands import report

result = report()
print(json.dumps(result, indent=2, ensure_ascii=False))

# 验证必要字段
assert result['success'] == True
assert 'report' in result
assert 'metadata' in result['report']
assert 'summary' in result['report']
assert 'sensing' in result['report']
print('JSON structure validation passed')
"
```

### 8.6 验收门槛
- `report` 命令返回稳定 JSON
- 所有字段符合模板定义
- 无运行时错误
- 可解析并通过 schema 验证

## 约束
- 不得顺手改其他步骤（步骤1-7、9-10）的内容
- 只做最小改动，聚焦于报告协议

## 输出要求
1. 代码改动清单
2. JSON 报告模板
3. 验证命令执行结果
4. 风险评估
5. 回滚方式（如有）

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP8_REPORT_YYYYMMDD_HHMMSS.md`
