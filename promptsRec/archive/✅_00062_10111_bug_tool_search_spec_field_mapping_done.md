Primary Executor: Codex
Task Type: Bug Fix
Stage: 111
Goal: Fix tool search API spec_model field mapping error
Execution: RUNPROMPT

---

# Context

前端工装搜索对话框 (ToolSearchDialog.vue) 中的"规格"列显示不出正确数据。

Debug ID: C-DIALOG-001 下的字段（编码、图号、规格、版本）与数据库字段不一致。

问题表现为：在创建订单页面打开工装搜索对话框，"规格"列的数据为空或不正确。

# Required References

- `backend/database/tool_io_queries.py` - search_tools 函数 (第84-91行)
- `frontend/src/components/tool-io/ToolSearchDialog.vue` - 工装搜索对话框
- `docs/DB_SCHEMA.md` - 数据库 schema 文档 (第214-218行)
- `frontend/src/utils/toolIO.js` - normalizeItem 函数 (第73-103行)

# Core Task

修复后端工装搜索 API 返回的规格型号字段映射错误。

# Required Work

1. 检查 `backend/database/tool_io_queries.py` 中的 `search_tools` 函数
2. 找到 SQL 查询中的字段映射部分（第84-91行附近）
3. 将 `[机型] as spec_model` 修改为 `[规格型号] as spec_model`
4. 确保其他字段映射正确：
   - `[序列号] as tool_code`
   - `[工装名称] as tool_name`
   - `[工装图号] as drawing_no`
   - `[当前版次] as current_version`
5. 验证修改后 API 返回正确的数据

# Constraints

- 不要修改前端代码
- 不要改变 API 响应结构
- 只修复字段映射问题
- 确保 SQL 语法正确

# Completion Criteria

1. 修改 `backend/database/tool_io_queries.py` 中的 search_tools 函数的 SQL 查询
2. 验证后端服务可以正常启动
3. 测试工装搜索 API 返回的 spec_model 字段包含正确数据
