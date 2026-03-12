Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 051
Goal: Dynamic form fields based on order type (outbound/inbound)
Execution: RUNPROMPT

---

# Context

工装出入库管理创建订单页面 (OrderCreate.vue) 的表单字段需要根据申请类型动态调整。

当前问题：
- 申请类型 (C-FIELD-001) 切换时，相关字段的显示逻辑不正确
- 出库时：用途字段是自由输入，应改为单选
- 入库时：用途字段和目标位置字段应隐藏
- 入库时：计划使用时间应改为计划还库时间
- 项目代号字段暂时多余，应隐藏

业务逻辑：
- 出库 (outbound)：用途(单选：零件生产/零件检验/工装试配/工装定检) + 目标位置 + 计划使用时间
- 入库 (inbound)：仅显示计划还库时间，隐藏其他两个字段

# Required References

- `frontend/src/pages/tool-io/OrderCreate.vue` - 创建订单页面
- `frontend/src/debug/debugIds.js` - Debug ID 注册表
- `docs/DB_SCHEMA.md` - 数据库 schema (工装出入库单_主表)

# Core Task

修改 OrderCreate.vue，实现申请类型切换时表单字段的动态显示逻辑。

# Required Work

1. 修改 `form` 数据结构，添加 `usagePurposeOptions` 用于单选项
2. 用途字段改为下拉单选 (Select/Radio)，选项：零件生产、零件检验、工装试配、工装定检
3. 使用 `v-if` 或计算属性根据 `form.orderType` 动态显示/隐藏字段：
   - 出库时：显示用途(单选)、目标位置、计划使用时间
   - 入库时：隐藏用途、隐藏目标位置、显示计划还库时间
4. 修改字段标签：入库时"计划使用时间"改为"计划还库时间"
5. 项目代号字段暂时使用 `v-if="false"` 隐藏
6. 验证表单提交时数据正确

# Constraints

- 不修改后端 API
- 不修改数据库结构
- 保持现有的 Debug ID (v-debug-id)
- 保持现有的表单验证逻辑

# Completion Criteria

1. OrderCreate.vue 中的表单字段可根据申请类型动态显示/隐藏
2. 出库时用途为单选，选项包含：零件生产、零件检验、工装试配、工装定检
3. 入库时隐藏用途和目标位置字段
4. 入库时计划使用时间字段标签变为"计划还库时间"
5. 项目代号字段暂时隐藏
6. 页面可正常加载和提交
