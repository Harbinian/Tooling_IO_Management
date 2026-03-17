# 00060 工装搜索有效性标注功能 - 前端实现

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 00060
Goal: 扩展工装搜索对话框，标注异常状态工装并禁用选择
Dependencies: 00060_tool_search_validity_backend (后端必须先完成)
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
保管员批准申请的标准需要班组长在选择工装时就知晓。班组长需要能看到工装的状态（返修/封存/定检超期/无合格证等），以便判断是否应该申请。当前工装搜索没有标注这些状态。

### 目标用户
- 班组长 (Team Leader): 搜索工装时看到异常状态

### 核心痛点
班组长搜索工装时，无法知道哪些工装是异常状态（返修中、封存、定检超期等），只能尝试选择后发现不可选。

### 业务目标
1. 工装搜索结果标注异常状态
2. 异常工装显示灰色/禁用态
3. 鼠标悬停显示禁用原因 tooltip
4. 复选框不可勾选

---

## Required References / 必需参考

- frontend/src/components/ToolSearchDialog.vue - 工装搜索对话框
- frontend/src/api/toolApi.js - 工装API调用
- .claude/rules/30_gemini_frontend.md - 前端设计协议

---

## Core Task / 核心任务

### 1. UI设计

#### 搜索结果列表

| 状态 | 显示效果 | 是否可选 |
|------|---------|:-------:|
| 正常工装 | 正常显示 | ✅ |
| 返修中 | 灰色 + 标注"返修" | ❌ |
| 封存 | 灰色 + 标注"封存" | ❌ |
| 定检超期 | 灰色 + 标注"定检超期" | ❌ |
| 定检中 | 灰色 + 标注"定检中" | ❌ |
| 无合格证 | 灰色 + 标注"无合格证" | ❌ |

#### 异常工装样式

```css
/* 禁用行样式 */
.tool-item-disabled {
    opacity: 0.5;
    background-color: var(--muted);
}

/* 禁用标签 */
.disabled-tag {
    font-size: 12px;
    padding: 2px 6px;
    border-radius: 4px;
    background-color: var(--warning);
    color: var(--warning-foreground);
}
```

#### 交互行为

1. 正常工装: `disabled=false`，checkbox 可勾选
2. 异常工装: `disabled=true`：
   - 行显示灰色半透明
   - 右侧显示禁用原因标签
   - checkbox 不可勾选
   - 鼠标悬停显示 `disabled_reason` tooltip

### 2. 组件修改

修改 `ToolSearchDialog.vue` 或 `ToolSelectionTable.vue`：

```vue
<el-table>
    <el-table-column label="工装编码" prop="tool_code" />
    <el-table-column label="工装名称" prop="tool_name" />
    <el-table-column label="规格" prop="spec" />
    <el-table-column label="位置" prop="current_location_text" />
    <el-table-column label="状态">
        <template #default="{ row }">
            <el-tag v-if="row.disabled" type="warning" effect="plain">
                {{ row.status_text }}
            </el-tag>
            <el-tag v-else type="success">
                {{ row.status_text }}
            </el-tag>
        </template>
    </el-table-column>
    <el-table-column label="操作" width="100">
        <template #default="{ row }">
            <el-tooltip
                v-if="row.disabled"
                :content="row.disabled_reason"
                placement="top"
            >
                <span class="disabled-reason">{{ row.disabled_reason }}</span>
            </el-tooltip>
            <el-checkbox
                v-model="row.selected"
                :disabled="row.disabled"
                @change="handleSelect(row)"
            />
        </template>
    </el-table-column>
</el-table>
```

### 3. API响应处理

API 已返回 `disabled` 和 `disabled_reason` 字段，前端需要：

1. 正常工装: `disabled=false`, `disabled_reason=null` → 可选
2. 异常工装: `disabled=true`, `disabled_reason="..."` → 禁用但可见

---

## Required Work / 必需工作

1. **组件修改**
   - 修改 `ToolSearchDialog.vue` 的搜索结果表格
   - 根据 `disabled` 字段渲染禁用态
   - 添加 `el-tooltip` 显示禁用原因

2. **样式处理**
   - 添加禁用行样式（灰色半透明）
   - 使用 CSS 变量，禁止硬编码颜色

3. **交互逻辑**
   - `disabled=true` 时 checkbox 不可勾选
   - 鼠标悬停显示 tooltip

4. **UI一致性**
   - 使用 Element Plus 组件
   - 符合深色主题规范

---

## Constraints / 约束条件

1. **CSS规范**: 禁止 `bg-white`, `text-white` 等硬编码，必须使用 CSS 变量
2. **主题兼容**: 支持明暗主题切换
3. **交互一致**: 异常工装必须禁用 checkbox
4. **无占位符**: 所有代码必须完整可执行

---

## Completion Criteria / 完成标准

1. ✅ 正常工装正常显示，可勾选
2. ✅ 异常工装显示灰色半透明态
3. ✅ 异常工装显示禁用原因标签
4. ✅ 异常工装 checkbox 不可勾选
5. ✅ 鼠标悬停显示禁用原因 tooltip
6. ✅ 前端构建通过: `cd frontend && npm run build`
7. ✅ UI 符合深色主题规范
