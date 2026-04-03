# KeeperProcess.vue UI 优化

## 任务概述

根据需求文档 `docs/REQUIREMENTS/REQ-20260403-002_keeper_process_ui_improvement.md`，实现以下功能：

### 1. 后端：新增按角色查询用户 API

**文件**：`backend/routes/user_routes.py`（新建）

**API**：`GET /api/users/by-role/<role_code>?org_id=<可选>`

**权限**：无 `admin:user_manage` 限制，所有登录用户可访问（使用 `dashboard:view` 权限）

**查询逻辑**：
```sql
SELECT
    u.user_id,
    u.login_name,
    u.display_name,
    u.default_org_id,
    o.org_name
FROM sys_user u
JOIN sys_user_role_rel ur ON u.user_id = ur.user_id
JOIN sys_role r ON ur.role_id = r.role_id
LEFT JOIN sys_org o ON u.default_org_id = o.org_id
WHERE r.role_code = ? AND u.status = 'active'
-- 如果 org_id 存在，添加 AND u.default_org_id = ?
ORDER BY u.display_name
```

**返回格式**：
```json
{
  "success": true,
  "data": [
    {
      "user_id": "xxx",
      "login_name": "fengliang",
      "display_name": "冯亮",
      "default_org_id": "org001",
      "org_name": "制造部"
    }
  ]
}
```

### 2. 前端：运输类型下拉

**文件**：`frontend/src/pages/tool-io/KeeperProcess.vue`

**修改位置**：第 151-153 行

**修改前**：
```html
<Input v-model="confirmForm.transportType" placeholder="如：人工 / 叉车 / 外协" />
```

**修改后**：
```html
<Select v-model="confirmForm.transportType">
  <option value="叉车">叉车</option>
  <option value="外协">外协</option>
</Select>
```

**默认赋值**：在 `confirmForm reactive` 定义处或 `onMounted` 中设置 `confirmForm.transportType = '叉车'`

### 3. 前端：运输负责人下拉

**新增状态**：
```javascript
const productionPrepUsers = ref([])

async function loadProductionPrepUsers() {
  // 调用 GET /api/users/by-role/PRODUCTION_PREP?org_id=<当前用户org_id>
  // 存入 productionPrepUsers
  // 设置默认值：优先 fengliang，否则取列表第一个
}
```

**修改位置**：第 155-157 行

**修改前**：
```html
<Input v-model="confirmForm.transportAssigneeName" placeholder="请输入姓名" />
```

**修改后**：
```html
<Select v-model="confirmForm.transportAssigneeId" @change="onTransportAssigneeChange">
  <option value="">请选择</option>
  <option v-for="user in productionPrepUsers" :key="user.user_id" :value="user.user_id">
    {{ user.display_name }}
  </option>
</Select>
```

**默认值逻辑**（在 `loadProductionPrepUsers` 中）：
```javascript
const fengliang = productionPrepUsers.value.find(u => u.login_name === 'fengliang')
if (fengliang) {
  confirmForm.transportAssigneeId = fengliang.user_id
  confirmForm.transportAssigneeName = fengliang.display_name
} else if (productionPrepUsers.value.length > 0) {
  confirmForm.transportAssigneeId = productionPrepUsers.value[0].user_id
  confirmForm.transportAssigneeName = productionPrepUsers.value[0].display_name
}
```

**onTransportAssigneeChange 函数**：
```javascript
function onTransportAssigneeChange(userId) {
  const user = productionPrepUsers.value.find(u => u.user_id === userId)
  if (user) {
    confirmForm.transportAssigneeName = user.display_name
  }
}
```

**在 `selectOrder` 函数中调用** `loadProductionPrepUsers()`

### 4. 前端：工装明细表格列调整

**修改位置**：第 181-226 行

**表头修改**：
```html
<tr>
  <th class="px-4 py-3 font-bold">工装序列号</th>
  <th class="px-4 py-3 font-bold">工装图号</th>
  <th class="px-4 py-3 font-bold">工装名称</th>
  <th class="px-4 py-3 font-bold w-[120px]">MPL</th>
  <th class="px-4 py-3 font-bold w-[120px]">状态</th>
  <th class="px-4 py-3 font-bold w-[100px]">分体数量</th>
</tr>
```

**单元格修改**（移除 locationText，显示 serial_no/drawing_no/tool_name）：
```html
<td class="px-4 py-4">
  <p class="font-semibold text-foreground font-mono text-xs">{{ item.serial_no || '-' }}</p>
</td>
<td class="px-4 py-4">
  <p class="text-xs break-word" style="word-break: break-word; white-space: normal; max-width: 200px;">
    {{ item.drawing_no || '-' }}
  </p>
</td>
<td class="px-4 py-4">
  <p class="text-xs break-word" style="word-break: break-word; white-space: normal; max-width: 200px;">
    {{ item.tool_name || '-' }}
  </p>
</td>
```

**移除原来的第三列（建议位置）和第四列（确认位置 Input）**

## 验收标准

1. 运输类型下拉默认选中"叉车"
2. 运输负责人下拉正确加载本部门生产准备工列表，默认"冯亮"（或列表第一个）
3. 工装明细表格正确显示三列：序列号、图号、名称，长文本自动换行
4. 新 API `GET /api/users/by-role/PRODUCTION_PREP` 可正常访问

## 约束

- 使用 CSS 变量，避免硬编码颜色
- 遵循 `backend/database/schema/column_names.py` 中的字段常量定义
- 保持 DEBUG_IDS 徽章（新增 UI 元素时添加）
