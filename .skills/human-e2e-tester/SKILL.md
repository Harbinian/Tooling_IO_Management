# Human E2E Tester

命令触发: /human-e2e-tester / Command Trigger: /human-e2e-tester

---

name: human-e2e-tester
executor: Claude Code
description: Simulate real human end-to-end system usage across roles to discover workflow defects, RBAC issues, usability problems, and integration failures.

PURPOSE

This skill performs human-simulated exploratory testing of the system.

Unlike automated test scripts, this skill tries to behave like a real user.

It verifies whether the system is actually usable and whether workflows make sense from a human perspective.

This skill is especially useful before releases and after major feature changes.

This skill should NOT be used for writing code.

Its purpose is discovery and validation.

WHEN TO USE

Use this skill when:

- a major feature is completed
- RBAC logic changes
- workflow states change
- frontend navigation changes
- before pilot release
- before production release
- after self-healing-dev-loop fixes

This skill should NOT be used for writing code.

Its purpose is discovery and validation.

CORE TEST AREAS

The skill must evaluate:

- authentication flow
- RBAC permission behavior (every role x every permission)
- organization data scope
- workflow usability
- navigation clarity
- UI state feedback
- notification behavior
- audit log generation
- dashboard correctness
- personal settings exploration
- confusion moments detection
- workflow guidance visibility
- cross-role workflow integration

---

## TEST USERS

This skill uses real human-named test accounts. All users must belong to the same organization for RBAC data scope testing.

### Named Test Accounts

| User Name | Login Name | Password | Role | Role ID | Organization | Test Focus |
|-----------|------------|----------|------|---------|-------------|------------|
| 冯亮 | fengliang | test1234 | Production Prep (生产准备工) | ROLE_PRODUCTION_PREP | 同一组织 | 运输执行、位置查看 |
| 胡婷婷 | hutingting | test1234 | Keeper (保管员) | ROLE_KEEPER | 同一组织 | 订单确认、驳回、通知 |
| 太东旭 | taidongxu | test1234 | Team Leader (班组长) | ROLE_TEAM_LEADER | 同一组织 | 创建订单、提交、最终确认 |
| CA | admin | admin123 | System Administrator | ROLE_SYS_ADMIN | ALL | 管理权限、订单删除 |

**注意**: 太东旭的登录名是 `taidongxu`（非 taitongxu），密码已统一重置为 `test1234`。

---

## RBAC PERMISSION TESTING STRATEGY

### Full Permission Matrix Test

For every role, test EVERY permission listed in `docs/RBAC_PERMISSION_MATRIX.md`:

**Roles to Test:**
| Role ID | Role Name | Description | Org Scope |
|---------|-----------|-------------|-----------|
| `ROLE_SYS_ADMIN` | System Administrator (系统管理员) | 系统管理员，拥有所有权限 | ALL |
| `ROLE_TEAM_LEADER` | Team Leader (班组长) | 创建订单、出库最终确认 | SELF, ORG |
| `ROLE_KEEPER` | Keeper (保管员) | 确认明细、拒绝订单、入库最终确认 | ORG, ASSIGNED |
| `ROLE_PLANNER` | Planner (计划员) | 可创建和提交工装订单 | ORG, ORG_AND_CHILDREN |
| `ROLE_PRODUCTION_PREP` | Production Prep (生产准备工) | 运输工装，负责运输执行 | SELF, ORG |
| `ROLE_AUDITOR` | Auditor (审计员) | 审计员，查看日志和报表 | ALL |

**Permission Catalog to Test:**
| Permission | Resource | Action | Description |
|------------|----------|--------|-------------|
| `dashboard:view` | dashboard | view | 查看仪表盘 |
| `tool:search` | tool | search | 搜索工装 |
| `tool:view` | tool | view | 查看工装详情 |
| `tool:location_view` | tool | location_view | 查看工装位置 |
| `tool:status_update` | tool | status_update | 更新工装状态（保管员批量） |
| `order:create` | order | create | 创建订单 |
| `order:view` | order | view | 查看订单详情 |
| `order:list` | order | list | 查看订单列表 |
| `order:submit` | order | submit | 提交订单 |
| `order:keeper_confirm` | order | keeper_confirm | 保管员确认订单 |
| `order:final_confirm` | order | final_confirm | 最终确认订单 |
| `order:cancel` | order | cancel | 取消/拒绝订单 |
| `order:delete` | order | delete | 删除订单 |
| `order:transport_execute` | order | transport_execute | 执行运输任务 |
| `notification:view` | notification | view | 查看通知 |
| `notification:create` | notification | create | 创建通知 |
| `notification:send_feishu` | notification | send_feishu | 发送飞书通知 |
| `log:view` | log | view | 查看系统日志 |
| `admin:user_manage` | admin | user_manage | 管理用户 |
| `admin:role_manage` | admin | role_manage | 管理角色 |

### RBAC Test Matrix Format

For each role, produce a permission test result:

```
## RBAC Test: ROLE_TEAM_LEADER

| API Endpoint | Method | Permission | Expected | Actual | Status |
|--------------|--------|------------|----------|--------|--------|
| /api/tool-io-orders | GET | order:list | ✅ ALLOW | ??? | TEST |
| /api/tool-io-orders | POST | order:create | ✅ ALLOW | ??? | TEST |
| /api/tool-io-orders/<order_no>/submit | POST | order:submit | ✅ ALLOW | ??? | TEST |
...
```

### Expected Permission Matrix

**Source**: `docs/RBAC_PERMISSION_MATRIX.md` (authoritative source)

