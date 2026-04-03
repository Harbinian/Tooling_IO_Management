# Bug Fix: SettingsPage.vue 系统配置开关误将 Webhook URL 覆盖为 'true'

Primary Executor: Claude Code
Task Type: Bug Fix
Priority: P1
Stage: 10195
Goal: 修复系统设置页功能开关表格错误地用 el-switch 渲染 Webhook URL 字段，导致配置值被覆盖为 'true'
Dependencies: None
Execution: RUNPROMPT

---

## Context / 上下文

### 问题描述

`frontend/src/pages/settings/SettingsPage.vue` 的"功能开关管理"表格把所有 `sys_system_config` 条目都用 `el-switch` 渲染，包括 `feishu_webhook_supply_team`、`feishu_webhook_transport`、`feishu_webhook_url` 这些 Webhook URL 字段。

切换开关时，`updateFeatureFlagHandler` 把 URL 值覆盖成了字符串 `'true'`：

```javascript
// 第600行 - 问题代码
const result = await updateFeatureFlag(flagKey, value ? 'true' : 'false')
```

结果：`TO-OUT-20260402-010` 等订单的飞书机器人通知全部失败，错误信息为 `unknown url type: 'true'`。

### 影响

- 飞书通知功能完全不可用（所有 Webhook URL 被覆盖为 'true'）
- 已手动修复数据库，但前端再次操作会重新覆盖

### 根因

前端没有区分"布尔值开关"和"URL 字符串配置"，统一用 `el-switch` 渲染。

---

## Required References / 必需参考

- `frontend/src/pages/settings/SettingsPage.vue` - 需要修改的前端文件
- `frontend/src/api/systemConfig.js` - API 封装
- `.claude/rules/00_core.md` - 核心开发规则
- `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵（参考）

---

## Core Task / 核心任务

修复 SettingsPage.vue 的功能开关管理组件，使其：
1. **布尔值字段**（`feishu_notification_enabled`, `mpl_enabled`, `mpl_strict_mode`）使用 `el-switch` 渲染
2. **URL 字段**（`feishu_webhook_supply_team`, `feishu_webhook_transport`, `feishu_webhook_url`）使用 `el-input` 渲染，并在保存时直接发送 `config_value`（不转成 true/false）

### 当前问题代码位置

SettingsPage.vue 第 144-170 行附近：

```html
<el-table :data="featureFlags" stripe class="w-full" v-loading="featureFlagsLoading">
  <!-- ... -->
  <el-table-column prop="config_value" label="当前值" min-width="120">
    <template #default="{ row }">
      <el-tag :type="row.config_value === 'true' ? 'success' : 'info'" disable-transitions>
        {{ row.config_value }}
      </el-tag>
    </template>
  </el-table-column>
  <!-- ... -->
  <el-table-column label="操作" min-width="120" fixed="right">
    <template #default="{ row }">
      <el-switch
        :model-value="row.config_value === 'true'"
        :loading="row._loading"
        @change="(val) => updateFeatureFlagHandler(row.config_key, val)"
      />
    </template>
  </el-table-column>
```

`updateFeatureFlagHandler` (第 594 行)：

```javascript
async function updateFeatureFlagHandler(flagKey, value) {
  // ...
  const result = await updateFeatureFlag(flagKey, value ? 'true' : 'false')
  // ...
}
```

---

## Required Work / 必需工作

### 1. 识别字段类型

在 `SettingsPage.vue` 中定义 URL 配置键集合：

```javascript
const urlConfigKeys = new Set([
  'feishu_webhook_supply_team',
  'feishu_webhook_transport',
  'feishu_webhook_url'
])

const boolConfigKeys = new Set([
  'feishu_notification_enabled',
  'mpl_enabled',
  'mpl_strict_mode'
])
```

### 2. 修改 el-table-column 渲染逻辑

在 `config_value` 列中，根据字段类型分别渲染：
- URL 字段：显示为文本（el-tag type=info），不展示 switch
- 布尔字段：保持现有 el-tag + switch 渲染

### 3. 修改操作列渲染逻辑

- URL 字段：渲染为"编辑"按钮，点击后弹出 el-dialog 中的 el-input 编辑
- 布尔字段：保持现有 el-switch

### 4. 新增编辑弹窗

为 URL 字段新增 `el-dialog` 编辑弹窗，包含：
- `el-input` 用于输入 Webhook URL
- 确认/取消按钮
- 保存时调用 `updateSystemConfig(key, { config_value: inputValue })`

注意：`systemConfig.js` 中 `updateSystemConfig` 发送的是 `config_value` 字段，而 `updateFeatureFlag` 发送的是 `value` 字段且强制转 true/false。

### 5. 验证

- 数据库中 `feishu_webhook_*` 当前已是正确 URL，确保修改后不覆盖
- 切换布尔开关（如 `mpl_enabled`）不受影响

---

## Constraints / 约束条件

1. **不得修改 API 行为**：`updateFeatureFlag` 的 `value ? 'true' : 'false'` 逻辑保留给布尔字段用
2. **URL 字段走单独 API 路径**：使用 `updateSystemConfig(key, { config_value: urlValue })`
3. **不破坏现有布尔字段**：切换 `mpl_enabled` 等布尔开关功能不变
4. **UTF-8 编码**：所有文件修改保持 UTF-8
5. **使用 CSS 变量**：不得使用硬编码颜色

---

## Completion Criteria / 完成标准

- [ ] URL 字段（`feishu_webhook_*`）在表格中渲染为文本 + 编辑按钮，不再展示 el-switch
- [ ] 点击编辑按钮弹出对话框，可编辑并保存 Webhook URL
- [ ] 布尔字段（`feishu_notification_enabled`、`mpl_enabled`、`mpl_strict_mode`）保持 el-switch 行为不变
- [ ] 切换布尔开关时，不影响 URL 字段的值
- [ ] 语法检查通过：`python -m py_compile` 无错误
- [ ] E2E 测试验证 SettingsPage 功能正常（管理员登录后访问 /settings）
