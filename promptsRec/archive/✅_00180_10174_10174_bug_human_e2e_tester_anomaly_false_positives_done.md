Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10174
Goal: 修复 human-e2e-tester 感知模块的异常检测误报问题
Dependencies: None
Execution: RUNPROMPT

---

# Bug修复: human-e2e-tester 异常检测误报

## 元数据 / Metadata

- **Prompt ID**: 10174
- **Task Type**: Bug Fix
- **Priority**: P1
- **Stage**: 10174
- **Goal**: 修复 human-e2e-tester 感知模块的异常检测误报问题
- **Dependencies**: None
- **Execution**: RUNPROMPT

---

## 上下文 / Context

### 问题背景

在 `test_reports/e2e_sensing.db` 的最新 completed run (run_id: 0378d062) 中：
- `critical_anomalies = 53`（要求 = 0，阻塞 8/10 达标）
- `high_anomalies = 68`（要求 ≤ 2）

6 项验收标准只通过 4 项，异常检测器产生大量误报。

### 异常分布（基于 run_id: 0378d062）

| 异常类型 | 数量 | 严重级别 |
|----------|------|----------|
| `illegal_state_transition` | 31 | critical |
| `workflow_blocked` | 22 | critical |
| `silent_fail` | 26 | high |
| `status_mismatch` | 22 | high |
| `button_should_be_visible` | 20 | high |

### 根本原因分析

#### Bug 1: `illegal_state_transition` 误报（31 critical）

**问题**：`workflow_detector.py` 将 `logged_in` 识别为工作流状态，触发非法状态转换误报。

**证据**：
```json
{
  "before_state": "transport_in_progress",
  "after_state": "logged_in",
  "order_type": "outbound"
}
```

`logged_in` 不在 `STATUS_LABEL_MAP` 中。当用户会话过期或未授权时，路由守卫将用户重定向到登录页，页面文本变为登录页内容。`infer_workflow_state()` 未能正确处理这种情况，导致将页面文本中匹配到的"登录"等词误识别为工作流状态。

**涉及文件**：
- `.skills/human-e2e-tester/sensing/workflow_detector.py`
- `.skills/human-e2e-tester/sensing/snapshot.py`

#### Bug 2: `workflow_blocked` 误报（22 critical）

**问题**：页面内容为空（`page_text: ''`）时被误判为 workflow blocked。

**证据**：
```json
{
  "url": "http://localhost:8150/tool-io",
  "page_text": ""
}
```

这通常是快照时机问题——Playwright 页面加载完成但 Vue 组件尚未渲染。或者用户被重定向到登录页但异常检测器未正确处理。

**涉及文件**：
- `.skills/human-e2e-tester/sensing/workflow_detector.py`

#### Bug 3: `silent_fail` 误报（26 high）

**问题**：操作后 API 未被调用但页面无错误提示，被误判为静默失败。

**证据**：
```json
{
  "operation": "smoke_login"
}
```

`smoke_login` 是测试初始化操作，不需要调用应用 API，但 `silent_fail` 检测器将其视为需要 API 调用的操作。

**涉及文件**：
- `.skills/human-e2e-tester/sensing/anomaly_detector.py`

---

## 必需参考 / Required References

1. `.skills/human-e2e-tester/sensing/workflow_detector.py` - 工作流状态检测
2. `.skills/human-e2e-tester/sensing/anomaly_detector.py` - 异常检测器
3. `.skills/human-e2e-tester/sensing/snapshot.py` - 页面快照和状态定义
4. `test_runner/validate_sensing_run.py` - 验收标准
5. `test_reports/e2e_sensing.db` - 实际异常数据

---

## 核心任务 / Core Task

修复 `human-e2e-tester` 感知模块的三个异常检测误报问题：

### Task 1: 修复 `illegal_state_transition` 误报

**位置**: `workflow_detector.py` 的 `infer_workflow_state()` 函数

**修复方案**：
1. 在 `infer_workflow_state()` 中添加对登录页的检测
2. 如果 `page_name` 或 URL 包含登录相关标识（如 `/login`），返回 `None` 而非错误状态
3. 在状态转换验证前，过滤掉 `None` 状态

**预期行为**：
- 用户被重定向到登录页时，不应触发 `illegal_state_transition`
- `before_state` 为工作流状态，`after_state` 为 `None` 时应跳过验证

### Task 2: 修复 `workflow_blocked` 误报

**位置**: `workflow_detector.py` 的 `detect_workflow_anomalies()` 函数

**修复方案**：
1. 在判定 `workflow_blocked` 前，检查 `page_text` 是否为空
2. 如果 `page_text` 为空且 `url` 是有效应用 URL（不是 `/login`），应判定为"页面加载中"而非 `workflow_blocked`
3. 添加等待重试逻辑或降低空页面的严重级别

**预期行为**：
- 空白页面不应直接判定为 `workflow_blocked (critical)`
- 空白页面可能是加载中或需要重试

### Task 3: 修复 `silent_fail` 误报

**位置**: `anomaly_detector.py` 的 `detect_silent_fail()` 函数

**修复方案**：
1. 在 `context` 中添加 `operation_type` 字段，区分 `user_action` 和 `test_action`
2. 将 `smoke_login` 等测试初始化操作标记为 `test_action`
3. `silent_fail` 检测器只对 `user_action` 类型操作生效

**预期行为**：
- `smoke_login` 等测试操作不应触发 `silent_fail`
- 只有用户执行的操作（如提交订单）才应触发 `silent_fail` 检测

---

## 约束条件 / Constraints

1. **不修改验收标准**：`validate_sensing_run.py` 的 6 项阈值保持不变
2. **向后兼容**：修复后，真实的异常仍应被正确检测
3. **只修改测试框架代码**：不修改应用代码（frontend/、backend/）
4. **使用 8D 问题解决协议**：遵循 `.claude/rules/40_debug_8d.md`

---

## 完成标准 / Completion Criteria

1. 运行 `python test_runner/validate_sensing_run.py` 验证修复效果
2. 目标：`critical_anomalies <= 0`，`high_anomalies <= 2`
3. 修复后在同一数据库上重新验证，确保不引入新误报
4. 编写修复报告到 `logs/prompt_task_runs/run_[timestamp]_bug_human_e2e_tester_anomaly_false_positives.md`