| 权限 | SYS_ADMIN | TEAM_LEADER | KEEPER | PLANNER | PRODUCTION_PREP | AUDITOR |
|------|-----------|-------------|--------|---------|-----------------|---------|
| `dashboard:view` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| `tool:search` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `tool:view` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `tool:location_view` | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| `tool:status_update` | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
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

---

## TEST DATA CONSTRAINT

All testing MUST use ONLY the following test tooling data:

| Field | Value |
|-------|-------|
| Serial Number (序列号) | T000001 |
| Tooling Drawing Number (工装图号) | Tooling_IO_TEST |
| Tool Name (工装名称) | 测试用工装 |
| Model (机型) | 测试机型 |

**DO NOT use any other tooling data for testing!**

---

## PHASE 1: EXPLORATION BEHAVIOR

**Semantic-Driven Navigation:**

- Click on buttons with action verbs (e.g., "创建", "提交", "确认")
- Hover over icons to see tooltips
- Visit every visible menu item in the sidebar
- Explore dropdown menus and nested navigation

**Required Menu Items to Visit:**
- Dashboard (首页)
- Order List (工装出入库)
- Keeper Process (保管员处理) - check role visibility
- Settings (个人设置)

---

## PHASE 2: RBAC PERMISSION VERIFICATION

### Test Each Role's Permissions

For each role, verify:

1. **Menu Visibility** - Only see menus allowed for role
2. **Button Visibility** - Only see action buttons allowed for role
3. **API Access** - Can/cannot call APIs based on permissions
4. **Data Scope** - Can only access own organization's data

### RBAC Test Sequence

#### 1. Login as 太东旭 (taidongxu / password: test1234) — TEAM_LEADER
**Test Permissions:**
- `order:list` - List own and org orders
- `order:create` - Create new orders
- `order:submit` - Submit orders for keeper approval
- `order:view` - View order details
- `order:final_confirm` - Final confirm outbound orders
- `notification:view` - View notifications
- `notification:create` - Create notifications
- `tool:search` - Search tools
- `tool:view` - View tool details

**Verify 403/Forbidden for:**
- `order:keeper_confirm` - Keeper-specific APIs return 403
- `order:transport_execute` - Transport APIs return 403
- `notification:send_feishu` - Feishu notification APIs return 403

#### 2. Login as 胡婷婷 (hutingting / password: test1234) — KEEPER
**Test Permissions:**
- `order:list` - List orders in org
- `order:view` - View order details
- `order:keeper_confirm` - Confirm order items
- `order:final_confirm` - Final confirm inbound orders
- `order:transport_execute` - Start/complete transport
- `order:cancel` - Reject orders
- `notification:view` - View notifications
- `notification:create` - Create notifications
- `notification:send_feishu` - Send Feishu notifications
- `tool:search` - Search tools
- `tool:view` - View tool details
- `tool:location_view` - View tool locations
- `tool:status_update` - Batch update tool status
- `log:view` - View system logs

**Verify 403/Forbidden for:**
- `order:create` - Create order APIs return 403
- `order:submit` - Submit order APIs return 403
- `admin:*` - Admin APIs return 403

#### 3. Login as 冯亮 (fengliang / password: test1234) — PRODUCTION_PREP
**Test Permissions:**
- `tool:search` - Search tools
- `tool:view` - View tool details
- `tool:location_view` - View tool locations
- `order:transport_execute` - Start/complete transport, report issues
- `order:pre_transport` - View pre-transport list

**Verify 403/Forbidden for:**
- `order:create` - Create order APIs return 403
- `order:list` - Order list APIs return 403 (EXCEPT pre-transport)
- `order:view` - Order detail APIs return 403
- `notification:view` - View notification APIs return 403
- `dashboard:view` - Dashboard APIs return 403

#### 4. Login as CA (admin / password: admin123) — SYS_ADMIN
**Test Permissions:**
- All permissions including `admin:user_manage`, `admin:role_manage`
- `order:delete` - Delete any order

---

## PHASE 3: COMPLETE WORKFLOW TEST — REJECTION AND RESUBMIT FLOW

### Scenario: Full Outbound with Keeper Rejection and Resubmit

This test executes a complete outbound workflow with an intentional keeper rejection and resubmit cycle.

