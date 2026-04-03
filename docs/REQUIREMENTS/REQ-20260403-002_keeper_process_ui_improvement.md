# 需求：保管员处理页面 UI 优化

## 基本信息 / Basic Information

- **需求编号**：REQ-20260403-002
- **创建日期**：2026-04-03
- **状态**：已完善

---

## 5W2H 分析 / 5W2H Analysis

### What - 核心需求

**功能描述**：

优化保管员处理页面（KeeperProcess.vue）的派工配置和工装明细确认区域，具体包含：

#### 1. 运输类型改为下拉菜单
- 选项固定为：**叉车**、**外协**
- 默认值：**叉车**
- 替代原来的自由文本输入

#### 2. 运输负责人改为下拉选择
- 数据来源：本部门（org_id）下所有 `PRODUCTION_PREP`（生产准备工）角色用户
- 显示格式：`display_name`（如"冯亮"）
- 默认值逻辑：
  - 优先选择 `login_name = "fengliang"` 的用户
  - 如果"冯亮"不在本部门或不可用，选择列表第一个用户
  - 如果列表为空，保持空

#### 3. 新增按角色查询用户 API
- **新 API**：`GET /api/users/by-role/<role_code>`
- **权限**：无 `admin:user_manage` 限制，登录用户均可访问
- **参数**：`role_code`（如 `PRODUCTION_PREP`）、`org_id`（可选，用于筛选本部门）
- **返回**：`[{ user_id, login_name, display_name, org_id, org_name }]`

#### 4. 工装明细表格列调整
- **移除列**：建议位置、确认位置
- **新增三列**：工装序列号(serial_no)、工装图号(drawing_no)、工装名称(tool_name)
- **布局**：三列并排显示，允许自动换行（处理长文本）
- **保留列**：MPL、状态、分体数量

**输入**：
- 运输类型：下拉选择（叉车/外协）
- 运输负责人：下拉选择（本部门生产准备工列表）
- 工装明细：API 已返回 serial_no、drawing_no、tool_name，前端调整展示方式

**输出**：
- KeeperProcess.vue 页面 UI 更新
- 新增 `GET /api/users/by-role/<role_code>` API

---

### Why - 动机与价值

**业务背景**：
当前保管员在确认订单时，运输类型和运输负责人需要手动填写，存在以下问题：
- 运输类型填写不统一（可能写"叉车"、"叉车搬运"等不一致表述）
- 运输负责人姓名可能拼写错误
- 手动输入效率低

**预期价值**：
- 标准化数据录入，减少人为错误
- 提高操作效率，默认值减少重复输入
- 规范运输类型，避免统计混乱

**成功标准**：
- 运输类型下拉选择工作正常，默认"叉车"
- 运输负责人下拉显示本部门生产准备工，默认"冯亮"（或列表第一个）
- 工装明细表格正确显示三列（序列号、图号、名称），长文本自动换行

---

### Who - 角色与用户

**主要用户**：
- 保管员（keeper）：使用 KeeperProcess.vue 页面进行订单确认和派工

**开发负责人**：
- 待分配

**受影响者**：
- 保管员：日常使用频率高，直接受益
- 运输负责人（生产准备工）：被指派时信息更准确
- 班组长：查看订单时数据更规范

---

### When - 时间线

**期望完成时间**：
- 待定

**使用频率**：
- 保管员每日多次使用

**优先级**：
- P1（重要改进，非紧急）

---

### Where - 使用场景

**使用环境**：
- 生产环境，工装出入库管理系统的保管员处理页面

**集成需求**：
- 新增 API：`GET /api/users/by-role/<role_code>`
- 前端修改：KeeperProcess.vue

**约束条件**：
- 需复用现有 `sys_user`、`sys_role`、`sys_user_role_rel` 表结构
- 新 API 不得使用 `admin:user_manage` 权限
- 订单详情中原有的 serial_no、drawing_no 字段已存在，只需调整展示

---

### How - 实现方式

**建议实现方式**：

#### 后端新增 API
```python
# backend/routes/user_routes.py (新建或扩展)
@require_permission("dashboard:view")  # 或无权限限制
def api_get_users_by_role(role_code: str):
    """获取指定角色的用户列表，支持按 org_id 筛选"""
    # 查询 sys_user_role_rel + sys_user + sys_org
    # 返回 user_id, login_name, display_name, org_id, org_name
```

