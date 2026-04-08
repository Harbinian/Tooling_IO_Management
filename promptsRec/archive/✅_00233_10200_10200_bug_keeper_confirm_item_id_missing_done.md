# Bug Fix: keeper-confirm API 400 Error - item_id Missing

**规则约束**: 本提示词遵循 `.claude/rules/02_debug.md` (8D 问题解决协议)。

---

## D1 - 团队分工 / Team Assignment

| 角色 | 负责人 |
|------|--------|
| **Reviewer** | Claude Code |
| **Coder** | Codex |
| **Architect** | Claude Code |

---

## D2 - 问题描述 / Problem Description (5W2H)

| 项目 | 内容 |
|------|------|
| **What** | 保管员确认时 API 返回 HTTP 400，所有工装明细项更新被跳过 |
| **Where** | `POST /api/tool-io-orders/:order_no/keeper-confirm` |
| **When** | 用户在 KeeperProcess.vue 点击"确认通过"按钮时 |
| **Who** | keeper 角色用户 |
| **Why** | 前端 approveOrder() 发送的 items 数组缺少 item_id（数据库主键） |
| **How** | HTTP 400，错误信息: `no items were updated - check item identifiers` |

---

## D3 - 临时遏制措施 / Containment

**立即修复**: 在 `KeeperProcess.vue` 的 `approveOrder` 函数中，`items` 数组需要包含 `item_id` 字段。

**验证方法**: 修复后重新执行 keeper-confirm 操作，观察 HTTP 响应码是否为 200。

---

## D4 - 根因分析 / Root Cause Analysis (5 Whys)

1. **Why**: keeper-confirm API 返回 400 错误
2. **Why**: 后端 `keeper_confirm()` 中 `updated_items_count == 0`，抛出 ValueError
3. **Why**: 每个 item 的 `item_id` 为 None/空，导致所有 item 被 `continue` 跳过
4. **Why**: 前端 `approveOrder()` 发送的 items 只有 `tool_code`，没有 `item_id`
5. **Why**: `buildEditableItems()` 虽然通过 `...item` 保留了 `id`（item_id），但 `approveOrder()` 未将其提取发送

**根因**: `approveOrder()` 函数（KeeperProcess.vue:767-775）缺少 `item_id` 字段的传递。

---

## D5 - 永久对策 + 防退化宣誓 / Permanent Fix & Regression Prevention

### 修复方案

**文件**: `frontend/src/pages/tool-io/KeeperProcess.vue`

**修改位置**: `approveOrder` 函数（约第 767-775 行）

**修改内容**: 在 `items` 映射中添加 `item_id: item.id`

```javascript
// 修改前
items: confirmItems.value.map((item) => ({
  tool_code: item.toolCode,
  location_id: null,
  // ... 缺少 item_id
}))

// 修改后
items: confirmItems.value.map((item) => ({
  item_id: item.id,  // ← 新增
  tool_code: item.toolCode,
  location_id: null,
  // ... 其余字段保持不变
}))
```

### 防退化宣誓

- `buildEditableItems()` 通过 `...item` 展开已保留 `id` 字段，此修改仅需提取发送
- 不修改任何后端接口或数据模型
- 修复后 keeper-confirm 必须返回 200 且订单状态变为 `keeper_confirmed`

---

## D6 - 实施验证 / Implementation

### 修改文件

1. `frontend/src/pages/tool-io/KeeperProcess.vue` - approveOrder 函数

### 验证步骤

1. 确认 `item.id` 在 `confirmItems` 中存在（通过 `buildEditableItems` 保留）
2. 确认 `approveOrder` 发送的 items 包含 `item_id` 字段
3. 调用 keeper-confirm API 验证返回 200
4. 检查数据库订单状态已更新为 `keeper_confirmed`

---

## D7 - 预防复发 / Prevention

- **自动化检测**: 在 `approveOrder` 调用前增加 console.log 调试，确认 item_id 存在
- **代码审查**: 确认所有 API 调用中 items 数组都包含主键字段

---

## D8 - 归档复盘 / Documentation

待修复完成后归档。

---

## Context / 上下文

保管员确认（keeper-confirm）是工装出入库的核心工作流步骤。订单状态为 `submitted` 时，keeper 需要确认每个工装明细项后才能推进流程。当前此功能完全阻塞。

---

## Required References / 必需参考

| 文件 | 说明 |
|------|------|
| `frontend/src/pages/tool-io/KeeperProcess.vue` | keeper-confirm 前端逻辑，approveOrder 函数 |
| `frontend/src/api/orders.js` | keeperConfirmOrder API 封装 |
| `backend/database/repositories/order_repository.py` | keeper_confirm Repository 层，期望 item_id |

---

## Constraints / 约束条件

- 仅修改前端 `KeeperProcess.vue`，不修改后端接口
- `item_id` 来自 `confirmItems` 中的 `item.id`（已由 `buildEditableItems` 保留）
- 不得修改后端 API 契约

---

## Completion Criteria / 完成标准

- [ ] `approveOrder` 函数发送的 items 包含 `item_id` 字段
- [ ] keeper-confirm API 返回 HTTP 200（不是 400）
- [ ] 订单状态从 `submitted` 变为 `keeper_confirmed`
- [ ] 前端显示"保管确认已提交"成功提示

---

**Primary Executor**: Codex
**Task Type**: Bug Fix
**Priority**: P0
**Stage**: 10200
**Goal**: 修复 keeper-confirm 因 item_id 缺失导致的 400 错误
**Dependencies**: None
**Execution**: RUNPROMPT