```
┌──────────────────────────────────────────────────────────────────────────┐
│     出库完整流程（含驳回重提）/ Outbound Flow with Rejection & Resubmit        │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [太东旭 - taidongxu 班组长]                                              │
│       │                                                                 │
│       ▼                                                                 │
│  1. 创建订单 (order:create) ────────────────────────────────────────────│
│     订单类型: 出库 / Outbound                                             │
│     工装: T000001                                                        │
│       │                                                                 │
│       ▼                                                                 │
│  2. 提交订单 (order:submit)                                             │
│       │                                                                 │
│       ▼                                                                 │
│  [胡婷婷 - 保管员]                                                        │
│       │                                                                 │
│       ▼                                                                 │
│  3. 查看待确认订单列表 (order:list) ─ 状态: submitted                    │
│       │                                                                 │
│       ▼                                                                 │
│  4. 驳回订单 (order:cancel/reject) ─────────────────────────────────────│
│     填写驳回原因（测试用）                                                  │
│       │                                                                 │
│       ▼                                                                 │
│       状态变为: rejected                                                 │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                          第一轮：驳回重提                                 │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  [太东旭 - taidongxu 班组长]                                              │
│       │                                                                 │
│       ▼                                                                 │
│  5. 查看被驳回的订单                                                       │
│       │                                                                 │
│       ▼                                                                 │
│  6. 修改订单（补充/调整工装数量）                                           │
│       │                                                                 │
│       ▼                                                                 │
│  7. 再次提交订单 (order:submit)                                          │
│       │                                                                 │
│       ▼                                                                 │
│  [胡婷婷 - 保管员]                                                        │
│       │                                                                 │
│       ▼                                                                 │
│  8. 再次查看待确认订单列表                                                 │
│       │                                                                 │
│       ▼                                                                 │
│  9. 确认工装明细 (order:keeper_confirm)                                   │
│       │                                                                 │
│       ▼                                                                 │
│  10. 选择运输接收方 (assign-transport)                                     │
│       │                                                                 │
│       ▼                                                                 │
│  11. 发送运输通知 (notification:send_feishu)                             │
│       │                                                                 │
│       ▼                                                                 │
│  [冯亮 - 生产准备工]                                                      │
│       │                                                                 │
│       ▼                                                                 │
│  12. 查看预知运输列表 (pre-transport) ─ 状态: keeper_confirmed           │
│       │                                                                 │
│       ▼                                                                 │
│  13. 开始运输 (transport-start) ─ 状态: transport_in_progress            │
│       │                                                                 │
│       ▼                                                                 │
│  14. 完成运输 (transport-complete) ─ 状态: transport_completed           │
│       │                                                                 │
│       ▼                                                                 │
│  [太东旭 - taidongxu 班组长]                                              │
│       │                                                                 │
│       ▼                                                                 │
│  15. 最终确认 (order:final_confirm) ─ 状态: completed                    │
│       │                                                                 │
│       ▼                                                                 │
│  16. 验证工装位置更新                                                     │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                          清理：管理员删除订单                             │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  [CA - 系统管理员]                                                     │
│       │                                                                 │
│       ▼                                                                 │
│  17. 查看订单列表，找到已完成的订单                                         │
│       │                                                                 │
│       ▼                                                                 │
│  18. 删除订单 (order:delete) ─ 验证删除功能                               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Test Objectives

| Step | Objective | Expected Result |
|------|-----------|-----------------|
| 1-2 | TEAM_LEADER 创建并提交出库订单 | 订单状态: submitted |
| 3-4 | KEEPER 驳回订单，填写原因 | 订单状态: rejected |
| 5-7 | TEAM_LEADER 查看驳回原因，修改后重新提交 | 订单状态恢复: submitted |
| 8-11 | KEEPER 再次确认、指派运输、发送通知 | 订单状态: transport_notified |
| 12-14 | PRODUCTION_PREP 执行运输开始和完成 | 订单状态: transport_completed |
| 15-16 | TEAM_LEADER 最终确认，验证工装位置变更 | 订单状态: completed |
| 17-18 | SYS_ADMIN 删除已完成的订单 | 订单从前端列表消失 |

### Rejection-Resubmit Specific Checks

1. **Rejection Reason Visibility** — After keeper rejects, does team_leader see the rejection reason?
2. **Resubmit Flow** — Can team_leader edit and resubmit a rejected order?
3. **Status Reset** — Does order status properly reset to submitted after resubmit?
4. **Transport Assignment Persistence** — If keeper had assigned transport before rejection, is it cleared on resubmit?

---

## PHASE 3 (ALT): FULL OUTBOUND WORKFLOW (Standard)

### Full Outbound Workflow (出库流程)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   出库工作流 / Outbound Workflow (taidongxu)                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [太东旭 - taidongxu 班组长]                                              │
│       │                                                                 │
│       ▼                                                                 │
│  1. 创建订单 (order:create) ────────────────────────────────────────────│
│       │                                                                 │
│       ▼                                                                 │
│  2. 搜索工装 T000001 (tool:search)                                      │
│       │                                                                 │
│       ▼                                                                 │
│  3. 选择目的组织/车间                                                     │
│       │                                                                 │
│       ▼                                                                 │
│  4. 提交订单 (order:submit)                                             │
│       │                                                                 │
│       ▼                                                                 │
│  [胡婷婷 - 保管员]                                                        │
│       │                                                                 │
│       ▼                                                                 │
│  5. 查看待确认订单列表 (order:list) ─ 状态: submitted                    │
│       │                                                                 │
│       ▼                                                                 │
│  6. 确认工装明细 (order:keeper_confirm)                                  │
│       │                                                                 │
│       ▼                                                                 │
│  7. 选择运输接收方 (assign-transport)                                    │
│       │                                                                 │
│       ▼                                                                 │
│  8. 发送运输通知 (notification:send_feishu)                              │
│       │                                                                 │
│       ▼                                                                 │
│  [冯亮 - 生产准备工]                                                      │
│       │                                                                 │
│       ▼                                                                 │
│  9. 查看预知运输列表 (pre-transport) ─ 状态: keeper_confirmed           │
│       │                                                                 │
│       ▼                                                                 │
│  10. 开始运输 (transport-start) ─ 状态: transport_in_progress           │
│       │                                                                 │
│       ▼                                                                 │
│  [可选] 11. 上报异常 (report-transport-issue)                            │
│       │                                                                 │
│       ▼                                                                 │
│  12. 完成运输 (transport-complete) ─ 状态: transport_completed           │
│       │                                                                 │
│       ▼                                                                 │
│  [太东旭 - taidongxu 班组长]                                              │
│       │                                                                 │
│       ▼                                                                 │
│  13. 最终确认 (order:final_confirm) ─ 状态: completed                    │
│       │                                                                 │
│       ▼                                                                 │
│  14. 验证工装位置更新                                                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Full Inbound Workflow (入库流程)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   入库工作流 / Inbound Workflow (taidongxu)                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [太东旭 - taidongxu 班组长]                                              │
│       │                                                                 │
│       ▼                                                                 │
│  1. 创建订单 (order:create) ─ type: inbound                             │
│       │                                                                 │
│       ▼                                                                 │
│  2. 选择源组织/车间                                                      │
│       │                                                                 │
│       ▼                                                                 │
│  3. 提交订单 (order:submit)                                             │
│       │                                                                 │
│       ▼                                                                 │
│  [胡婷婷 - 保管员]                                                        │
│       │                                                                 │
│       ▼                                                                 │
│  5. 确认工装明细 (order:keeper_confirm)                                  │
│       │                                                                 │
│       ▼                                                                 │
│  7. 选择运输接收方 (assign-transport)                                    │
│       │                                                                 │
│       ▼                                                                 │
│  8. 发送运输通知 (notification:send_feishu)                              │
│       │                                                                 │
│       ▼                                                                 │
│  [冯亮 - 生产准备工]                                                      │
│       │                                                                 │
│       ▼                                                                 │
│  10. 开始运输 (transport-start)                                          │
│       │                                                                 │
│       ▼                                                                 │
│  12. 完成运输 (transport-complete)                                       │
│       │                                                                 │
│       ▼                                                                 │
│  [胡婷婷 - 保管员]                                                        │
│       │                                                                 │
│       ▼                                                                 │
│  13. 最终确认 (order:final_confirm) ─ 入库由KEEPER最终确认                │
│       │                                                                 │
│       ▼                                                                 │
│  14. 验证工装位置更新                                                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Workflow State Definitions

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

### API Endpoints by Workflow Step

| Step | API | Method | Permission | Role |
|------|-----|--------|------------|------|
| 创建订单 | `/api/tool-io-orders` | POST | order:create | TEAM_LEADER, PLANNER |
| 搜索工装 | `/api/tools/search` | GET | tool:search | TEAM_LEADER, KEEPER, PLANNER, PRODUCTION_PREP |
| 提交订单 | `/api/tool-io-orders/<order_no>/submit` | POST | order:submit | TEAM_LEADER, PLANNER |
| 查看待确认 | `/api/tool-io-orders` | GET | order:list | TEAM_LEADER, KEEPER, PLANNER |
| 保管员确认 | `/api/tool-io-orders/<order_no>/keeper-confirm` | POST | order:keeper_confirm | KEEPER |
| 指派运输 | `/api/tool-io-orders/<order_no>/assign-transport` | POST | order:keeper_confirm | KEEPER |
| 发送通知 | `/api/tool-io-orders/<order_no>/notify-transport` | POST | notification:send_feishu | KEEPER |
| 预知列表 | `/api/tool-io-orders/pre-transport` | GET | order:transport_execute | PRODUCTION_PREP |
| 开始运输 | `/api/tool-io-orders/<order_no>/transport-start` | POST | order:transport_execute | KEEPER, PRODUCTION_PREP |
| 上报异常 | `/api/tool-io-orders/<order_no>/report-transport-issue` | POST | order:transport_execute | PRODUCTION_PREP |
| 查看异常 | `/api/tool-io-orders/<order_no>/transport-issues` | GET | order:keeper_confirm | KEEPER |
| 处理异常 | `/api/tool-io-orders/<order_no>/resolve-transport-issue` | POST | order:keeper_confirm | KEEPER |
| 完成运输 | `/api/tool-io-orders/<order_no>/transport-complete` | POST | order:transport_execute | KEEPER, PRODUCTION_PREP |
| 最终确认 | `/api/tool-io-orders/<order_no>/final-confirm` | POST | order:final_confirm | TEAM_LEADER (出库), KEEPER (入库) |
| 取消订单 | `/api/tool-io-orders/<order_no>/cancel` | POST | order:cancel | TEAM_LEADER, KEEPER |

### Key Differences: Outbound vs Inbound

| 差异点 | 出库 (Outbound) | 入库 (Inbound) |
|--------|----------------|----------------|
| 创建者 | TEAM_LEADER | TEAM_LEADER |
| 方向 | 从仓库到车间 | 从车间到仓库 |
| 最终确认者 | TEAM_LEADER | KEEPER |
| 状态可见性 | TEAM_LEADER可监控全程 | TEAM_LEADER可监控全程 |

---

## PHASE 4: PERSONAL SETTINGS

1. **Find and Visit Settings Page**
2. **Profile Information** - name, role, permissions
3. **Password Change** - validation testing
4. **Theme Toggle** - dark/light mode persistence
5. **Bug Feedback** - category, subject, content

---

## PHASE 5: CONFUSION METRICS

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| Page residence time | >30 seconds | User may be confused |
| Repeated failed operations | >2 attempts | User doesn't understand |
| Abandoned drafts | Created but not submitted | Workflow unclear |
| Navigation loops | Same pages visited multiple times | User is lost |

---

## PHASE 6: SELF-HEALING INTEGRATION

After each test run, if issues are found:

1. **Analyze issues** using Dev Inspector
2. **Generate prompts** using Auto Task Generator
3. **Execute fixes** via RUNPROMPT
4. **Re-test** the fixed functionality

If a critical bug is found during testing, immediately trigger self-healing-dev-loop.

---

## SENSING MODULE ARCHITECTURE

The skill includes a **perception framework** that gives the tester "eyes" — the ability to observe page state and detect anomalies, not just execute steps blindly.

### Four-Layer Sensing Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Test Agent (决策层)                                    │
│  - Maintains test intent and current context             │
│  - Decides next action based on sensing results          │
│  - Judges test pass/fail                                │
└─────────────────────────────────────────────────────────┘
            ▲                    │
            │ Sensing results     │ Action commands
            │                    ▼
┌─────────────────────────────────────────────────────────┐
│  PageContextObserver (页面感知层)                        │
│  - Reads current page DOM state                          │
│  - Perceives: elements, text, values, status labels     │
│  - Output: PageSnapshot                                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  WorkflowStateDetector (工作流感知层)                    │
│  - Infers order workflow position from snapshot          │
│  - Checks if available buttons match current state       │
│  - Detects illegal state transitions                    │
│  - Output: WorkflowPosition                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  AnomalyDetector (异常感知层)                           │
│  - Catches API errors (500/400/403)                    │
│  - Detects blank pages / empty lists / missing data     │
│  - Detects missing error messages / button no-response  │
│  - Output: AnomalyReport[]                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  DataConsistencyVerifier (数据一致性层)                  │
│  - List total = Detail total                           │
│  - Status label = Actual status                         │
│  - Tool quantities match                               │
│  - Rejection reason visible and non-empty               │
│  - Output: ConsistencyCheck[]                           │
└─────────────────────────────────────────────────────────┘
```

