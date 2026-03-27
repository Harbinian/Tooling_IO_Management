# 提示词 / Prompt

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 00069-03
Goal: Frontend OrderDetail.vue - replace confirmed qty with split_quantity
Dependencies: 00069-01, 00069-02
Execution: RUNPROMPT

---

## Context / 上下文

订单详情页面（OrderDetail.vue）目前显示"确认数量"字段（item.approvedQty），需要改为显示"分体数量"（item.split_quantity）。此字段来自后端联查的工装主数据表。

---

## Required References / 必需参考

- `frontend/src/pages/tool-io/OrderDetail.vue`:
  - 第193-194行：显示"确认数量"的部分

---

## Core Task / 核心任务

将 OrderDetail.vue 中"确认数量"的显示改为 `split_quantity`。

---

## Required Work / 必需工作

### 修改（第193-194行）

```html
<!-- 修改前 -->
<div class="space-y-1">
  <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">确认数量</p>
  <p class="text-sm font-medium text-foreground/80">{{ item.approvedQty ?? '-' }}</p>
</div>

<!-- 修改后 -->
<div class="space-y-1">
  <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-muted-foreground">分体数量</p>
  <p class="text-sm font-medium text-foreground/80">{{ item.split_quantity ?? '-' }}</p>
</div>
```

---

## Constraints / 约束条件

1. **只读显示**：分体数量只读，不允许编辑
2. **样式保持**：使用现有 CSS 类，保持 UI 一致性
3. **零退化**：不得破坏其他功能和样式

---

## Completion Criteria / 完成标准

1. 字段标签从"确认数量"改为"分体数量"
2. 显示值从 `item.approvedQty` 改为 `item.split_quantity`
3. 前端构建成功：`cd frontend && npm run build`
