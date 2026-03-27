Primary Executor: Codex
Task Type: Bug Fix
Priority: P2
Stage: 10175
Goal: 出库申请目标位置改为下拉选择框（A06/A02/A08）
Dependencies: None
Execution: RUNPROMPT

---

# Bug修复: 出库申请目标位置下拉框

## 上下文 / Context

### 问题描述

在 `OrderCreate.vue` 中，出库申请表单的"目标位置"字段使用自由文本输入框：

```vue
<Input v-model="form.targetLocationText" placeholder="输入目标位置" />
```

应该改为下拉选择框，只允许选择 `A06`、`A02`、`A08` 三个值，禁止手动输入。

### 受影响文件

- `frontend/src/pages/tool-io/OrderCreate.vue`

## 核心任务 / Core Task

1. 将 `targetLocationText` 从 `<Input>` 改为 `<el-select>`
2. 固定选项：`A06`、`A02`、`A08`
3. 保持 `form.targetLocationText` 绑定不变
4. 验证区域：`v-if="form.orderType === 'outbound'"`（第 72-75 行）

## 必需工作 / Required Work

1. 将 `<Input v-model="form.targetLocationText" placeholder="输入目标位置" />` 替换为：
   ```vue
   <el-select v-model="form.targetLocationText" placeholder="选择目标位置">
     <el-option label="A06" value="A06" />
     <el-option label="A02" value="A02" />
     <el-option label="A08" value="A08" />
   </el-select>
   ```
2. 确保导入 `el-select` 和 `el-option`（如果尚未导入）
3. 验证下拉框在出库类型时正确显示，入库类型时隐藏

## 约束条件 / Constraints

1. 只修改 `frontend/src/pages/tool-io/OrderCreate.vue`
2. 不修改应用逻辑，只修改 UI 组件
3. 保持 `form.targetLocationText` 字段名称不变
4. 运行 `cd frontend && npm run build` 验证构建

## 完成标准 / Completion Criteria

1. `npm run build` 构建成功
2. 出库申请时，目标位置显示为下拉框，选项为 A06/A02/A08
3. 用户无法手动输入其他值
