# 重构提示词：前端 tool_code → serial_no 字段重命名

## Header

Primary Executor: Claude Code
Task Type: Refactoring
Priority: P1
Stage: 2/2
Goal: 将前端代码中的 tool_code 字段重命名为 serial_no，UI 显示"工装编码"改为"工装序列号"
Dependencies: "20110（后端和数据库重构完成后）"
Execution: RUNPROMPT

---

## Context / 上下文

**业务背景**：与后端重构配套，前端需要将所有 `tool_code` 字段引用改为 `serial_no`，并将 UI 显示文本"工装编码"改为"工装序列号"。

**前置依赖**：后端和数据库重构（提示词 20110）必须先完成，确保 API 响应中的字段名已从 `tool_code` 改为 `serial_no`。

**影响范围**：
- 前端 API 客户端：处理 serial_no 字段
- 前端工具函数：normalizeItem 等函数中的字段映射
- Vue 组件：UI 显示文本

---

## Core Task / 核心任务

### 1. 修改前端 API 客户端

文件：`frontend/src/api/tools.js`

检查并更新：
- API 请求参数中的 `tool_code` → `serial_no`
- API 响应解析中的 `tool_code` → `serial_no`

### 2. 修改前端工具函数

文件：`frontend/src/utils/toolIO.js`

修改 `normalizeItem` 函数中的字段映射：

```javascript
// 第 83 行：将
toolCode: pickValue(record, ['tool_code', '序列号']),
// 改为
toolCode: pickValue(record, ['serial_no', 'tool_code', '序列号']),
```

**注意**：保持向后兼容，同时支持 `serial_no`、`tool_code`、`序列号` 三个字段名，以确保平滑过渡。

### 3. 修改 Vue 组件 UI 文本

文件：`frontend/src/pages/tool-io/KeeperProcess.vue`

将以下 UI 文本中的"工装编码"改为"工装序列号"：

- 第 290 行：`placeholder="输入工装编码后按回车搜索"` → `placeholder="输入工装序列号后按回车搜索"`
- 第 414 行：表头 `<th class="px-4 py-3">工装编码</th>` → `<th class="px-4 py-3">工装序列号</th>`

文件：`frontend/src/pages/tool-io/OrderCreate.vue`

检查并更新所有显示"工装编码"文本的地方。

### 4. 更新前端规则文档

文件：`.claude/rules/04_frontend.md`

更新字段映射表：
- 第 20 行：`- 工装编码 / tool code` → `- 工装序列号 / serial number`
- 第 57 行：`| 工装编码 / Tool Code | tool_code |` → `| 工装序列号 / Serial Number | serial_no |`

---

## Required Work / 必需工作

1. **API 客户端更新** - 修改 `frontend/src/api/tools.js`
2. **工具函数更新** - 修改 `frontend/src/utils/toolIO.js` 的 normalizeItem
3. **Vue 组件更新** - 修改 KeeperProcess.vue、OrderCreate.vue 中的 UI 文本
4. **规则文档更新** - 更新 `.claude/rules/04_frontend.md`

---

## Constraints / 约束条件

1. **CSS 变量使用** - 严禁使用硬编码颜色，必须使用 CSS 变量
2. **API 字段映射** - 确保前端 API 层正确处理 serial_no 字段
3. **向后兼容** - toolIO.js 中的 pickValue 应该同时支持新旧字段名

---

## Completion Criteria / 完成标准

1. ✅ `frontend/src/api/tools.js` 中的 API 字段已更新
2. ✅ `frontend/src/utils/toolIO.js` 中的 normalizeItem 已更新
3. ✅ KeeperProcess.vue 中的 UI 文本已更新
4. ✅ OrderCreate.vue 中的 UI 文本已更新
5. ✅ `.claude/rules/04_frontend.md` 中的字段映射已更新
6. ✅ 前端构建成功：`cd frontend && npm run build`

---

## Verification / 验证

```powershell
# 前端构建
cd frontend && npm run build

# 如果有 E2E 测试环境
python test_runner/playwright_e2e.py
```