### Sensing Module Location

```
.skills/human-e2e-tester/
├── skill.md                          # This skill file
└── sensing/                          # Perception framework
    ├── __init__.py                   # Module exports
    ├── snapshot.py                   # Core data structures
    ├── page_observer.py              # Page perception layer
    ├── workflow_detector.py           # Workflow perception layer
    ├── anomaly_detector.py            # Anomaly perception layer
    ├── consistency_verifier.py        # Data consistency layer
    └── orchestrator.py                # Sensing coordinator
```

### Key Sensing Concepts

#### PageSnapshot
The core data structure that captures what a human "sees" on a page:

| Field | Description |
|-------|-------------|
| `page_name` | Page type: OrderList, OrderDetail, OrderCreate, etc. |
| `order_status` | Status label displayed (Chinese) |
| `table_rows` | Number of rows in table |
| `visible_buttons` | Buttons that are visible and clickable |
| `error_message` | Error message displayed (if any) |
| `fields` | Key fields and their values |

#### WorkflowPosition
Inferred workflow state:

| Field | Description |
|-------|-------------|
| `current_state` | Current state value (e.g. "draft", "submitted") |
| `current_state_label` | Current state label (e.g. "草稿", "已提交") |
| `available_actions` | Actions expected to be available |
| `forbidden_actions` | Actions that should NOT be available |

