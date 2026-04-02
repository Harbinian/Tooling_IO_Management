# 提示词：增强 E2E 测试数据清理机制

Primary Executor: Codex
Task Type: Feature Development
Priority: P2
Stage: 00019
Goal: Enhance E2E test data cleanup to prevent stale order conflicts
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
E2E API 测试运行时发现工装 T000001 被历史订单 TO-OUT-20260402-003（状态为 keeper_confirmed）占用，导致测试创建新订单失败。虽然测试框架使用时间戳前缀 AUTO_XXXX_ 作为数据隔离，但旧数据清理逻辑未生效。

### 目标用户
测试工程师、开发人员

### 核心痛点
测试数据污染导致 E2E 测试误报失败。`tool_io_service.py` 的工装可用性检查逻辑正确，但测试未清理超过1天的历史订单。

### 业务目标
实现有效的数据清理机制，确保 E2E 测试可重复执行且结果稳定。

---

## Required References / 必需参考

- `test_runner/api_e2e.py` - 测试运行器主文件
- `backend/database/repositories/order_repository.py` - 订单仓库
- `.claude/rules/00_core.md` - 核心开发规则
- `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵（了解测试用户角色）

---

## Core Task / 核心任务

增强 `test_runner/api_e2e.py` 中的测试数据清理机制，确保测试开始前清理以下内容：

1. **订单清理**：清理超过24小时的已完成/已拒绝订单
2. **工装占用清理**：确保被旧订单锁定的工装在测试前被释放
3. **测试数据清理**：按测试前缀 AUTO_XXXX_ 清理孤立测试数据

---

## Required Work / 必需工作

### Step 1: 分析现有清理逻辑
- 读取 `test_runner/api_e2e.py` 中的数据清理相关代码
- 确认当前清理机制的实现方式
- 识别为何时间戳前缀机制未能防止旧订单冲突

### Step 2: 设计增强清理策略
- 方案A：测试前强制清理24小时前的所有订单（谨慎）
- 方案B：为工装可用性检查添加 `exclude_order_no` 参数（推荐）
- 方案C：测试数据管理器添加主动清理任务（可与方案B组合）

### Step 3: 实现增强清理
- 在 `TestDataManager` 类中添加 `cleanup_stale_orders()` 方法
- 或在 `check_tools_available()` 调用时传入当前测试订单号排除检查

### Step 4: 验证
- 运行 `python test_runner/api_e2e.py` 确认测试可重复执行
- 确认工装占用错误不再出现

---

## Constraints / 约束条件

1. 清理操作必须对生产数据安全（只清理测试前缀或超时数据）
2. 禁止修改业务逻辑（`tool_io_service.py`、`order_repository.py` 中的工装检查逻辑保持不变）
3. 使用英文变量名和函数名
4. 测试通过 `python -m py_compile` 语法检查

---

## Completion Criteria / 完成标准

1. [ ] E2E 测试可连续执行3次而不出现工装占用错误
2. [ ] 测试数据清理代码添加到 `test_runner/api_e2e.py`
3. [ ] 代码通过语法检查：`python -m py_compile test_runner/api_e2e.py`
4. [ ] 测试报告不再显示因历史订单导致的误报失败
