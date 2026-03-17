Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 083
Goal: Implement keeper tool status management UI in KeeperProcess page
Dependencies: 082
Execution: RUNPROMPT

---

## Context / 上下文

保管员需要直接设置工装状态（不依赖订单流程），系统需要保存设置记录。

后端 API 已实现 (`082_keeper_batch_tool_status_backend.md`)：
- `PATCH /api/tools/batch-status` - 批量更新工装状态
- `GET /api/tools/status-history/<tool_code>` - 查询状态变更历史

现在需要实现前端 UI。

---

## Required References / 必需参考

- `frontend/src/pages/tool-io/KeeperProcess.vue` - 保管员处理页面，复用现有布局和组件
- `frontend/src/api/` - API 调用封装，参考现有模式
- `frontend/src/utils/permission.js` - 权限检查工具
- `docs/ARCHITECTURE.md` 3.3 节 - 工装状态定义: `in_storage`(在库), `outbounded`(已出库), `maintain`(维修中), `scrapped`(已报废)
- 项目 UI 规范：使用 Element Plus 深色主题组件

---

## Core Task / 核心任务

在 KeeperProcess.vue 页面新增"工装状态管理"功能区域：

1. 工装搜索与选择器
2. 批量状态设置下拉框
3. 变更历史查询展示
4. 权限控制（仅 keeper 角色可见）

---

## Required Work / 必需工作

### 1. API 封装

**文件**: `frontend/src/api/toolApi.js` (如不存在则创建)

封装新增的 API：

```javascript
// 批量更新工装状态
export function batchUpdateToolStatus(data) {
  return request.patch('/api/tools/batch-status', data)
}

// 查询状态变更历史
export function getToolStatusHistory(toolCode, params) {
  return request.get(`/api/tools/status-history/${toolCode}`, { params })
}
```

### 2. 状态管理

**文件**: `frontend/src/store/toolStore.js` (如不存在则创建)

或直接在 KeeperProcess.vue 中使用 `ref/reactive` 管理状态：

```javascript
// 工装选择相关状态
const selectedTools = ref([])
const toolSearchKeyword = ref('')

// 状态设置相关状态
const newToolStatus = ref('')
const statusRemark = ref('')

// 历史记录相关状态
const statusHistory = ref([])
const historyLoading = ref(false)
```

### 3. UI 组件开发

**文件**: `frontend/src/pages/tool-io/KeeperProcess.vue`

新增"工装状态管理"标签页或侧边区域：

```vue
<template>
  <!-- 新增标签页 -->
  <el-tabs v-model="activeTab">
    <el-tab-pane label="订单处理" name="orders">...</el-tab-pane>
    <el-tab-pane label="工装状态管理" name="tool-status">
      <!-- 工装搜索选择区 -->
      <div class="tool-status-section">
        <!-- 搜索框 -->
        <el-input v-model="toolSearchKeyword" placeholder="搜索工装编码/名称" />

        <!-- 已选工装展示 -->
        <el-table :data="selectedTools">
          <el-table-column prop="toolCode" label="工装编码" />
          <el-table-column prop="toolName" label="工装名称" />
          <el-table-column prop="currentStatus" label="当前状态" />
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button @click="removeTool(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 批量操作区 -->
        <div class="batch-actions">
          <el-select v-model="newToolStatus" placeholder="选择新状态">
            <el-option label="在库" value="in_storage" />
            <el-option label="已出库" value="outbounded" />
            <el-option label="维修中" value="maintain" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
          <el-input v-model="statusRemark" placeholder="变更原因" />
          <el-button @click="applyStatusChange" :loading="submitting">
            确认变更
          </el-button>
        </div>

        <!-- 状态变更历史 -->
        <div class="history-section">
          <h4>状态变更历史</h4>
          <el-table :data="statusHistory" v-loading="historyLoading">
            <el-table-column prop="tool_code" label="工装编码" />
            <el-table-column prop="old_status" label="原状态" />
            <el-table-column prop="new_status" label="新状态" />
            <el-table-column prop="remark" label="变更原因" />
            <el-table-column prop="operator_name" label="操作人" />
            <el-table-column prop="change_time" label="变更时间" />
          </el-table>
        </div>
      </div>
    </el-tab-pane>
  </el-tabs>
</template>
```

### 4. 权限控制

- `tool:status_update` 权限控制批量更新按钮显示
- 使用 `hasPermission('tool:status_update')` 检查

### 5. 状态值映射

| UI 显示 | API 值 |
|---------|--------|
| 在库 | in_storage |
| 已出库 | outbounded |
| 维修中 | maintain |
| 已报废 | scrapped |

---

## Constraints / 约束条件

1. **UI 规范**：使用 Element Plus 深色主题，与 KeeperProcess.vue 现有风格一致
2. **权限控制**：仅 keeper 和 admin 角色可见状态管理功能
3. **响应式设计**：适配 KeeperProcess.vue 现有的布局结构
4. **状态保持**：页面刷新后需重新选择工装（不持久化）
5. **错误处理**：API 调用失败需显示错误消息
6. **加载状态**：批量操作进行时显示 loading 状态
7. **无拼音变量**：所有变量使用英文命名

---

## Completion Criteria / 完成标准

1. **语法检查通过**：
   ```powershell
   cd frontend && npm run build
   ```

2. **功能验证**：
   - 使用 keeper 角色登录，进入 KeeperProcess 页面
   - 点击"工装状态管理"标签页
   - 搜索并选择多个工装
   - 选择新状态（如"维修中"）并填写变更原因
   - 点击"确认变更"按钮
   - 验证成功提示出现
   - 查看历史记录表格，确认记录已添加

3. **权限验证**：
   - 使用 team_leader 角色登录，验证"工装状态管理"标签页不可见或禁用
