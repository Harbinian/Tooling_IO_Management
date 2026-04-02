# Human E2E 8分达标 - 步骤10：最终回归与评分

## 任务编号
- **类型编号**: 30110
- **任务类型**: 测试任务
- **Primary Executor**: Claude Code

## 任务目标
连续回归确认达到8分标准。执行 `quick_smoke + full_workflow + rbac` 连跑至少3轮。

## 前置依赖
- 步骤1-9 必须全部已完成并验收通过
- **P0修复任务已完成**: `promptsRec/archive/✅_00185_10178_10178_backend_p0_fixes_done.md`
  - 外部表字段名常量规范化 ✅
  - order_repository 事务包装 ✅
  - SECRET_KEY 生产强制检查 ✅
  - Flask-Limiter 速率限制 ✅

## 步骤10 具体修改要求

### 10.1 执行完整回归测试
```bash
# 连续3轮完整回归
for round in 1 2 3; do
    echo "=========================================="
    echo "Regression Round $round / 3"
    echo "=========================================="

    # Round 1: quick_smoke
    echo "[Round $round] Running quick_smoke..."
    python test_runner/test_runner_agent.py --command start --test-type quick_smoke
    python test_runner/test_runner_agent.py --command stop --reason "round_${round}_smoke_done"

    # Round 2: full_workflow
    echo "[Round $round] Running full_workflow..."
    python test_runner/test_runner_agent.py --command start --test-type full_workflow
    python test_runner/test_runner_agent.py --command stop --reason "round_${round}_workflow_done"

    # Round 3: rbac
    echo "[Round $round] Running rbac..."
    python test_runner/test_runner_agent.py --command start --test-type rbac
    python test_runner/test_runner_agent.py --command stop --reason "round_${round}_rbac_done"

    # 验证本轮结果
    python test_runner/validate_sensing_run.py
done
```

### 10.2 评分计算
根据 `test_runner/validate_sensing_run.py` 的 calculate_score 函数评分 (满分10分)

### 10.3 验收标准
| 指标 | 门槛 |
|------|------|
| `quick_smoke` | 通过，无critical错误 |
| `full_workflow` | 通过，无critical错误 |
| `rbac` | 通过，无critical错误 |
| 评分 | >= 8/10，连续3轮 |

### 10.4 最终报告
生成 `test_reports/HUMAN_E2E_STEP10_REPORT_YYYYMMDD_HHMMSS.md`

## 约束
- 此步骤为验证步骤，聚焦于验证而非修改
- 如有未达标项，记录到 next_steps

## 报告输出
写入 `test_reports/HUMAN_E2E_STEP10_REPORT_YYYYMMDD_HHMMSS.md`

---

## 遗留问题（从上次执行，已在P0修复中处理）

### P0修复已处理的问题

1. **外部表访问规范化** (`✅_00185_10178_10178_backend_p0_fixes_done.md`)
   - `database_manager.py` 字段名改为常量引用
   - `column_names.py` 规范化 ✅

2. **order_repository 事务包装** (`✅_00185_10178_10178_backend_p0_fixes_done.md`)
   - `create_order`, `submit_order`, `keeper_confirm`, `final_confirm` 已添加事务 ✅

3. **SECRET_KEY 生产强制检查** (`✅_00185_10178_10178_backend_p0_fixes_done.md`)
   - 生产环境必须设置 SECRET_KEY ✅

4. **Flask-Limiter 速率限制** (`✅_00185_10178_10178_backend_p0_fixes_done.md`)
   - 全局 100/minute，登录 5/minute ✅

### 仍需关注的问题

1. **测试数据冲突**: 工装 T000001 被订单占用
   - 影响: 订单创建失败
   - 解决: 清理未完成订单或使用隔离数据

2. **keeper-confirm API参数问题**: item标识符不匹配
   - 错误: `no items were updated - check item identifiers`
   - 需验证: P0修复后是否已解决

3. **SensingOrchestrator.storage 缺失**: RBAC结果无法记录
   - 需验证: 是否已初始化 `orchestrator.storage` 属性

### 上次执行结果 (2026-03-27)
- 平均分: 4/10 (未达到8/10)
- 异常数: 69 critical + 73 high (应接近0)
