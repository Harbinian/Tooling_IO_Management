# 工装主数据字段映射 / Tool Master Field Mapping

---

## 审计依据 / Audit Basis

源表: `工装身份卡_主表` / Source table: `工装身份卡_主表`

实时 SQL Server 审计确认: / Live SQL Server audit confirmed:

- `序列号` 在所有 `1465` 行中都有值。/ `序列号` is populated for all `1465` rows.
- `序列号` 的不同值计数也是 `1465`。/ `序列号` distinct count is also `1465`.
- 对于当前项目，`序列号` 是正确的唯一标识符，应被视为工装实例键。/ For the current project, `序列号` is the correct unique identifier and should be treated as the tool instance key.

## 推荐的字段映射 / Recommended Field Mapping

| 实际数据库字段 / Actual DB Field | 逻辑别名 / Logical Alias | 推荐业务含义 / Recommended Business Meaning | 用于搜索 / Used In Search | 用于对话框显示 / Used In Dialog Display | 用于已选工装表 / Used In Selected Tool Table | 预留未来使用 / Reserved For Future |
|---|---|---|---|---|---|---|
| `序列号` | `tool_code` | 工装唯一键/实例代码 / Tool unique key / instance code | 是 / Yes | 是 / Yes | 是 / Yes | 否 / No |
| `工装名称` | `tool_name` | 工装名称 / Tool name | 是 / Yes | 是 / Yes | 是 / Yes | 否 / No |
| `工装图号` | `drawing_no` | 图号 / Drawing number | 是 / Yes | 是 / Yes | 是 / Yes | 否 / No |
| `机型` | `spec_model` | 当前 UI 最佳可用型号/规格候选 / Best available model/specification candidate for current UI | 是 / Yes | 是 / Yes | 是 / Yes | 否 / No |
| `当前版次` | `current_version` | 当前工装版本 / Current tool version | 是 / Yes | 是 / Yes | 是 / Yes | 是 / Yes |
| `库位` | `current_location_text` | 当前存储位置 / Current storage location | 是 / Yes | 是 / Yes | 是 / Yes | 否 / No |
| `可用状态` | `available_status` | 操作可用状态 / Operational availability status | 是 / Yes | 否 / No | 否 / No | 是 / Yes |
| `工装有效状态` | `valid_status` | 有效/无效状态 / Valid/invalid state | 是 / Yes | 否 / No | 否 / No | 是 / Yes |
| `出入库状态` | `io_status` | 来自源表的 IO 工作流状态 / IO workflow state from source table | 是 / Yes | 否 / No | 否 / No | 是 / Yes |
| `应用历史` | `application_history` | 使用/位置历史文本 / Usage/location history text | 是 / Yes | 否 / No | 否 / No | 是 / Yes |
| `定检有效截止` | `inspection_expiry_date` | 定检到期日期 / Inspection expiry date | 否 / No | 否 / No | 否 / No | 是 / Yes |
| `定检属性` | `inspection_category` | 定检类别 / Inspection category | 否 / No | 否 / No | 否 / No | 是 / Yes |
| `定检周期` | `inspection_cycle` | 定检周期 / Inspection cycle | 否 / No | 否 / No | 否 / No | 是 / Yes |
| `产权所有` | `owner_name` | 所有权 / Ownership | 否 / No | 否 / No | 否 / No | 是 / Yes |
| `工作包` | `work_package` | 工作包 / Work package | 是 / Yes | 否 / No | 否 / No | 是 / Yes |
| `主体材质` | `main_material` | 主要材质 / Main material | 是 / Yes | 否 / No | 否 / No | 是 / Yes |
| `制造商` | `manufacturer` | 制造商 / Manufacturer | 是 / Yes | 否 / No | 否 / No | 是 / Yes |

## 选择的主字段 / Chosen Primary Fields

### 主键 / 唯一标识符 / Primary Key / Unique Identifier

- 选择字段: `序列号` / Chosen field: `序列号`
- 原因: / Reason:
  - 所有审计的行都已填充 / all audited rows are populated
  - 不同值计数与总行数匹配 / distinct count matches total row count
  - 与当前业务规则一致，即 `序列号` 是工装 UUID 和工装出入库键 / aligns with current business rule that `序列号` is the tool UUID and the tool IO key

