---
name: human-e2e-tester
executor: Claude Code
auto_invoke: false
depends_on: []
triggers:
  - /human-e2e-tester
rules_ref:
  - .claude/rules/00_core.md
  - .claude/rules/06_testing.md
version: 1.0.0
---

# 人工 E2E 测试技能 / Human E2E Tester

命令触发: `/human-e2e-tester`

---

## 目的 / Purpose

本技能执行系统的人工模拟探索性测试。/ This skill performs human-simulated exploratory testing of the system.

与自动化测试脚本不同，本技能尝试像真实用户一样行为。/ Unlike automated test scripts, this skill tries to behave like a real user.

它验证系统是否真正可用，以及工作流从人类角度是否有意义。/ It verifies whether the system is actually usable and whether workflows make sense from a human perspective.

本技能在发布前和重大功能变更后特别有用。/ This skill is especially useful before releases and after major feature changes.

本技能不应用于编写代码。/ This skill should NOT be used for writing code.

其目的是发现和验证。/ Its purpose is discovery and validation.

---

## 测试数据来源 / Test Data Sources

**测试账户**: `docs/e2e_test_accounts.yaml`
**RBAC 权限矩阵**: `docs/e2e_rbac_matrix.yaml`
**工作流定义**: `docs/e2e_workflows.md`

---

## 核心测试领域 / Core Test Areas

本技能必须评估：/ The skill must evaluate:
- 认证流程 / authentication flow
- RBAC 权限行为（每个角色 × 每个权限）/ RBAC permission behavior (every role x every permission)
- 组织数据范围 / organization data scope
- 工作流可用性 / workflow usability
- 导航清晰度 / navigation clarity
- UI 状态反馈 / UI state feedback
- 通知行为 / notification behavior
- 审计日志生成 / audit log generation
- 仪表盘正确性 / dashboard correctness
- 个人设置探索 / personal settings exploration
- 困惑时刻检测 / confusion moments detection
- 工作流引导可见性 / workflow guidance visibility
- 跨角色工作流集成 / cross-role workflow integration

---

## RBAC 权限测试策略 / RBAC Permission Testing Strategy

### 完整权限矩阵测试 / Full Permission Matrix Test

对于每个角色，测试 `docs/RBAC_PERMISSION_MATRIX.md` 中列出的每个权限。/ For every role, test EVERY permission listed in `docs/RBAC_PERMISSION_MATRIX.md`.

测试账户来源: `docs/e2e_test_accounts.yaml`
期望权限矩阵来源: `docs/e2e_rbac_matrix.yaml`

### RBAC 测试序列 / RBAC Test Sequence

1. **以 taidongxu 登录 (TEAM_LEADER)** — 测试 `order:list`, `order:create`, `order:submit`, `order:view`, `order:final_confirm`, `notification:view`, `notification:create`, `tool:search`, `tool:view`
   - 验证 403: `order:keeper_confirm`, `order:transport_execute`, `notification:send_feishu`

2. **以 hutingting 登录 (KEEPER)** — 测试 `order:list`, `order:view`, `order:keeper_confirm`, `order:final_confirm`, `order:transport_execute`, `order:cancel`, `notification:*`, `tool:*`, `log:view`
   - 验证 403: `order:create`, `order:submit`, `admin:*`

3. **以 fengliang 登录 (PRODUCTION_PREP)** — 测试 `tool:search`, `tool:view`, `tool:location_view`, `order:transport_execute`, `order:pre_transport`
   - 验证 403: `order:create`, `order:list`, `order:view`, `notification:view`, `dashboard:view`

4. **以 admin 登录 (SYS_ADMIN)** — 测试所有权限，包括 `admin:user_manage`, `admin:role_manage`, `order:delete`

---

## 工作流测试 / Workflow Testing

### 完整出库工作流 / Full Outbound Workflow

详见 `docs/e2e_workflows.md` — 包含完整 ASCII 流程图。

出库流程: taidongxu(TEAM_LEADER) 创建提交 → hutingting(KEEPER) 确认驳回重提 → fengliang(PRODUCTION_PREP) 运输 → taidongxu 最终确认 → admin 删除

### 完整入库工作流 / Full Inbound Workflow

详见 `docs/e2e_workflows.md`。

入库流程: taidongxu(TEAM_LEADER) 创建提交 → hutingting(KEEPER) 确认 → fengliang(PRODUCTION_PREP) 运输 → hutingting 最终确认（保管员做最终确认）

### 工作流状态定义 / Workflow State Definitions

| 状态 | 中文 | 说明 | 可执行操作 |
|------|------|------|-----------|
| `draft` | 草稿 | 订单刚创建 | submit, delete |
| `submitted` | 已提交 | 等待保管员确认 | keeper_confirm, cancel |
| `keeper_confirmed` | 保管员已确认 | 工装已确认，运输已指派 | transport_start, cancel |
| `transport_notified` | 运输已通知 | 运输人员已通知 | transport_start, cancel |
| `transport_in_progress` | 运输中 | 运输执行中 | transport_complete |
| `transport_completed` | 运输完成 | 等待最终确认 | final_confirm |
| `completed` | 已完成 | 订单完成 | (read only) |
| `rejected` | 已拒绝 | 订单被拒绝 | (read only) |

