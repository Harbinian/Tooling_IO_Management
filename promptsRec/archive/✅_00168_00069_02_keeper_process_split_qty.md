# 提示词 / Prompt

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 00069-02
Goal: Frontend KeeperProcess.vue - replace approvedQty with split_quantity
Dependencies: 00069-01
Execution: RUNPROMPT

---

## Context / 上下文

保管员工作台（KeeperProcess.vue）中存在"批准数量"字段供保管员手动输入，但该字段已被取消。现在需要改为显示从后端获取的"分体数量"（split_quantity）字段，此字段由数据库工装主数据表提供，保管员无需手动填写。

---

## Required References / 必需参考

- `frontend/src/pages/tool-io/KeeperProcess.vue`:
  - 第181行：表头 `<th>批准数量</th>`
  - 第202-212行：Input 输入框 `v-model.number="item.approvedQty"`
  - 第642-659行：`buildEditableItems` 函数中 `approvedQty: defaultApprovedQty`
  - 第718行：payload 中 `approved_qty: item.approvedQty || item.applyQty || 1`

---

## Core Task / 核心任务

将 KeeperProcess.vue 中的"批准数量"字段改为"分体数量"只读显示。

---

## Required Work / 必需工作

### 1. 表头修改（第181行）

```html
<!-- 修改前 -->
<th class="px-4 py-3 font-bold w-[120px]">批准数量</th>

<!-- 修改后 -->
<th class="px-4 py-3 font-bold w-[100px]">分体数量</th>
```

### 2. 单元格修改（第202-212行）

```html
<!-- 修改前 -->
<td class="px-4 py-4">
  <div class="flex items-center gap-2">
    <Input
      type="number"
      v-model.number="item.approvedQty"
      class="h-8 w-16 text-center border-border text-xs"
      :max="item.applyQty"
    />
    <span class="text-[10px] text-muted-foreground">/ {{ item.applyQty }}</span>
  </div>
</td>

<!-- 修改后 -->
<td class="px-4 py-4 text-center">
  <span class="text-sm">{{ item.split_quantity || '-' }}</span>
</td>
```

### 3. buildEditableItems 函数修改（约第642-659行）

移除 `approvedQty: defaultApprovedQty` 行，保留其他字段。

### 4. approveOrder payload 修改（约第718行）

```javascript
// 修改前
approved_qty: item.status === 'approved' ? item.approvedQty || item.applyQty || 1 : 0,

// 修改后
approved_qty: item.status === 'approved' ? item.split_quantity || item.applyQty || 1 : 0,
```

---

## Constraints / 约束条件

1. **只读显示**：分体数量不可编辑，只显示从后端获取的数据
2. **样式保持**：使用现有 CSS 类，保持 UI 一致性
3. **零退化**：不得破坏其他功能和样式

---

## Completion Criteria / 完成标准

1. 表头显示"分体数量"而非"批准数量"
2. 单元格显示 `item.split_quantity` 只读值，不再有输入框
3. buildEditableItems 移除了 approvedQty 相关逻辑
4. payload 中 approved_qty 使用 split_quantity 值
5. 前端构建成功：`cd frontend && npm run build`
