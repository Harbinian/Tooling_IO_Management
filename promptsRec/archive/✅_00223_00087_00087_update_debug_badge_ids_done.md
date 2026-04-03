# 00087 - 更新 DEBUG_IDS 以匹配新增前端元素

## Context / 上下文

管理员的 debug 徽章功能用于在开发/调试时显示元素 ID。目前 `frontend/src/debug/debugIds.js` 中定义的 `DEBUG_IDS` 与实际使用中的 `v-debug-id` 指令不匹配，导致部分元素无法正确显示 debug 徽章。

前端已新增/更新了多个组件和页面，但 DEBUG_IDS 常量未同步更新。

---

## Required References / 必需参考

- `frontend/src/debug/debugIds.js` - 当前 DEBUG_IDS 定义
- `frontend/src/directives/vDebugId.js` - debug 徽章指令实现
- `frontend/src/pages/tool-io/OrderCreate.vue` - 使用 `DEBUG_IDS.ORDER_CREATE.*`
- `frontend/src/pages/tool-io/OrderDetail.vue` - 使用 `DEBUG_IDS.ORDER_DETAIL.*`
- `frontend/src/pages/tool-io/KeeperProcess.vue` - 使用 `DEBUG_IDS.KEEPER.*`
- `.claude/rules/04_frontend.md` - 前端开发规范

---

## Core Task / 核心任务

更新 `frontend/src/debug/debugIds.js` 中的 `DEBUG_IDS` 对象，补全缺失的 ID 定义，确保所有 `v-debug-id` 指令都能找到对应的 DEBUG_ID。

### 缺失的 ID（按优先级排序）

#### 1. ORDER_CREATE 缺失
| ID Key | 用途 | 建议值 |
|--------|------|--------|
| `TOOL_LIST` | 工装列表卡片 | `C-CARD-001` (与 FORM 区分) |

#### 2. ORDER_DETAIL 缺失
| ID Key | 用途 | 建议值 |
|--------|------|--------|
| `RESET_TO_DRAFT_BTN` | 重置为草稿按钮 | `OD-BTN-011` |
| `DELETE_BTN` | 删除订单按钮 | `OD-BTN-012` |

#### 3. KEEPER 缺失/修复
| ID Key | 用途 | 建议值 |
|--------|------|--------|
| `APPROVE_BTN` | 批准/确认按钮 | `K-BTN-007` |
| `TRANSPORT_PREVIEW_BTN` | 运输预览按钮 | `K-BTN-008` |
| `DISPATCH_TRANSPORT_BTN` | 当前为字符串 `'keeper.dispatch_transport_btn'`，应改为标准格式 | `K-BTN-009` |

### ID 格式规范
- 格式: `{PAGE}-{TYPE}-{NUMBER}`
- PAGE: 2-3 字符页面缩写
- TYPE: `CARD`, `BTN`, `FIELD`, `TABLE`, `PANEL`, `SECTION`, `LIST`, `ACTION` 等
- NUMBER: 3 位序号，从 001 开始

### 验证清单
更新后，确保以下 ID 都已正确定义：
- [ ] `DEBUG_IDS.ORDER_CREATE.TOOL_LIST`
- [ ] `DEBUG_IDS.ORDER_DETAIL.RESET_TO_DRAFT_BTN`
- [ ] `DEBUG_IDS.ORDER_DETAIL.DELETE_BTN`
- [ ] `DEBUG_IDS.KEEPER.APPROVE_BTN`
- [ ] `DEBUG_IDS.KEEPER.TRANSPORT_PREVIEW_BTN`
- [ ] `DEBUG_IDS.KEEPER.DISPATCH_TRANSPORT_BTN` (格式修正)

---

## Required Work / 必需工作

1. **读取并分析** `frontend/src/debug/debugIds.js` 当前内容
2. **检查所有使用 v-debug-id 的 Vue 文件**，确认 ID 使用情况
3. **更新 debugIds.js**：
   - 在 `ORDER_CREATE` 部分添加 `TOOL_LIST: 'C-CARD-001'`
   - 在 `ORDER_DETAIL` 部分添加 `RESET_TO_DRAFT_BTN: 'OD-BTN-011'` 和 `DELETE_BTN: 'OD-BTN-012'`
   - 在 `KEEPER` 部分添加 `APPROVE_BTN: 'K-BTN-007'`
   - 在 `KEEPER` 部分添加 `TRANSPORT_PREVIEW_BTN: 'K-BTN-008'`
   - 在 `KEEPER` 部分修正 `DISPATCH_TRANSPORT_BTN: 'K-BTN-009'`
4. **验证**：确保没有其他遗漏的 DEBUG_IDS 引用

---

## Constraints / 约束条件

- **只修改** `frontend/src/debug/debugIds.js`
- 不修改任何 Vue 组件文件
- 不修改 vDebugId.js 指令
- 保持现有 ID 编号连续性（不重编已有 ID）
- 新增 ID 必须符合格式规范 `{PAGE}-{TYPE}-{NUMBER}`
- UTF-8 编码

---

## Completion Criteria / 完成标准

1. [ ] `debugIds.js` 中所有缺失的 ID 都已补全
2. [ ] ID 命名符合格式规范
3. [ ] 没有引入重复的 ID
4. [ ] 没有修改任何 Vue 组件文件
5. [ ] 文件语法正确（可被 ES Module 导入）