#### AnomalyReport
Detected anomaly:

| Field | Description |
|-------|-------------|
| `anomaly_type` | Type: api_500, status_mismatch, button_gone, etc. |
| `severity` | critical / high / medium / low |
| `description` | Human-readable description |
| `evidence` | Evidence: screenshots, API responses |

### How to Use Sensing in Test Steps

**Before each operation**, observe the current page:

```
>>> After loading OrderList page:
Snapshot: OrderList
  - URL: http://localhost:8150/tool-io
  - Order status: "已提交" (submitted)
  - Visible buttons: ["查看", "取消"]
  - Table rows: 3
  - Error: None

This tells me:
  - There are 3 submitted orders
  - I can view details or cancel (no submit button visible, correct for submitted state)
```

**After each operation**, verify the result:

```
>>> After clicking "确认" button:
  - Operation recorded: "keeper_confirm"
  - API called: POST /api/tool-io-orders/<order_no>/keeper-confirm
  - Response: 200 OK
  - Page changed to: "保管员已确认" (keeper_confirmed) ✓
  - New buttons visible: ["通知运输", "取消"] ✓
  - No error messages ✓

Anomalies detected: None
Consistency checks: All passed
```

### What the Sensor Can Detect

| Category | What it Detects | Example |
|----------|----------------|---------|
| **API Errors** | 500/400/403 responses | API returns 500 Internal Server Error |
| **Status Mismatch** | Label doesn't match actual state | Shows "已完成" but API says "submitted" |
| **Missing Button** | Action available but button absent | State is "submitted" but no "确认" button |
| **Extra Button** | Action not available but button shown | State is "completed" but "提交" still visible |
| **Silent Fail** | Operation clicked but no API call | Clicked "提交" but nothing happened |
| **Missing Error** | API failed but no error shown | API returned 400 but page shows no error |
| **Data Mismatch** | List total ≠ Detail total | List shows 5 tools, detail shows 3 |
| **Rejection Reason** | Rejected order has no reason | Order is "rejected" but reason field empty |
| **Gibberish Text** | Garbled characters in UI | Shows "鍒涘缓" instead of "创建" |

### Integrating Sensing into Test Execution

In each test step, the executor should:

1. **Before action**: Call `orchestrator.snapshot_before(driver)` to capture current state
2. **Execute action**: Perform the UI action (click button, fill form, etc.)
3. **After action**: Call `orchestrator.snapshot_after(driver, "action_name", api_response)` to analyze result
4. **Check anomalies**: If `orchestrator.has_blocking_issues()`, pause and report
5. **Continue or halt**: If critical anomaly found, consider triggering self-healing

Example flow:

