# 工装搜索数据库集成 / Tool Search DB Integration

---

## 更新的后端文件 / Backend Files Updated

- `database.py`
- `backend/services/tool_io_service.py`
- `web_server.py`

## 更新的前端文件 / Frontend Files Updated

- `frontend/src/api/toolIO.js`
- `frontend/src/utils/toolIO.js`
- `frontend/src/components/tool-io/ToolSearchDialog.vue`
- `frontend/src/components/tool-io/ToolSelectionTable.vue`
- `frontend/src/pages/tool-io/OrderCreate.vue`

## 使用的实际源字段 / Actual Source Fields Used

此集成现在使用 `工装身份卡_主表` 中的实时字段: / This integration now uses live fields from `工装身份卡_主表`:

- `序列号` / Serial Number
- `工装名称` / Tool Name
- `工装图号` / Drawing Number
- `机型` / Model
- `当前版次` / Current Version
- `库位` / Storage Location
- `应用历史` / Application History
- `可用状态` / Available Status
- `工装有效状态` / Tool Valid Status
- `出入库状态` / IO Status
- `产权所有` / Owner
- `工作包` / Work Package
- `主体材质` / Main Material
- `制造商` / Manufacturer
- `定检有效截止` / Inspection Expiry Date
- `定检属性` / Inspection Category
- `定检周期` / Inspection Cycle

## 搜索策略 / Search Strategy

### 后端 / Backend

`database.search_tools()` 现在搜索真实源表字段而非假设字段。 / `database.search_tools()` now searches against the real source table fields instead of assumed fields.

- 关键词搜索覆盖: / Keyword search covers:
  - `序列号` / Serial Number
  - `工装名称` / Tool Name
  - `工装图号` / Drawing Number
  - `机型` / Model
  - `库位` / Storage Location
  - `当前版次` / Current Version
  - `应用历史` / Application History
  - `工作包` / Work Package
  - `主体材质` / Main Material
  - `制造商` / Manufacturer
- 位置过滤器使用: / Location filter uses:
  - `库位` / Storage Location
  - 回退 `应用历史` / fallback `应用历史`
- 状态过滤器使用: / Status filter uses:
  - `可用状态` / Available Status
  - `工装有效状态` / Tool Valid Status
  - `出入库状态` / IO Status

后端响应现在返回规范化的逻辑别名，例如: / The backend response now returns normalized logical aliases such as:

- `tool_code` / 工装编码
- `tool_name` / 工装名称
- `drawing_no` / 图号
- `spec_model` / 规格型号
- `current_version` / 当前版次
- `current_location_text` / 当前位置文本
- `available_status` / 可用状态
- `valid_status` / 有效状态
- `io_status` / 出入库状态
- `status_text` / 状态文本

### 前端 / Frontend

对话框使用真实后端 API: / The dialog uses the real backend API:

- 端点: `GET /api/tools/search` / endpoint: `GET /api/tools/search`
- 封装: `searchTools(params)` / wrapper: `searchTools(params)`

UI 字段映射到后端行为如下: / The UI fields map to backend behavior as follows:

- 工装编码、工装名称、图号和型号使用后端 `keyword` 搜索，然后进行客户端细化 / tool code, tool name, drawing number, and model use the backend `keyword` search, then apply client-side refinement
- 位置使用后端 `location` 过滤器加上客户端细化 / location uses the backend `location` filter plus client-side refinement
- 状态使用后端 `status` 过滤器加上客户端细化 / status uses the backend `status` filter plus client-side refinement

## 回退逻辑 / Fallback Logic

某些 UI 概念不是源表中的直接物理字段。 / Some UI concepts are not direct physical fields in the source table.

### 规格/型号 / Specification / Model

- `工装身份卡_主表` 中不存在真正的 `规格型号` 字段 / No real `规格型号` field exists in `工装身份卡_主表`
- `机型` 被用作实用的 `spec_model` 别名 / `机型` is used as the practical `spec_model` alias

### 状态 / Status

- 没有单一的标准状态列满足当前 UI 需求 / There is no single canonical status column for current UI needs
- `status_text` 派生如下: / `status_text` is derived with:
  - `出入库状态` / IO Status
  - 否则使用 `可用状态` / else `可用状态`
  - 否则使用 `工装有效状态` / else `工装有效状态`

### 位置 / Location

- `库位` 是主要的当前位置字段 / `库位` is the primary current-location field
- `应用历史` 仍可作为回退位置/历史信号搜索 / `应用历史` remains searchable as a fallback location/history signal

## 重复预防逻辑 / Duplicate Prevention Logic

- 父页面将 `selectedToolCodes` 传入 `ToolSearchDialog` / Parent page passes `selectedToolCodes` into `ToolSearchDialog`
- 订单中已选择的行在表格选择列中被禁用 / Rows already selected in the order are disabled in the table selection column
- `OrderCreate.vue` 使用 `toolCode` / `序列号` 执行第二次去重 / `OrderCreate.vue` performs a second deduplication pass using `toolCode` / `序列号`
- 重复选择被跳过并通过 `ElMessage.warning` 显示 / Duplicate selections are skipped and shown with `ElMessage.warning`

## 剩余限制 / Remaining Limitations

- 源表没有为搜索结果提供可靠的通用更新时间戳 / The source table does not provide a reliable general-purpose update timestamp for search results
- 后端路由在某些层中仍保留历史 `location_id` 命名以保持兼容性，但现在也接受文本 `location` 查询 / The backend route still keeps the historical `location_id` naming in some layers for compatibility, but it now accepts a textual `location` query too
- 当前由于现有仓库配置问题，阻止了对 `database.py` 的直接运行时导入验证: 模块初始化期望 `settings.db`，而 `config/settings.py` 仍暴露扁平配置属性 / Direct runtime import validation of `database.py` is currently blocked by an existing repository configuration issue: module initialization expects `settings.db`, while `config/settings.py` still exposes flat config attributes
- 前端构建验证通过，但在解决现有后端配置问题后应重复端到端 Flask 路由验证 / Frontend build verification passed, but end-to-end Flask route verification should be repeated after the existing backend config issue is addressed