---

## 阶段执行 / Phase Execution

### 阶段 1：探索行为 / Phase 1: Exploration Behavior

语义驱动导航 — 点击动作动词按钮（"创建"、"提交"、"确认"），悬停图标，访问每个可见菜单项，探索下拉和嵌套导航。

必须访问的菜单项: 仪表盘、订单列表、保管员处理、个人设置

### 阶段 2：RBAC 权限验证 / Phase 2: RBAC Permission Verification

对每个角色验证：菜单可见性、按钮可见性、API 访问、数据范围

### 阶段 3：完整工作流测试 / Phase 3: Complete Workflow Test

执行完整出库（含驳回重提循环）或入库工作流，验证每个步骤的状态转换和操作按钮。

### 阶段 4：个人设置 / Phase 4: Personal Settings

访问设置页面，验证个人信息、密码修改、主题切换、Bug 反馈。

### 阶段 5：困惑指标 / Phase 5: Confusion Metrics

| 指标 | 阈值 | 含义 |
|------|------|------|
| 页面停留时间 | >30 秒 | 用户可能困惑 |
| 重复失败操作 | >2 次 | 用户不理解 |
| 废弃的草稿 | 创建但未提交 | 工作流不清晰 |
| 导航循环 | 多次访问同一页面 | 用户迷失 |

### 阶段 6：自愈集成 / Phase 6: Self-Healing Integration

发现问题后：分析 → 生成提示词 → 执行修复 → 重新测试
发现关键 bug 时立即触发 `self-healing-dev-loop`。

---

## 端口要求 / Port Requirements

**强制端口检查 — 必须在测试前验证服务正在运行 / MANDATORY PORT CHECK**

| 服务 | 端口 | URL |
|------|------|-----|
| 前端 | 8150 | http://localhost:8150 |
| 后端 | 8151 | http://localhost:8151 |

如果端口 8150/8151 上的服务未运行，立即退出，不要做任何操作。

---

## 执行步骤 / Execution Steps

### 步骤 0 — 端口检查

```powershell
$frontend = Test-NetConnection -ComputerName localhost -Port 8150 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
$backend = Test-NetConnection -ComputerName localhost -Port 8151 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if (-not $frontend.TcpTestSucceeded -or -not $backend.TcpTestSucceeded) {
    Write-Host "[ABORT] Services not ready" -ForegroundColor Red
    exit 1
}
```

### 步骤 1 — 启动测试

使用 `test_runner/commands.py` 管理测试状态：

```python
from test_runner.commands import start, status, advance, resume, stop

# 开始新测试
result = start("full_workflow")  # full_workflow / quick_smoke / rbac

# 查看状态
current = status()

# 推进测试（在每个步骤后调用）
advance("login_taidongxu", anomalies_count=0, critical_count=0)

# 继续测试（auto-compact 后）
resume()

# 停止测试
stop("测试完成")
```

### 断点续传 / Checkpoint Resume

| 触发条件 | 行为 |
|---------|------|
| 每 10 步骤 | 强制断点，写入 SQLite |
| 发现 critical 异常 | 立即暂停 |
| 主会话调用 `stop` | Agent 状态 = IDLE |
| auto-compact | Agent 进程不受影响，主会话通过 `resume` 恢复 |

### 测试类型 / Test Types

| 类型 | 说明 | 调用 |
|------|------|------|
| `full_workflow` | 完整出库工作流（22 步骤） | `start("full_workflow")` |
| `quick_smoke` | 快速冒烟测试（5 步骤） | `start("quick_smoke")` |
| `rbac` | RBAC 权限测试（5 步骤） | `start("rbac")` |

---

## 期望输出 / Expected Output

执行后生成报告，包含：

- **测试元数据**: 日期、测试人员、系统、测试用户
- **执行摘要**: 总体结果 (PASS/FAIL/CRITICAL ISSUES)、关键指标
- **RBAC 权限测试结果**: 期望 vs 实际权限行为完整矩阵
- **工作流测试结果**: 每个阶段通过/失败状态
- **发现的问题**: 按严重性分类，含描述和推荐修复
- **困惑指标**: 停留时间、重复失败、废弃草稿、导航循环
- **自愈建议**: 应触发 self-healing-dev-loop 的问题

---

## 完成标准 / Completion Criteria

技能完成当且仅当：

1. [ ] 端口检查通过（8150 和 8151 服务运行）
2. [ ] 所有 4 个角色的 RBAC 权限矩阵已验证
3. [ ] 完整出库或入库工作流已端到端测试
4. [ ] 个人设置页面已探索
5. [ ] 测试报告已生成并保存到 `test_reports/`
6. [ ] 发现的关键问题已触发 `self-healing-dev-loop`（如适用）

---

## 约束 / Constraints

本技能严禁：

- 在服务未运行时继续测试 / Do NOT proceed if services are not running
- 使用 `docs/e2e_test_accounts.yaml` 以外的测试账户
- 修改生产代码
- 假设 API 结构而不验证