```
STEP 3: Keeper confirms order (hutingting)

Before:
  Snapshot: OrderList - 3 submitted orders visible

Action:
  - Navigate to order detail
  - Click "确认明细" button
  - System calls API: POST /keeper-confirm
  - API returns: 200 { success: true }

After:
  Snapshot: OrderDetail - status now "保管员已确认"
  Expected next state: "keeper_confirmed" ✓
  Expected buttons: ["通知运输", "取消"] ✓
  Anomalies: None

→ Continue to next step
```

### Sensing Report

At the end of testing, the orchestrator generates a sensing report:

```json
{
  "summary": {
    "total_anomalies": 3,
    "critical": 1,
    "high": 1,
    "medium": 1,
    "passed_consistency_checks": 12,
    "failed_consistency_checks": 1
  },
  "anomalies": [
    {
      "type": "status_mismatch",
      "severity": "high",
      "description": "Status label shows '已提交' but actual is 'keeper_confirmed'",
      "order_no": "IO2026032601"
    }
  ],
  "workflow_positions": [...]
}
```

---

## PORT REQUIREMENTS

**MANDATORY PORT CHECK — MUST verify externally launched services are running before testing**

| Service | Port | URL |
|---------|------|-----|
| Frontend | 8150 | http://localhost:8150 |
| Backend | 8151 | http://localhost:8151 |

### Service Availability Check (MUST be performed before ANY testing)

User will manually start frontend and backend services on these ports externally before running this skill.

Verify services are running on the required ports:

```powershell
# Check if ports 8150 and 8151 are in use (services running)
$frontend = Test-NetConnection -ComputerName localhost -Port 8150 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
$backend = Test-NetConnection -ComputerName localhost -Port 8151 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if (-not $frontend.TcpTestSucceeded -or -not $backend.TcpTestSucceeded) {
    Write-Host "SERVICE NOT READY: Frontend (8150) and/or Backend (8151) are not responding" -ForegroundColor Red
    Write-Host "Frontend (8150): $($frontend.TcpTestSucceeded ? 'RUNNING' : 'NOT RUNNING')"
    Write-Host "Backend (8151): $($backend.TcpTestSucceeded ? 'RUNNING' : 'NOT RUNNING')"
    Write-Host ""
    Write-Host "Please start the services externally before running human-e2e-tester:"
    Write-Host "  Frontend: npm run dev (port 8150)"
    Write-Host "  Backend: python web_server.py (port 8151)"
    exit 1
}
```

### Service Not Running — Exit Rule

**IF SERVICES ARE NOT RUNNING on ports 8150/8151, IMMEDIATELY EXIT — DO NOTHING**

- Do NOT proceed with any testing
- Do NOT attempt to start services
- Do NOT modify any configuration
- Simply output the following message and exit:

```
[ABORT] Services not ready. Frontend (8150) and/or Backend (8151) are not responding.
Human E2E testing requires externally launched services on these specific ports.
Please start the services manually before running human-e2e-tester.
```

---

## EXECUTION STEPS

### TEST RUNNER AGENT 集成执行流程

本 skill 使用 **TestRunnerAgent** 管理测试步骤状态，使用 **SensingOrchestrator** 执行页面感知。两者通过 SQLite 数据库共享数据，不受 Claude Code auto-compact 影响。

#### Agent 命令接口（通过 subprocess 调用）

```bash
# Agent 状态管理
python test_runner/test_runner_agent.py --command start --test-type full_workflow
python test_runner/test_runner_agent.py --command resume
python test_runner/test_runner_agent.py --command status
python test_runner/test_runner_agent.py --command advance --current-operation "step_name" --anomalies-count N --critical-count N
python test_runner/test_runner_agent.py --command stop --reason "reason"

# 感知层查询
python test_runner/sensing_integration.py --command status
python test_runner/sensing_integration.py --command get_report
```

#### Python 命令模块（推荐）

```python
from test_runner.commands import start, resume, status, advance, stop

# 开始测试
start("full_workflow")   # full_workflow / quick_smoke / rbac

# 查看状态
status()

# 推进测试（在每个步骤执行后调用）
advance("login_taidongxu", anomalies_count=0, critical_count=0)

# 继续测试（auto-compact 后）
resume()

# 停止测试
stop("reason")
```

---

### 完整执行流程

#### STEP 0 — 端口检查

```powershell
$frontend = Test-NetConnection -ComputerName localhost -Port 8150 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
$backend = Test-NetConnection -ComputerName localhost -Port 8151 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if (-not $frontend.TcpTestSucceeded -or -not $backend.TcpTestSucceeded) {
    Write-Host "[ABORT] Services not ready" -ForegroundColor Red
    exit 1
}
```

#### STEP 1 — 启动 Agent

```python
from test_runner.commands import start, status

# 开始新测试（或恢复中断的测试）
result = start("full_workflow")

# 检查是否需要恢复
if result.get("state") == "RUNNING":
    # 已有测试在运行，检查是否需要 resume
    current = status()
    if current.get("operation_index", 0) > 0:
        print(f"发现未完成测试: operation={current['operation_index']}, next={current.get('next_operation')}")
        # 决定是否 resume 或重新开始
```

#### STEP 2 — 执行测试步骤

对每个测试步骤执行：

