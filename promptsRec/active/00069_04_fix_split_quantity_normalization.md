# 提示词 / Prompt

Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 00069
Goal: Fix split_quantity normalization so keeper workflow actually uses split quantity end-to-end
Dependencies: 00069_01_split_quantity_backend, 00069_02_keeper_process_split_qty, 00069_03_order_detail_split_qty
Execution: RUNPROMPT

---

## Context / 上下文

对 `00069_replace_approved_qty_with_split_quantity.md` 的执行结果进行验证后，发现后端联查和前端模板替换虽然已落地，但功能链路仍未真正打通。

根因在于前端数据规范化层 `frontend/src/utils/toolIO.js` 的 `normalizeItem()` 没有保留后端返回的 `split_quantity` 字段。订单详情接口会先经过 `normalizeOrder()` / `normalizeItem()` 转换，再传给 `KeeperProcess.vue` 和 `OrderDetail.vue`。由于 `split_quantity` 在规范化时被丢弃：

1. KeeperProcess 页面中的 `{{ item.split_quantity || '-' }}` 很可能始终显示 `-`
2. `approveOrder` payload 中的 `approved_qty` 很可能回退为 `item.applyQty || 1`
3. OrderDetail 页面中的 `{{ item.split_quantity ?? '-' }}` 很可能也显示 `-`

这属于 00069 的阻断性残留问题，必须补齐。

---

## Required References / 必需参考

- `frontend/src/utils/toolIO.js` - `normalizeOrder()` / `normalizeItem()`，当前未映射 `split_quantity`
- `frontend/src/pages/tool-io/KeeperProcess.vue` - 第203行显示 `item.split_quantity`，第702行 payload 使用 `item.split_quantity`
- `frontend/src/pages/tool-io/OrderDetail.vue` - 第194行显示 `item.split_quantity`
- `frontend/src/api/orders.js` - `getOrderDetail()` 会调用 `normalizeOrder()`
- `logs/prompt_task_runs/run_20260327_00171_00069_01_split_quantity_backend.md` - 后端已返回 `split_quantity`

---

## Core Task / 核心任务

### 1. 前端修复 - toolIO.js

修改 `frontend/src/utils/toolIO.js` 的 `normalizeItem()`，显式保留并规范化后端返回的 `split_quantity` 字段，确保页面和 payload 都能读取到真实值。

### 2. 链路验证

确认 `getOrderDetail()` 返回的数据经 `normalizeOrder()` 处理后，`KeeperProcess.vue` 与 `OrderDetail.vue` 仍可直接读取 `item.split_quantity`。

### 3. RUNPROMPT 收口

补充本次修复的执行报告；若形成真实代码修正，还需写入 `logs/codex_rectification/`。

---

## Required Work / 必需工作

### 前端 (Codex)

1. 修改 `frontend/src/utils/toolIO.js`
2. 在 `normalizeItem()` 返回对象中新增 `split_quantity`
3. 优先兼容以下来源键：
   - `split_quantity`
   - `分体数量`
4. 数值处理要求：
   - 保留 `0` 的可见性，不要因为 `||` 误吞零值
   - 不要破坏现有 `approvedQty`、`applyQty` 等字段兼容性
5. 验证以下链路：
   - `getOrderDetail()` 经 `normalizeOrder()` 后包含 `items[].split_quantity`
   - KeeperProcess 读取的 `item.split_quantity` 有值时正常显示
   - `approved_qty` payload 优先使用 `split_quantity`
   - OrderDetail 正常显示 `split_quantity`
6. 执行前端构建验证：`cd frontend && npm run build`

### 文档与日志 (Codex)

1. 在 `logs/prompt_task_runs/` 下写本次 `00069_04` 执行报告
2. 若有真实修正，在 `logs/codex_rectification/` 下写纠正日志
3. 按规则归档本提示词：`✅_<archive-seq>_00069_04_fix_split_quantity_normalization_done.md`

---

## Constraints / 约束条件

1. **最小修复**：只修复 `split_quantity` 在规范化层丢失的问题，不扩大改动范围
2. **零值安全**：若 `split_quantity = 0`，前端不得误显示为 `-`
3. **兼容优先**：保留 `approvedQty` 等旧字段，避免影响其他页面
4. **链路一致**：后端字段名、规范化字段名、页面读取字段名必须一致
5. **UTF-8**：新增或修改的文本文件必须为 UTF-8 无 BOM

---

## Completion Criteria / 完成标准

1. `normalizeItem()` 明确返回 `split_quantity`
2. `getOrderDetail()` 的 `result.data.items[]` 中保留 `split_quantity`
3. KeeperProcess 页面分体数量不再因规范化丢字段而显示 `-`
4. `approveOrder` payload 中的 `approved_qty` 实际优先使用 `split_quantity`
5. OrderDetail 页面分体数量显示正确
6. `npm run build` 成功
7. 本次 RUNPROMPT 的报告、纠正日志、归档文件齐全