#### 前端修改 KeeperProcess.vue
1. 运输类型：将 `<Input v-model="confirmForm.transportType">` 改为 `<Select>`
   - 选项：[{ label: '叉车', value: '叉车' }, { label: '外协', value: '外协' }]
   - 默认值：`confirmForm.transportType = '叉车'`

2. 运输负责人：
   - 新增 `productionPrepUsers` ref 存储用户列表
   - 新增 `loadProductionPrepUsers()` 方法调用新 API
   - 将 `<Input v-model="confirmForm.transportAssigneeName">` 改为 `<Select>`
   - 默认值逻辑：优先 fengliang，否则取列表第一个

3. 工装明细表格：
   - 表头：从 `<th>工装信息</th><th>建议位置</th><th>确认位置</th>` 改为三列
   - `<th>工装序列号</th><th>工装图号</th><th>工装名称</th>`
   - 单元格：去除 locationText 相关逻辑，改为显示 serial_no、drawing_no、tool_name
   - 添加 CSS `word-break: break-word; white-space: normal;` 支持换行

**参考系统**：
- 现有 `admin_user_routes.py` 的 `list_users` 查询逻辑
- 现有 KeeperProcess.vue 的 select/option 使用方式

**技术栈**：
- 后端：Flask + SQL Server (pyodbc)
- 前端：Vue 3 + Element Plus

---

### How Much - 资源与范围

**范围**：

**包含**：
- [ ] 新增 `GET /api/users/by-role/<role_code>` API
- [ ] KeeperProcess.vue 运输类型下拉改造
- [ ] KeeperProcess.vue 运输负责人下拉改造（包含默认值逻辑）
- [ ] KeeperProcess.vue 工装明细表格列调整

**不包含**：
- 其他页面（如 OrderCreate.vue）的类似改造
- 运输类型"外协"的其他关联业务逻辑
- 用户管理页面的改造

**资源需求**：
- 后端：1-2 小时
- 前端：2-3 小时
- 测试：1 小时

---

## 工装明细表格列调整详情 / Item Table Column Adjustment

### 现状
- 表头：`工装信息 | 建议位置 | 确认位置 | MPL | 状态 | 分体数量`
- 工装信息列：上下结构显示 tool_code、tool_name

### 目标
- 表头：`工装序列号 | 工装图号 | 工装名称 | MPL | 状态 | 分体数量`
- 三列并排显示，使用 `word-break: break-word` 处理长文本

### CSS 调整
```css
/* 工装明细表格单元格 */
.tool-info-cell {
  word-break: break-word;
  white-space: normal;
  max-width: 200px; /* 防止过宽 */
}
```

---

## 待确认问题 / Open Questions

- [x] 冯亮的标识：login_name="fengliang", display_name="冯亮"
- [x] 生产准备工列表获取：新增 API
- [x] 默认值逻辑：优先冯亮，否则列表第一个
- [x] 工装明细字段：已有数据，调整展示为三列并排

---

## 验收标准 / Acceptance Criteria

1. **运输类型下拉**
   - [ ] 下拉选项只有"叉车"和"外协"两个选项
   - [ ] 页面加载时默认选中"叉车"
   - [ ] 选中值正确保存到 `confirmForm.transportType`

2. **运输负责人下拉**
   - [ ] 下拉选项显示本部门所有生产准备工
   - [ ] 默认选中"冯亮"（fengliang）
   - [ ] 如果冯亮不在本部门，默认选中列表第一个
   - [ ] 如果列表为空，下拉显示为空
   - [ ] 选中值正确保存到 `confirmForm.transportAssigneeId` 和 `confirmForm.transportAssigneeName`

3. **新 API**
   - [ ] `GET /api/users/by-role/PRODUCTION_PREP?org_id=xxx` 返回用户列表
   - [ ] 无需 admin:user_manage 权限即可访问

4. **工装明细表格**
   - [ ] 表格有三列：工装序列号、工装图号、工装名称
   - [ ] 无"建议位置"和"确认位置"列
   - [ ] 长文本自动换行，不溢出

---

## 关联文档 / Related Documents

- `frontend/src/pages/tool-io/KeeperProcess.vue` - 保管员处理页面
- `backend/routes/admin_user_routes.py` - 用户管理 API 参考
- `backend/database/schema/column_names.py` - 数据库字段常量
- `docs/RBAC_PERMISSION_MATRIX.md` - 权限矩阵