### 工装编码候选 / Tool Code Candidate

- 选择字段: `序列号` / Chosen field: `序列号`
- 原因: / Reason:
  - 当前项目已使用作为业务键 / already used by the current project as the business key
  - 唯一且稳定 / unique and stable

### 工装名称候选 / Tool Name Candidate

- 选择字段: `工装名称` / Chosen field: `工装名称`

### 图号候选 / Drawing Number Candidate

- 选择字段: `工装图号` / Chosen field: `工装图号`

### 规格/型号候选 / Specification / Model Candidate

- 选择字段: `机型` / Chosen field: `机型`
- 原因: / Reason:
  - 源表不包含真正的 `规格型号` 字段 / the source table does not contain a real `规格型号` field
  - `机型` 是当前 UI 显示和过滤最接近的实用字段 / `机型` is the closest practical field for current UI display and filtering
  - 这被记录为业务别名，而非物理 Schema 重命名 / this is documented as a business alias rather than a physical schema rename

### 位置候选 / Location Candidate

- 选择字段: `库位` / Chosen field: `库位`
- 回退/相关字段: `应用历史` / Fallback/related field: `应用历史`
- 原因: / Reason:
  - `库位` 是直接的当前位置字段 / `库位` is the direct current-location field
  - `应用历史` 包含有用的历史或更广泛的位置上下文，适合作为搜索辅助字段 / `应用历史` contains useful historical or broader location context and is suitable as a search assist field

### 状态候选 / Status Candidate

- 选择字段: / Chosen fields:
  - `出入库状态` / `出入库状态`
  - `可用状态` / `可用状态`
  - `工装有效状态` / `工装有效状态`
- 运行时显示规则: / Runtime display rule:
  - 使用 `出入库状态` / use `出入库状态`
  - 否则使用 `可用状态` / else `可用状态`
  - 否则使用 `工装有效状态` / else `工装有效状态`

### 部门/负责人候选 / Department / Owner Candidate

- 选择字段: `产权所有` / Chosen field: `产权所有`
- 说明: / Notes:
  - 对于本项目的直接需求，没有找到强部门负责人字段 / no strong department owner field was found for this project's immediate needs
  - `机型` 在实时数据中包含一些混合的业务值，不应被视为部门字段 / `机型` contains some mixed business values in the live data and should not be treated as a department field

### 更新时间候选 / Update Time Candidate

- 在 `工装身份卡_主表` 中未找到可靠的通用最后更新时间戳。/ No reliable general-purpose last-update timestamp was found in `工装身份卡_主表`.
- 候选日期字段如 `工艺信息完善日期`、`编制日期` 和 `校对日期` 是特定于工作流的，不应用作通用更新时间戳。/ Candidate date fields such as `工艺信息完善日期`, `编制日期`, and `校对日期` are workflow-specific and should not be used as a generic update timestamp.

## 搜索建议 / Search Recommendations

当前后端搜索应使用: / Current backend search should use:

- 关键词: / keyword:
  - `序列号`
  - `工装名称`
  - `工装图号`
  - `机型`
  - `库位`
  - `当前版次`
  - `应用历史`
  - `工作包`
  - `主体材质`
  - `制造商`
- 位置过滤器: / location filter:
  - `库位`
  - 回退 `应用历史` / fallback `应用历史`
- 状态过滤器: / status filter:
  - `可用状态`
  - `工装有效状态`
  - `出入库状态`

## 对话框显示建议 / Dialog Display Recommendations

工装搜索对话框推荐的列: / Recommended columns for the tool search dialog:

- `序列号`
- `工装名称`
- `工装图号`
- `机型`
- `当前版次`
- `库位`
- 合并状态文本 / merged status text

## 已选工装表建议 / Selected Tool Table Recommendations

推荐的已选工流行字段: / Recommended selected-tool row fields:

- `序列号`
- `工装名称`
- `工装图号`
- `机型`
- `当前版次`
- `库位`

## 未来预留字段 / Future Reserved Fields

保留供以后工作流扩展的有用字段: / Useful fields to keep available for later workflow extensions:

- `应用历史`
- `定检有效截止`
- `定检属性`
- `定检周期`
- `产权所有`
- `工作包`
- `主体材质`
- `制造商`
- `当前版次`
