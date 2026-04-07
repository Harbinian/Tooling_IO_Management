name: scripted-e2e-builder
executor: Codex
auto_invoke: false
depends_on:
  - human-e2e-tester
triggers: []
rules_ref:
  - .claude/rules/06_testing.md
version: 1.0.0
description: 将已验证的人工工作流转换为前端和后端的自动化端到端和回归测试脚本。/ Convert validated human workflows into automated end-to-end and regression test scripts for frontend and backend.

---

# 脚本化 E2E 构建器技能 / Scripted E2E Builder Skill

## 目的 / Purpose

此技能将手动验证的工作流转换为可重复的自动化测试。/ This skill converts manually validated workflows into repeatable automated tests.

它获取探索性测试的结果（如 human-e2e-tester 生成的报告）并将它们转换为结构化的自动化测试。/ It takes the results from exploratory testing (such as reports produced by human-e2e-tester) and transforms them into structured automated tests.

目标是确保关键的系统工作流随着系统演进保持稳定。/ The goal is to ensure that critical system workflows remain stable as the system evolves.

## RBAC 权限矩阵 / RBAC Permission Matrix

**权威来源**: `docs/RBAC_INIT_DATA.md` (source of truth)

### 角色定义 / Role Definitions

| Role ID | Role Name | Type | 说明 |
|---------|-----------|------|------|
| `ROLE_SYS_ADMIN` | 系统管理员 | system | 系统管理员，拥有所有权限 |
| `ROLE_TEAM_LEADER` | 班组长 | business | 创建订单、出库最终确认 |
| `ROLE_KEEPER` | 保管员 | business | 确认明细、拒绝订单、入库最终确认 |
| `ROLE_PLANNER` | 计划员 | business | 计划员，可创建和提交工装订单 |
| `ROLE_PRODUCTION_PREP` | 生产准备工 | business | 运输工装，负责运输执行 |
| `ROLE_AUDITOR` | 审计员 | system | 审计员，查看日志和报表 |

### 权限清单 / Permission Catalog

| Permission | Resource | Action |
|------------|----------|--------|
| `dashboard:view` | dashboard | view |
| `tool:search` | tool | search |
| `tool:view` | tool | view |
| `tool:location_view` | tool | location_view |
| `order:create` | order | create |
| `order:view` | order | view |
| `order:list` | order | list |
| `order:submit` | order | submit |
| `order:keeper_confirm` | order | keeper_confirm |
| `order:final_confirm` | order | final_confirm |
| `order:cancel` | order | cancel |
| `order:delete` | order | delete |
| `order:transport_execute` | order | transport_execute |
| `notification:view` | notification | view |
| `notification:create` | notification | create |
| `notification:send_feishu` | notification | send_feishu |
| `log:view` | log | view |
| `admin:user_manage` | admin | user_manage |
| `admin:role_manage` | admin | role_manage |

### 角色-权限矩阵 / Role-Permission Matrix

| 权限 | SYS_ADMIN | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|------|-----------|-------------|--------|---------|-----------------|---------|
| `dashboard:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `tool:search` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `tool:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `tool:location_view` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `order:create` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `order:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `order:list` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `order:submit` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| `order:keeper_confirm` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `order:final_confirm` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `order:cancel` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `order:delete` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `order:transport_execute` | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| `notification:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `notification:create` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `notification:send_feishu` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `log:view` | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| `admin:user_manage` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `admin:role_manage` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

## 何时使用此技能 / When To Use This Skill

在以下情况下使用此技能：/ Use this skill when:

- 人工模拟测试已验证工作流 / a human-simulated test has validated workflows
- Bug 已修复需要回归保护 / a bug has been fixed and needs regression protection
- 新工作流功能已完成 / a new workflow feature has been completed
- 正在准备发布候选版本 / a release candidate build is being prepared
- 在试发布或生产发布之前 / before pilot release or production release

此技能不应该发明新工作流。/ This skill should **not invent new workflows**.

它应该只将已验证的工作流转换为自动化测试。/ It should only convert verified workflows into automated tests.

## 输入 / Inputs

此技能应检查以下来源：/ The skill should inspect sources such as:

- `test_reports/HUMAN_SIMULATED_E2E_TEST_REPORT_*.md` (latest)
- `docs/RBAC_PERMISSION_MATRIX.md` (permission source of truth)
- `docs/API_SPEC.md` (API contract)

这些文档描述了应该被回归测试保护的真正用户流程。/ These documents describe real user flows that should be protected by regression tests.

## 核心职责 / Core Responsibilities

此技能必须：/ The skill must:

1. 识别关键工作流 / identify critical workflows
2. 将它们翻译成自动化测试场景 / translate them into automated test scenarios
3. 生成可维护的测试脚本 / generate maintainable test scripts
4. 确保测试验证成功路径和权限规则 / ensure tests validate both success paths and permission rules
5. 确保当系统行为破坏时测试清楚地失败 / ensure tests fail clearly when system behavior breaks

---

## 执行步骤 / Execution Steps

### Step 1 — 识别关键工作流 / Identify Critical Workflows

**关键约束：测试数据限制**

所有自动化测试必须仅使用以下测试工装数据：/ **CRITICAL CONSTRAINT: TEST DATA RESTRICTION**

| 字段 / Field | 值 / Value |
|-------------|-----------|
| 序列号 / Serial Number | T000001 |
| 工装图号 / Tooling Drawing Number | Tooling_IO_TEST |
| 工装名称 / Tool Name | 测试用工装 |
| 机型 / Model | 测试机型 |

