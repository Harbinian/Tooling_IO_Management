# 00058 运输异常上报功能 - 前端实现

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 00058
Goal: 实现运输异常上报前端界面（Production Prep发现问题时可上报）
Dependencies: 00058_transport_exception_reporting_backend (后端必须先完成)
Execution: RUNPROMPT

---

## Context / 上下文

### 业务场景
生产准备工（Production Prep）在执行运输任务时发现异常（如工装损坏、数量不符、位置错误等），需要通过前端界面上报。保管员（Keeper）需要能查看异常列表并处理。

### 目标用户
- 生产准备工：执行运输任务，发现异常时上报
- 保管员：查看异常列表，处理/回复异常

### 核心痛点
当前 Production Prep 发现异常后没有系统化的上报渠道，异常没有持久化记录，Keeper 无法及时获得问题反馈。

### 业务目标
1. Production Prep 可通过前端界面上报运输异常
2. Keeper 可在前端查看管辖范围内的所有运输异常
3. Keeper 可对异常进行处理/回复
4. 界面符合深色主题 Element Plus 规范

---

## Required References / 必需参考

- frontend/src/pages/OrderDetail.vue - 订单详情页参考
- frontend/src/api/orderApi.js - 订单API调用
- docs/RBAC_PERMISSION_MATRIX.md - 权限矩阵
- .claude/rules/30_gemini_frontend.md - 前端设计协议

---

## Core Task / 核心任务

### 1. 订单详情页添加异常上报入口

在 OrderDetail.vue 中，当用户角色为 Production Prep 且订单状态为 `transport_in_progress` 或 `keeper_confirmed` 时，显示"上报异常"按钮。

**位置**: OrderDetail.vue 工具栏区域

**UI要求**:
- 按钮样式: `type="warning"` (Element Plus)
- 图标: `Warning` 或 `Exclamation`
- 文字: "上报异常"

### 2. 异常上报对话框

**组件**: ReportTransportIssueDialog.vue (新建)

**表单字段**:
| 字段 | 组件 | 说明 |
|------|------|------|
| 异常类型 | el-select | 工装损坏/数量不符/位置错误/其他 |
| 异常描述 | el-input textarea | 最少10字符，最多500字符 |
| 图片上传 | el-upload | 可选，最多3张 |

**对话框规范**:
- 宽度: 500px
- 确认按钮: "提交异常" (warning类型)
- 取消按钮: "取消"

### 3. 保管员异常查看面板

**位置**: OrderDetail.vue 或新建 KeeperIssueListPanel.vue

**列表展示**:
| 列 | 说明 |
|----|------|
| 异常类型 | 标签显示 |
| 异常描述 | 文本 |
| 上报人 | 姓名 |
| 上报时间 | 格式: YYYY-MM-DD HH:mm |
| 状态 | pending=待处理(红色), resolved=已处理(绿色) |
| 操作 | 查看详情/处理 |

**处理操作**: 点击"处理"打开处理对话框

### 4. 异常处理对话框

**组件**: ResolveIssueDialog.vue (新建)

**表单字段**:
| 字段 | 组件 | 说明 |
|------|------|------|
| 处理回复 | el-input textarea | 必填，最多500字符 |

**对话框规范**:
- 宽度: 400px
- 确认按钮: "确认处理"
- 取消按钮: "取消"

---

## Required Work / 必需工作

1. **API层**
   - 在 `frontend/src/api/orderApi.js` 添加:
     - `reportTransportIssue(orderNo, data)`
     - `getTransportIssues(orderNo)`
     - `resolveTransportIssue(orderNo, data)`

2. **组件开发**
   - 创建 `ReportTransportIssueDialog.vue`
   - 创建 `ResolveIssueDialog.vue`
   - 在 `OrderDetail.vue` 中集成异常查看面板

3. **权限控制**
   - Production Prep 角色: 显示"上报异常"按钮
   - Keeper 角色: 显示异常列表和处理功能
   - 其他角色: 不显示相关功能

4. **状态管理**
   - 使用 Pinia store 管理异常列表状态
   - 刷新机制: 打开对话框时自动刷新列表

5. **UI一致性**
   - 确认对话框使用 `ElMessageBox.confirm`
   - 使用 CSS 变量，禁止硬编码颜色
   - 符合深色主题 Element Plus 规范

---

## Constraints / 约束条件

1. **确认对话框**: 所有关键操作必须使用 `ElMessageBox.confirm`
2. **CSS规范**: 禁止 `bg-white`, `text-white` 等硬编码，必须使用 CSS 变量
3. **权限控制**: 基于当前用户角色动态显示功能
4. **主题兼容**: 支持明暗主题切换
5. **无占位符**: 所有代码必须完整可执行

---

## Completion Criteria / 完成标准

1. ✅ 创建 `ReportTransportIssueDialog.vue` 组件
2. ✅ 创建 `ResolveIssueDialog.vue` 组件
3. ✅ OrderDetail.vue 显示"上报异常"按钮（Production Prep可见）
4. ✅ Keeper 可查看订单的异常列表
5. ✅ Keeper 可处理异常
6. ✅ 所有 API 调用正确
7. ✅ 前端构建通过: `cd frontend && npm run build`
8. ✅ UI 符合深色主题规范