```
┌─────────────────────────────────────────────────────────────┐
│  STEP N: <操作名称>                                          │
│                                                             │
│  1. 调用 agent status 获取下一步操作                          │
│     current = status()                                     │
│     next_op = current["next_operation"]                    │
│                                                             │
│  2. 执行操作（Playwright/Selenium）                          │
│     - 登录 / 点击按钮 / 填写表单 / 提交                       │
│                                                             │
│  3. 感知页面状态（主会话内 import sensing 模块）             │
│     from sensing import SensingOrchestrator                 │
│     orch = SensingOrchestrator(db_path=db_path, run_id=run_id)│
│     snap, anomalies, checks = orch.snapshot_after(driver,    │
│                                              operation)     │
│                                                             │
│  4. 汇总异常数并推进 agent                                   │
│     critical = sum(1 for a in anomalies if a.severity=="critical")│
│     high = sum(1 for a in anomalies if a.severity=="high") │
│     result = advance(op_name, len(anomalies), critical)     │
│                                                             │
│  5. 检查是否暂停                                             │
│     if result.get("state") == "PAUSED":                     │
│         print(f"测试暂停: {result['message']}")             │
│         # 报告异常，等待指令                                 │
└─────────────────────────────────────────────────────────────┘
```

#### STEP 3 — 感知模块使用（主会话内）

```python
import sys
sys.path.insert(0, ".skills/human-e2e-tester")

from sensing import SensingOrchestrator

# 初始化（与 Agent 共用同一 db_path）
orch = SensingOrchestrator(
    db_path="test_reports/e2e_sensing.db",
    run_id="<from agent status>",
    test_type="full_workflow",
)

# 恢复上下文（如果 resume）
if orch.resumed_from_checkpoint:
    ctx = orch.context
    print(f"恢复: user={ctx.current_user}, order={ctx.current_order_no}")

# 设置用户上下文
orch.set_user_context("taidongxu", "TEAM_LEADER", "ORG001")

# 操作前快照
before = orch.snapshot_before(driver)

# 执行浏览器操作...

# 操作后快照 + 异常检测
snap, anomalies, checks = orch.snapshot_after(
    driver,
    operation="keeper_confirm",
    expected_next_status="keeper_confirmed",
)

# 检查阻断性问题
if orch.has_blocking_issues():
    print("发现阻断性异常，暂停测试")

# 检查是否触发自愈
if orch.should_trigger_self_healing():
    print("触发 self-healing-dev-loop")
```

#### STEP 4 — auto-compact 后的恢复

```
主会话被压缩 → 新主会话启动 → 检测到有未完成的测试 →

1. 调用 resume() 获取上次状态
   result = resume()
   run_id = result["run_id"]

2. 从 Agent 获取最后状态
   current = status()
   next_op = current["next_operation"]

3. 初始化 orchestrator 并恢复上下文
   orch = SensingOrchestrator(db_path=db_path, run_id=run_id)

4. 继续从 next_op 执行
```

#### STEP 5 — 完成测试

```python
from test_runner.commands import stop
from test_runner.sensing_integration import cmd_get_report

# 停止 Agent
stop("测试完成")

# 获取完整感知报告
report = cmd_get_report(db_path="test_reports/e2e_sensing.db")

# 生成人类可读报告
create_human_readable_report(report)
```

---

### 测试类型对应的 Agent 剧本

| test_type | 说明 | 调用 |
|-----------|------|------|
| `full_workflow` | 完整出库工作流（22 步骤） | `start("full_workflow")` |
| `quick_smoke` | 快速冒烟测试（5 步骤） | `start("quick_smoke")` |
| `rbac` | RBAC 权限测试（5 步骤） | `start("rbac")` |

---

### 断点续传条件

| 触发条件 | 行为 |
|---------|------|
| 每 10 步骤 | 强制断点，写入检查点到 SQLite |
| 发现 critical 异常 | 立即暂停，Agent 状态 = PAUSED |
| 主会话调用 `stop` | Agent 状态 = IDLE，测试中断 |
| auto-compact | Agent 进程不受影响，主会话通过 `resume` 恢复 |

---

### 快速冒烟测试流程（无感知层）

```
start("quick_smoke")
→ login (taidongxu)
→ view_order_list
→ create_simple_order
→ stop
```

### 完整出库测试流程（带感知）

```
start("full_workflow")
→ login_taidongxu
→ wait_page_load
→ create_order_start
→ create_order_verify
→ submit_order_start
→ submit_order_verify
→ switch_user_hutingting
→ keeper_view_orders
→ keeper_confirm_start
→ keeper_confirm_verify
→ notify_transport_start
→ notify_transport_verify
→ switch_user_fengliang
→ transport_view
→ transport_start
→ transport_complete
→ switch_user_taidongxu_final
→ final_confirm_start
→ final_confirm_verify
→ verify_completed
→ stop
```

---

### 感知报告输出格式

```json
{
  "run_id": "uuid",
  "test_type": "full_workflow",
  "status": "completed",
  "summary": {
    "total_anomalies": 3,
    "severity_counts": {
      "critical": 1,
      "high": 1,
      "medium": 1,
      "low": 0
    },
    "passed_consistency_checks": 12,
    "failed_consistency_checks": 1
  },
  "anomalies": [
    {
      "anomaly_type": "status_mismatch",
      "severity": "high",
      "description": "Status label shows '已提交' but actual is 'keeper_confirmed'",
      "order_no": "IO2026032601"
    }
  ],
  "workflow_positions": [...]
}
```

---

## EXPECTED OUTPUT

After execution:

- Full RBAC permission matrix verified
- Complete workflow tested end-to-end
- All issues classified and documented
- Test report generated
- Self-healing triggered for any critical issues

---

## REPORT REQUIREMENTS

The report must include:

### Test Metadata
- Date, Tester, System, Test Users
- Backend/Frontend URLs