提取关键场景：/ Extract key scenarios:

- 用户登录 / User login
- 工装搜索（搜索：T000001 或 Tooling_IO_TEST）/ Tool search
- 订单创建（仅使用测试工装）/ Order creation
- 订单提交 / Order submission
- 保管员确认 / Keeper confirmation
- 运输工作流 / Transport workflow
- 最终确认 / Final confirmation
- 仪表盘指标可见性 / Dashboard metrics
- **RBAC 权限验证 / RBAC permission validation**

### Step 2 — 构建后端 API 测试 / Build Backend API Tests

创建自动化 API 级测试以验证：/ Create automated API-level tests:

1. **认证端点** - POST /api/auth/login
2. **订单生命周期端点** - CRUD operations
3. **工装搜索端点** - GET /api/tools/search
4. **仪表盘指标端点** - GET /api/dashboard/metrics
5. **RBAC 权限执行** - 每个角色 x 每个权限

**RBAC API 测试矩阵 / RBAC API Test Matrix:**

| API Endpoint | Method | TEAM_LEADER | KEEPER | ADMIN |
|--------------|--------|-------------|--------|-------|
| /api/tool-io-orders | GET | 200 | 200 | 200 |
| /api/tool-io-orders | POST | 201 | 403 | 201 |
| /api/tool-io-orders/<order_no>/submit | POST | 200 | 403 | 200 |
| /api/tool-io-orders/<order_no>/keeper-confirm | POST | 403 | 200 | 200 |
| /api/tool-io-orders/<order_no>/final-confirm | POST | 200 | 200 | 200 |
| /api/tools/search | GET | 200 | 200 | 200 |
| /api/notifications | GET | 200 | 200 | 200 |

### Step 3 — 构建前端 E2E 测试 / Build Frontend E2E Tests

使用 Playwright 风格的测试：/ Use Playwright-style tests:

- 登录流程 / login flow
- 侧边栏导航 / sidebar navigation
- 仪表盘打开 / dashboard opening
- 订单创建 / order creation
- 订单提交 / order submission
- 保管员确认流程 / keeper confirmation flow
- 设置页面探索 / settings page exploration
- 主题切换 / theme toggle

### Step 4 — 验证 RBAC 场景 / Validate RBAC Scenarios

自动化测试必须确认：/ Automated tests must confirm:

1. **管理员 (SYS_ADMIN)** - 可以访问所有系统功能
2. **班组长 (TEAM_LEADER)** - 可以创建、提交订单，查看订单，确认出库最终确认，但不能执行保管员确认
3. **保管员 (KEEPER)** - 可以处理订单、确认明细、发送通知、执行运输，但不能创建/提交订单
4. **计划员 (PLANNER)** - 可以创建、提交、查看订单，搜索工具，但不能执行确认操作
5. **生产准备工 (PRODUCTION_PREP)** - 可以执行运输操作
6. **未授权用户** - 不能访问受保护页面（403）

### Step 5 — 验证数据范围 / Validate Data Scope

验证：/ Verify:

- 用户只能看到其组织范围内的数据
- 其他组织的订单不可见
- 仪表盘指标正确反映范围数据

### Step 6 — 添加回归覆盖 / Add Regression Coverage

确保以下功能保持被测试保护：/ Ensure coverage for:

- 订单工作流状态转换
- 通知创建
- 审计日志生成
- 仪表盘指标计算
- 工装位置更新
- **keeper_confirm API 返回正确的更新行数**

### Step 7 — 组织测试结构 / Organize Test Structure

```
tests/
├── api/
│   ├── test_auth.py
│   ├── test_orders.py
│   ├── test_tools.py
│   ├── test_dashboard.py
│   └── test_rbac_permissions.py
├── e2e/
│   ├── test_login_flow.py
│   ├── test_order_creation.py
│   ├── test_keeper_workflow.py
│   └── test_theme_toggle.py
├── rbac/
│   ├── test_team_leader_permissions.py
│   ├── test_keeper_permissions.py
│   └── test_admin_permissions.py
└── workflows/
    ├── test_outbound_workflow.py
    └── test_inbound_workflow.py
```

### Step 8 — 确保测试稳定性 / Ensure Test Stability

测试必须：/ Tests must:

- 避免脆弱的选择器
- 等待 UI 就绪 (element.is_visible())
- 失败时提供有意义的错误消息
- 使用确定性测试数据

### Step 9 — 生成文档 / Generate Documentation

创建文档: `docs/AUTOMATED_TEST_SUITE.md`

文档必须包括:
- 自动化工作流列表
- 已实现的 API 测试
- 已实现的 E2E 测试
- 已测试的 RBAC 场景
- 测试执行说明

---

## RBAC 测试脚本模板 / RBAC Test Script Template

```python
# tests/rbac/test_keeper_permissions.py

def test_keeper_can_confirm_orders():
    """KEEPER should be able to confirm orders"""
    response = api.keeper_confirm(order_no, items, user="keeper")
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_team_leader_cannot_confirm_orders():
    """TEAM_LEADER should NOT be able to confirm orders (403)"""
    response = api.keeper_confirm(order_no, items, user="team_leader")
    assert response.status_code == 403

def test_keeper_cannot_create_orders():
    """KEEPER should NOT be able to create orders (403)"""
    response = api.create_order(order_data, user="keeper")
    assert response.status_code == 403
```

## 预期结果 / Expected Outcome

执行后：/ After execution:

- 关键工作流受到自动化测试保护
- 前端导航被验证
- RBAC 规则自动验证
- 回归更容易检测
- 存在可维护的自动化测试套件
