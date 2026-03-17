# 工装搜索对话框实现 / Tool Search Dialog Implementation

---

## 更新的文件 / Updated Files

- `frontend/src/components/tool-io/ToolSearchDialog.vue`
- `frontend/src/components/tool-io/ToolSelectionTable.vue`
- `frontend/src/api/toolIO.js`
- `frontend/src/pages/tool-io/OrderCreate.vue`
- `frontend/src/utils/toolIO.js`

## 使用的 API 方法 / API Method Used

- 前端 API 封装: `searchTools(params)` / Frontend API wrapper: `searchTools(params)`
- 后端端点: `GET /api/tools/search` / Backend endpoint: `GET /api/tools/search`

当前后端搜索 API 支持 `keyword`、`status`、`page_no` 和 `page_size`。/ The current backend search API supports `keyword`, `status`, `page_no`, and `page_size`.

对话框为工装编码、工装名称、规格/型号和位置显示单独字段，/ The dialog exposes separate fields for tool code, tool name, specification/model, and location,

然后使用现有的 `keyword` 搜索加上客户端过滤，以保持在当前 API 能力范围内。/ then uses the existing `keyword` search plus client-side filtering to stay within current API capability.

## 选中工装的返回结构 / Selected Tool Return Structure

对话框发出 `confirm` 时附带规范化的工装记录数组: / The dialog emits `confirm` with an array of normalized tool records:

```js
{
  toolId,           // 工装ID
  toolCode,         // 工装编码
  toolName,         // 工装名称
  drawingNo,        // 图号
  specModel,        // 规格型号
  currentLocationText,  // 当前位置文本
  itemStatus,       // 项目状态
  statusText        // 状态文本
}
```

`OrderCreate.vue` 将这些记录直接追加到已选工装表，并使用相同的结构 / `OrderCreate.vue` appends these records directly into the selected tool table and uses the same structure

构建订单创建 payload。/ to build the order creation payload.

## 重复预防逻辑 / Duplicate Prevention Logic

- `ToolSearchDialog.vue` 从父页面接收 `selectedToolCodes`。/ `ToolSearchDialog.vue` receives `selectedToolCodes` from the parent page.
- 订单中已存在的行在选择列中被禁用。/ Rows already present in the order are disabled in the selection column.
- `OrderCreate.vue` 仍使用 `toolCode` 作为唯一键执行第二次去重。/ `OrderCreate.vue` still performs a second deduplication pass using `toolCode` as the unique key.
- 重复选择被跳过并通过 `ElMessage.warning` 报告。/ Duplicate picks are skipped and reported with an `ElMessage.warning`.

## 限制和假设 / Limitations And Assumptions

- 后端搜索 API 目前不提供专用的工装编码、工装名称、/ The backend search API does not currently provide dedicated filters for tool code, tool name,
  规格/型号或位置过滤器。这些作为 UI 字段处理，在前端进行细化。/ specification/model, or location. These are handled as UI fields and refined on the frontend.
- 后端搜索结果目前不公开稳定的工装状态字段，因此对话框仅在 API 返回 / The backend search result does not expose a stable tool status field today, so the dialog shows
  `statusText` 时显示它；否则回退到 `-`。/ `statusText` only when the API returns one; otherwise it falls back to `-`.
- 在前端选择流程中，`toolCode` 被视为唯一工装标识符，这与当前业务规则一致 / `toolCode` is treated as the unique tool identifier in the frontend selection flow, which aligns
  即 `序列号` 是唯一的工装键。/ with the current business rule that `序列号` is the unique tool key.