### Executive Summary
- Overall result (PASS/FAIL/CRITICAL ISSUES)
- Key metrics (total steps, passed, failed, blocked, issues found)

### Test Users Table
| User | Login Name | Role | Organization | Permissions |

### RBAC Permission Test Results
Full matrix of expected vs actual permission behavior

### Workflow Test Results
Each phase with pass/fail status and findings

### Issues Found
Categorized by severity with description and recommended fix

### Confusion Metrics
| Metric | Value | Notes |

### Self-Healing Recommendations
Any issues that should trigger self-healing-dev-loop

---

## TEST RUNNER AGENT

### 为什么需要 Test Runner Agent？

Claude Code 的 auto-compact 会在测试过程中压缩上下文，导致测试状态丢失。Test Runner Agent 是一个**独立的后台进程**，不受 auto-compact 影响，维护完整的测试状态。

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│  Test Runner Agent (后台进程)                                │
│                                                             │
│  - 独立 Python 进程                                         │
│  - 状态持久化到 test_reports/e2e_sensing.db              │
│  - 不受 Claude Code auto-compact 影响                       │
│  - 通过文件系统与主会话通信                                  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ 消息/指令
                            │
┌─────────────────────────────────────────────────────────────┐
│  主会话 (Claude Code)                                        │
│                                                             │
│  - 发送指令："开始测试"、"继续测试"、"查看状态"、"停止"        │
│  - 接收报告：进度摘要、异常发现                                │
│  - 上下文只保留：当前报告 + 下一步指令                        │
└─────────────────────────────────────────────────────────────┘
```

### Agent 文件结构

```
test_runner/
├── __init__.py
├── test_runner_agent.py      # Agent 核心逻辑
└── commands.py               # 命令行工具

.skills/human-e2e-tester/sensing/
├── storage.py                 # SQLite 存储
├── orchestrator.py           # 感知协调器
└── ...

.claude/agents/
└── test-runner.md            # Agent 定义
```

### Agent 命令

| 命令 | 说明 |
|------|------|
| `start` | 开始新测试 |
| `resume` | 继续最近的测试 |
| `status` | 查询当前状态 |
| `stop` | 停止测试 |
| `report` | 获取完整报告 |

### 使用方法

**方法 1：直接运行**

```bash
# 开始测试
python test_runner/test_runner_agent.py --command start --test-type full_workflow

# 查看状态
python test_runner/test_runner_agent.py --command status

# 继续测试
python test_runner/test_runner_agent.py --command resume

# 获取报告
python test_runner/test_runner_agent.py --command report

# 停止测试
python test_runner/test_runner_agent.py --command stop --reason "done"
```

**方法 2：使用 commands 模块**

```python
from test_runner.commands import start, status, resume, report, stop

# 开始测试
result = start("full_workflow")

# 查看状态
result = status()

# 继续测试
result = resume()

# 获取报告
result = report()

# 停止
result = stop("user request")
```

**方法 3：在 Claude Code 中使用 Agent**

使用 Agent 工具启动后台 Agent：

```
Agent: test-runner
Prompt: 在后台执行完整工作流测试，使用 resume 命令继续最近的测试
run_in_background: true
```

### Agent 状态机

```
IDLE → RUNNING → PAUSED → COMPLETED
           ↓
        FAILED
```

- **IDLE**: 没有测试运行
- **RUNNING**: 测试执行中
- **PAUSED**: 测试暂停（断点或发现 critical 异常）
- **COMPLETED**: 测试完成
- **FAILED**: 测试失败

### 状态文件

| 文件 | 说明 |
|------|------|
| `test_reports/.agent_command.json` | 命令文件（主会话写入，Agent 读取） |
| `test_reports/.agent_status.json` | 状态文件（Agent 写入，主会话读取） |
| `test_reports/.agent.pid` | Agent 进程 PID |
| `test_reports/e2e_sensing.db` | SQLite 数据库 |

### 断点续传流程

1. **开始测试**
   ```
   主会话 → start 命令 → Agent 开始执行 → 每 10 步断点 → 数据写入 SQLite
   ```

2. **auto-compact 发生**
   ```
   Claude Code 上下文被压缩 → 但 Agent 进程不受影响 → 测试继续在后台执行
   ```

3. **续传**
   ```
   新主会话 → resume 命令 → Agent 从 SQLite 恢复状态 → 继续执行
   ```

### 测试类型

| 类型 | 说明 | 步骤数 |
|------|------|--------|
| `full_workflow` | 完整出库工作流 | 22 |
| `rbac` | RBAC 权限测试 | 5 |
| `quick_smoke` | 快速冒烟测试 | 5 |

### 输出示例

**status 命令响应：**

```json
{
  "success": true,
  "status": {
    "state": "RUNNING",
    "run_id": "abc123-def456",
    "test_type": "full_workflow",
    "operation_index": 15,
    "total_operations": 30,
    "current_operation": "keeper_confirm",
    "next_operation": "notify_transport",
    "anomalies_count": 2,
    "critical_count": 0,
    "high_count": 1,
    "last_updated": "2026-03-26T10:30:00",
    "message": "Test running"
  }
}
```

### 注意事项

1. **Agent 必须手动启动**：Claude Code 不会自动启动后台 Agent
2. **停止时清理**：测试完成后使用 `stop` 命令清理 Agent 进程
3. **数据库保留**：测试数据保留在 SQLite 中，可以多次查询报告
4. **PID 文件**：如果 Agent 崩溃，手动删除 `.agent.pid` 文件
