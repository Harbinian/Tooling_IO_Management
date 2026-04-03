# Bug 修复提示词 / Bug Fix Prompt

## 头部 / Header

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10196
Goal: 修复订单提交/创建 API 的重复提交防护和取消订单 400 错误
Dependencies: None
Execution: RUNPROMPT

---

## D1 - 团队分工 / Team Assignment

| 角色 | 职责 |
|------|------|
| Reviewer | 分析根因和方案评审 |
| Coder | 检查源码并实施修复 |

---

## D2 - 问题描述 / Problem Description

**What (发生了什么)**
- 用户在订单创建页面点击"提交"按钮后，页面没有跳转
- 用户再次点击提交按钮后，系统报"锁"错误
- `POST /tool-io-orders` 返回 400 (重复创建)
- `POST /tool-io-orders/TO-OUT-20260402-010/cancel` 返回 400

**Where (在哪里)**
- 后端: `backend/services/tool_io_service.py`
- 前端: `frontend/src/pages/tool-io/OrderCreate.vue`

**When (何时发生)**
- 订单创建 → 提交流程中

**Who (谁)**
- 班组长角色用户

**Why (为什么是问题)**
- 前端提交回调没有正确处理成功响应，导致用户认为提交失败而再次点击
- 重复点击产生并发重复提交
- 取消订单 API 状态机校验不通过

**How (如何复现)**
1. 登录为班组长
2. 进入订单创建页面
3. 填写工装明细
4. 点击提交按钮
5. 观察页面不跳转，再次点击后报锁

---

## D3 - 临时遏制措施 / Containment

**前端临时修复**
- 在 `OrderCreate.vue` 的提交按钮上添加防抖/节流装饰器，防止重复点击
- 检查提交成功回调是否正确触发路由跳转

**后端临时修复**
- 检查 `submit_order` 和 `create_order` 的幂等性逻辑

---

## D4 - 根因分析 / Root Cause Analysis

**必须执行以下检查：**

1. **读取后端日志** - 查看 `logs/` 目录下最近的日志文件，分析 400 错误的详细原因
2. **检查 `tool_io_service.py`**:
   - `create_order` 方法：是否有重复订单检查？是否在提交后返回订单号？
   - `submit_order` 方法：提交成功后的返回值是什么？
   - `cancel_order` 方法：状态机校验逻辑是什么？哪些状态不允许取消？
3. **检查 `OrderCreate.vue`**:
   - `submitCreatedOrder` 函数的成功回调处理
   - 是否正确处理了 `createOrder` 返回的订单号用于后续 submit？
4. **检查数据库订单状态** - `TO-OUT-20260402-010` 当前状态是什么？是否允许取消？

---

## D5 - 永久对策 + 防退化宣誓 / Permanent Fix + Anti-Regression

**必须实施：**

1. **前端 - 提交后跳转逻辑修复**
   - `createOrder` 成功后必须立即跳转到订单详情页或刷新列表
   - 添加提交按钮 loading 状态管理

2. **后端 - 取消订单状态机检查**
   - 明确哪些状态允许/禁止取消
   - 返回明确的错误信息而非 400

3. **后端 - 重复提交防护（如果缺失）**
   - 检查订单号是否已存在，如存在则返回已有订单而非 400

**防退化誓言：**
- 不修改 `column_names.py` 中的字段常量
- 不改变现有的 RBAC 权限逻辑
- 不修改数据库表结构

---

## D6 - 实施验证 / Implementation

**修复后必须验证：**

1. `POST /tool-io-orders` 提交后前端正确跳转
2. 重复点击不产生重复订单
3. `POST /tool-io-orders/<order_no>/cancel` 对正确状态的订单返回 200
4. `POST /tool-io-orders/<order_no>/cancel` 对不允许取消的状态返回明确错误码

---

## D7 - 预防复发 / Prevention

- 提交操作后前端必须立即跳转或显示成功消息，不留歧义
- API 层增加幂等性 key（可选优化）

---

## D8 - 归档复盘 / Documentation

- 记录根因和修复方案到 `logs/codex_rectification/`
- 更新 `docs/API_SPEC.md` 如有 API 行为变更

---

## 上下文 / Context

当前订单提交流程：
1. 前端 `OrderCreate.vue` 调用 `createOrder` (POST /tool-io-orders)
2. 成功后调用 `submitCreatedOrder` (POST /tool-io-orders/{order_no}/submit)

问题可能出在：
- `createOrder` 返回后前端没有使用返回的 order_no 进行 submit
- 或者 submit 本身失败了但前端没捕获到

---

## 必需参考 / Required References

| 文件路径 | 说明 |
|---------|------|
| `backend/services/tool_io_service.py` | 订单创建、提交、取消核心逻辑 |
| `frontend/src/pages/tool-io/OrderCreate.vue` | 订单创建页面，416行附近提交逻辑 |
| `frontend/src/api/orders.js` | 订单 API 封装 |
| `backend/routes/order_routes.py` | 订单 API 路由 |

---

## 约束条件 / Constraints

- 禁止修改 `column_names.py`
- 禁止修改数据库表结构
- 禁止改变 RBAC 权限逻辑
- 所有文件操作使用 `encoding='utf-8'`

---

## 完成标准 / Completion Criteria

- [ ] 订单提交后前端正确跳转到订单详情或刷新列表
- [ ] 重复点击提交按钮不会产生重复订单
- [ ] 取消订单 API 对允许取消的订单返回 200
- [ ] 取消订单 API 对不允许取消的订单返回明确错误信息（而非 400）
- [ ] 语法检查通过：`python -m py_compile backend/services/tool_io_service.py`
